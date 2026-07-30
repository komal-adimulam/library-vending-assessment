from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings."""

    # Database configuration
    database_url: str = "postgresql+psycopg2://postgres:6669@localhost:5432/librarydb"
    database_pool_size: int = 5
    database_max_overflow: int = 10
    database_pool_timeout: int = 30
    database_pool_recycle: int = 1800

    # Loan processing configuration
    catalog_sync_window: float = 0.0
    enable_graceful_degradation: bool = False

    # Circulation desk configuration
    circulation_lock_timeout: int = 0

    # Authentication configuration.  Set JWT_SECRET to a long, random value
    # in every deployed environment; the development default is deliberately
    # unsuitable for shared deployments.
    jwt_secret: str = "development-only-change-this-secret-before-deploying"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
