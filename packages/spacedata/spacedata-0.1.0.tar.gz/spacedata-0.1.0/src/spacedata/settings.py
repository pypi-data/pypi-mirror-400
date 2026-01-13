import enum

from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggingLevelValues(str, enum.Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class SpaceDataSettings(BaseSettings):
    api_key: str = "DEMO_KEY"
    logging_level: LoggingLevelValues = LoggingLevelValues.INFO
    http_timeout: int = 30

    main_base_url: str = "https://api.nasa.gov"
    neo_base_url: str = "https://api.nasa.gov/neo/rest/v1"

    retry_attempts: int = 5
    retry_wait_multiplier: int = 2
    retry_wait_min: int = 10
    retry_wait_max: int = 20

    cache_controller: str | None = None
    cache_ttl: int = 60 * 60 * 24  # 1 day
    cache_weekday_number: int = 0
    duckdb_url: str = "./spacedata_cache_duckdb.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="SPACEDATA_",
    )


__all__ = ["SpaceDataSettings"]
