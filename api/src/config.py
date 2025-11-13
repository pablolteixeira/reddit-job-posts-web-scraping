from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    POSTGRES_USER: str = "reddit_user"
    POSTGRES_PASSWORD: str = "reddit_password"
    POSTGRES_DB: str = "reddit_jobs"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def database_url(self) -> str:
        """Construct PostgreSQL database URL."""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
