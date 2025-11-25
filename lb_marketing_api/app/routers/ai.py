"""
AI generation endpoints.
Handles requests to external AI services using Azure OpenAI.
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
from openai import AzureOpenAI

from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["ai"])


class GenerateRequest(BaseModel):
    """Request model for AI generation endpoint."""
    text: str
    tone: str


def get_azure_openai_client() -> AzureOpenAI:
    """
    Create and return an Azure OpenAI client instance.
    
    Returns:
        AzureOpenAI client instance
        
    Raises:
        HTTPException: If API key is not configured
    """
    if not settings.AZURE_OPENAI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Azure OpenAI API key is not configured"
        )
    
    return AzureOpenAI(
        api_version=settings.AZURE_OPENAI_API_VERSION,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_API_KEY,
    )


@router.post("/generate")
def generate(payload: GenerateRequest) -> Dict[str, Any]:
    """
    Generate AI response based on input text using Azure OpenAI.
    
    Args:
        payload: Request body containing 'text' property
        
    Returns:
        Response from the AI model with the generated content
        
    Raises:
        HTTPException: If the AI API call fails
    """
    try:
        logger.info(f"Calling Azure OpenAI with text: {payload.text[:100]}...")
        
        # Create Azure OpenAI client
        client = get_azure_openai_client()
        
        # Call the chat completions API
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that generates social media posts for a business. You will take in text and a descriptive word for tone and generate a text post for social media.",
                },
                {
                    "role": "user",
                    "content": payload.text + " use the following tone: " + payload.tone,
                }, 
                
            ],
            max_completion_tokens=13107,
            temperature=1.0,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            model=settings.AZURE_OPENAI_DEPLOYMENT
        )
        
        # Extract the generated content
        generated_content = response.choices[0].message.content
        
        logger.info("Azure OpenAI API call successful")
        
        return {
            "content": generated_content,
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            } if response.usage else None
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (e.g., missing API key)
        raise
    except Exception as e:
        # Check if it's an OpenAI API error
        error_type = type(e).__name__
        if "OpenAI" in error_type or "API" in error_type or hasattr(e, "status_code"):
            logger.error(f"Azure OpenAI API error: {str(e)}")
            status_code = getattr(e, "status_code", 502)
            raise HTTPException(
                status_code=status_code if 400 <= status_code < 600 else 502,
                detail=f"Azure OpenAI API error: {str(e)}"
            )
        else:
            logger.error(f"Unexpected error in AI generation: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )

