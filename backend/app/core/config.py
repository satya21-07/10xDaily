from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "10xDaily"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = "REPLACE_THIS_WITH_A_SECURE_SECRET_KEY"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    GEMINI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    GOOGLE_CLIENT_ID: Optional[str] = None

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
