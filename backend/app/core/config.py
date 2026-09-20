from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "Multilingual AI Voice Platform"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    OPENAI_API_KEY: Optional[str] = None
    USE_MOCK_AI: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
