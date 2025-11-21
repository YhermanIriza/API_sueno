from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Backend API"
    environment: str = "development"
    database_url: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()
