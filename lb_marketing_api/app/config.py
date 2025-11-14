from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "LB Marketing API"
    APP_ENV: str = "development"

    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "postgres"
    DATABASE_NAME: str = "lb-marketing"

    CORS_ORIGINS: List[AnyHttpUrl] = []

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
