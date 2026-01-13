from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "secblast"
    db_user: str = "postgres"
    db_password: str = ""

    # XBRL file paths
    xbrl_base_path: str = "/mnt/moto/rss_processed_filings/xbrl"
    feed_documents_path: str = "/mnt/moto/feed/documents"

    # API
    api_port: int = 3008
    api_host: str = "0.0.0.0"

    # Cache settings
    cache_ttl: int = 3600  # 1 hour
    cache_maxsize: int = 1000

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    class Config:
        env_prefix = ""
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
