from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str
    
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    AI_HF_API_KEY: Optional[str] = None  # Hugging Face API key
    AI_OPENAI_API_KEY: Optional[str] = None  # OpenAI API key
    
    # Redis Configuration (optional)
    REDIS_URL: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = ""

settings = Settings()
