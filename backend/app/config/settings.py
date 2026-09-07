from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Mercury Hive Control Plane"
    POSTGRES_USER: str = "mercury"
    POSTGRES_PASSWORD: str = "hivepassword"
    POSTGRES_DB: str = "mercury_hive"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"

settings = Settings()
