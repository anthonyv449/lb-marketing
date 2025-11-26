"""
Instagram Graph API client for Business/Creator accounts.
Handles authenticated requests to the Facebook Graph API for Instagram operations.
"""

import requests
import time
import logging
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass

from ..config import settings

logger = logging.getLogger(__name__)


@dataclass
class InstagramGraphError:
    """Clean error object for Instagram Graph API errors"""
    message: str
    code: Optional[int] = None
    error_subcode: Optional[int] = None
    error_type: Optional[str] = None
    http_status: Optional[int] = None


class InstagramGraphClient:
    """
    Client for making authenticated requests to the Instagram Graph API.
    
    The Instagram Graph API is accessed through the Facebook Graph API at:
    https://graph.facebook.com/v{version}/
    
    This client handles:
    - Authenticated GET and POST requests
    - Rate limiting with exponential backoff
    - Error handling and logging
    - Clean error object returns
    """
    
    def __init__(
        self,
        ig_user_id: str,
        access_token: str,
        api_version: Optional[str] = None
    ):
        """
        Initialize the Instagram Graph API client.
        
        Args:
            ig_user_id: The Instagram Business/Creator account ID
            access_token: Long-lived Facebook/Instagram access token
            api_version: Graph API version (e.g., 'v21.0'). Defaults to IG_GRAPH_API_VERSION from config
        """
        self.ig_user_id = ig_user_id
        self.access_token = access_token
        self.api_version = api_version or settings.IG_GRAPH_API_VERSION or "v21.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
        
        # Rate limiting configuration
        self.max_retries = 3
        self.initial_backoff = 1  # seconds
        self.max_backoff = 60  # seconds
        
    def _handle_rate_limit(self, response: requests.Response) -> bool:
        """
        Check if response indicates rate limiting and handle it.
        
        Args:
            response: The HTTP response object
            
        Returns:
            True if rate limited, False otherwise
        """
        if response.status_code == 429:
            # Rate limit error
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                wait_time = int(retry_after)
            else:
                # Try to extract from error response
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_info = error_data["error"]
                        # Facebook Graph API sometimes includes retry info
                        if "error_subcode" in error_info and error_info["error_subcode"] == 2446079:
                            wait_time = 60  # Default to 60 seconds for rate limits
                        else:
                            wait_time = 60
                    else:
                        wait_time = 60
                except Exception:
                    wait_time = 60
            
            logger.warning(
                f"Rate limit hit for Instagram Graph API. Waiting {wait_time} seconds before retry."
            )
            time.sleep(wait_time)
            return True
        
        return False
    
    def _parse_error_response(self, response: requests.Response) -> InstagramGraphError:
        """
        Parse error response from Instagram Graph API into a clean error object.
        
        Args:
            response: The HTTP response object
            
        Returns:
            InstagramGraphError object with parsed error information
        """
        http_status = response.status_code
        error_message = f"Instagram Graph API request failed with status {http_status}"
        error_code = None
        error_subcode = None
        error_type = None
        
        try:
            error_data = response.json()
            if "error" in error_data:
                error_info = error_data["error"]
                error_message = error_info.get("message", error_message)
                error_code = error_info.get("code")
                error_subcode = error_info.get("error_subcode")
                error_type = error_info.get("type")
            elif "error_description" in error_data:
                error_message = error_data["error_description"]
        except Exception as e:
            logger.debug(f"Could not parse error response JSON: {e}")
            # Try to get text response
            try:
                error_text = response.text[:500]  # Limit length
                if error_text:
                    error_message = f"{error_message}: {error_text}"
            except Exception:
                pass
        
        return InstagramGraphError(
            message=error_message,
            code=error_code,
            error_subcode=error_subcode,
            error_type=error_type,
            http_status=http_status
        )
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ) -> Tuple[Optional[Dict[str, Any]], Optional[InstagramGraphError]]:
        """
        Make an authenticated request to the Instagram Graph API with retry logic.
        
        Args:
            method: HTTP method ('GET' or 'POST')
            endpoint: API endpoint (e.g., '{ig_user_id}/media')
            params: Query parameters for GET requests
            json_data: JSON body for POST requests
            retry_count: Current retry attempt number
            
        Returns:
            Tuple of (response_data, error)
            - response_data: Parsed JSON response if successful, None otherwise
            - error: InstagramGraphError if request failed, None otherwise
        """
        # Build URL
        url = f"{self.base_url}/{endpoint}"
        
        # Add access token to params
        if params is None:
            params = {}
        params["access_token"] = self.access_token
        
        # Prepare request
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, headers=headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, params=params, json=json_data, headers=headers, timeout=30)
            else:
                error = InstagramGraphError(
                    message=f"Unsupported HTTP method: {method}",
                    http_status=400
                )
                return None, error
        except requests.exceptions.Timeout as e:
            error = InstagramGraphError(
                message=f"Request timeout: {str(e)}",
                http_status=408
            )
            logger.error(f"Instagram Graph API request timeout: {endpoint}")
            return None, error
        except requests.exceptions.RequestException as e:
            error = InstagramGraphError(
                message=f"Request failed: {str(e)}",
                http_status=0
            )
            logger.error(f"Instagram Graph API request exception: {endpoint}, error: {str(e)}")
            return None, error
        
        # Handle rate limiting with retry
        if self._handle_rate_limit(response):
            if retry_count < self.max_retries:
                # Exponential backoff
                backoff_time = min(
                    self.initial_backoff * (2 ** retry_count),
                    self.max_backoff
                )
                logger.info(
                    f"Retrying Instagram Graph API request after {backoff_time}s "
                    f"(attempt {retry_count + 1}/{self.max_retries})"
                )
                time.sleep(backoff_time)
                return self._make_request(method, endpoint, params, json_data, retry_count + 1)
            else:
                error = InstagramGraphError(
                    message="Rate limit exceeded. Maximum retries reached.",
                    http_status=429
                )
                logger.error(f"Instagram Graph API rate limit exceeded after {self.max_retries} retries")
                return None, error
        
        # Check for successful response
        if response.status_code >= 200 and response.status_code < 300:
            try:
                data = response.json()
                logger.debug(f"Instagram Graph API {method} {endpoint} successful")
                return data, None
            except Exception as e:
                error = InstagramGraphError(
                    message=f"Failed to parse response JSON: {str(e)}",
                    http_status=response.status_code
                )
                logger.error(f"Failed to parse Instagram Graph API response: {e}")
                return None, error
        else:
            # Handle error response
            error = self._parse_error_response(response)
            logger.error(
                f"Instagram Graph API {method} {endpoint} failed: "
                f"HTTP {error.http_status}, {error.message}"
            )
            
            # Retry on 5xx errors (server errors)
            if response.status_code >= 500 and retry_count < self.max_retries:
                backoff_time = min(
                    self.initial_backoff * (2 ** retry_count),
                    self.max_backoff
                )
                logger.info(
                    f"Retrying Instagram Graph API request after server error "
                    f"(attempt {retry_count + 1}/{self.max_retries})"
                )
                time.sleep(backoff_time)
                return self._make_request(method, endpoint, params, json_data, retry_count + 1)
            
            return None, error
    
    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Tuple[Optional[Dict[str, Any]], Optional[InstagramGraphError]]:
        """
        Make an authenticated GET request to the Instagram Graph API.
        
        Args:
            endpoint: API endpoint (e.g., '{ig_user_id}/media' or '{ig_user_id}')
            params: Optional query parameters
            
        Returns:
            Tuple of (response_data, error)
            - response_data: Parsed JSON response if successful, None otherwise
            - error: InstagramGraphError if request failed, None otherwise
            
        Example:
            >>> client = InstagramGraphClient(ig_user_id="123", access_token="token")
            >>> data, error = client.get(f"{ig_user_id}/media")
            >>> if error:
            ...     print(f"Error: {error.message}")
            >>> else:
            ...     print(f"Success: {data}")
        """
        return self._make_request("GET", endpoint, params=params)
    
    def post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Tuple[Optional[Dict[str, Any]], Optional[InstagramGraphError]]:
        """
        Make an authenticated POST request to the Instagram Graph API.
        
        Args:
            endpoint: API endpoint (e.g., '{ig_user_id}/media')
            json_data: JSON body data
            params: Optional query parameters
            
        Returns:
            Tuple of (response_data, error)
            - response_data: Parsed JSON response if successful, None otherwise
            - error: InstagramGraphError if request failed, None otherwise
            
        Example:
            >>> client = InstagramGraphClient(ig_user_id="123", access_token="token")
            >>> data, error = client.post(
            ...     f"{ig_user_id}/media",
            ...     json_data={"image_url": "https://example.com/image.jpg", "caption": "Hello"}
            ... )
            >>> if error:
            ...     print(f"Error: {error.message}")
            >>> else:
            ...     print(f"Success: {data}")
        """
        return self._make_request("POST", endpoint, params=params, json_data=json_data)

