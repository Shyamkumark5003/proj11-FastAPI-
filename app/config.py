import sys
from functools import lru_cache
from typing import Literal

from pydantic import SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # default irukku -> optional
    app_env: Literal["development", "test", "production"] = "development"
    log_level: str = "INFO"

    # default illa -> REQUIRED (missing na startup stop)
    database_url: str
    llm_api_key: SecretStr

    @property
    def docs_enabled(self) -> bool:
        # docs development la mattum on
        return self.app_env == "development"


@lru_cache
def get_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as e:
        print("\nCONFIG ERROR: service start aaga mudiyala.\n")
        for err in e.errors():
            name = ".".join(str(p) for p in err["loc"]).upper()
            print(f"  - {name}: {err['msg']}")
        print("\nFix: .env.example ah .env nu copy panni, values fill pannu.\n")
        sys.exit(1)