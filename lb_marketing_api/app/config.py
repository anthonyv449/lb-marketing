from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, field_validator
from typing import List, Union

class Settings(BaseSettings):
    APP_NAME: str = "LB Marketing API"
    APP_ENV: str = "development"

    # Database configuration
    # Azure Database for PostgreSQL uses these exact variable names
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "postgres"
    DATABASE_NAME: str = "lb-marketing"

    # CORS configuration
    # In Azure, set CORS_ORIGINS as comma-separated URLs (e.g., "https://app1.com,https://app2.com")
    # Can also be set as a list in .env file
    CORS_ORIGINS: Union[str, List[AnyHttpUrl]] = []
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from string (comma-separated) or list."""
        if isinstance(v, str):
            # Handle comma-separated string (common in Azure App Settings)
            if not v.strip():
                return []
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # JWT Secret Key for authentication
    # MUST be set in production via Azure App Settings or Key Vault
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # Twitter/X OAuth 2.0 credentials
    TWITTER_CLIENT_ID: str = ""
    TWITTER_CLIENT_SECRET: str = ""
    # Redirect URI should point to the backend callback endpoint
    # In production, this should be your actual domain
    TWITTER_REDIRECT_URI: str = "http://localhost:8000/oauth/x/callback"
    TWITTER_BEARER_TOKEN: str = ""

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    class Config:
        env_file = ".env"

settings = Settings()
