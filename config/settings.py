"""Centralised, typed access to environment configuration.

All values come from environment variables (loaded from `.env` when present),
so the suite never contains hardcoded URLs or credentials.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable '{name}'. "
            "Copy .env.example to .env and fill it in."
        )
    return value


@dataclass(frozen=True)
class Settings:
    web_url: str
    api_base_url: str
    app_email: str
    app_password: str
    app_alias: str

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            web_url=_require("WEB_URL").rstrip("/"),
            api_base_url=_require("API_BASE_URL").rstrip("/"),
            app_email=_require("APP_EMAIL"),
            app_password=_require("APP_PASSWORD"),
            app_alias=os.getenv("APP_ALIAS", ""),
        )
