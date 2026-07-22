from collections.abc import Sequence
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "developer-portfolio-api"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    log_dir: Path = Field(default=Path("logs"))
    data_dir: Path = Field(default=Path("data"))
    cors_origins: str = "*"
    database_url: str = "postgresql://zephy_db:1234@localhost:5441/zephy_db"
    database_connect_timeout_seconds: int = 5

    owner_email: str = "owner@example.com"

    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from: str = "portfolio@example.com"
    smtp_use_tls: bool = False
    smtp_timeout_seconds: int = 10

    openai_api_key: str = ""
    openai_model: str = "llama-3.1-8b-instant"
    openai_base_url: str = "https://api.groq.com/openai/v1"
    ai_timeout_seconds: int = 12

    rate_limit_requests: int = 5
    rate_limit_window_seconds: int = 60
    rate_limit_hash_secret: str = "change-me"

    def cors_allow_list(self) -> Sequence[str]:
        value = self.cors_origins.strip()
        if value == "*":
            return ["*"]
        return [item.strip() for item in value.split(",") if item.strip()]

    def ensure_directories(self) -> None:
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings
