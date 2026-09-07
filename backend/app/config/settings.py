from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Mercury Hive Control Plane"

    @property
    def DATABASE_URL(self) -> str:
        # Use SQLite for local development
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'mercury_hive.db')
        return f"sqlite:///{db_path}"

    class Config:
        env_file = ".env"

settings = Settings()
