from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings."""

    # Database configuration
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/librarydb"

    # Loan processing configuration
    enable_strict_idempotency_check: bool = False
    catalog_sync_window: float = 0.0
    enable_graceful_degradation: bool = False

    # Circulation desk configuration
    circulation_lock_timeout: int = 0

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
