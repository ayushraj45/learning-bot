"""Load and validate settings from .env. Secrets are never printed."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = ROOT / "data" / "learning.db"

# Config field -> environment variable name
ENV_NAMES = {
    "telegram_bot_token": "TELEGRAM_BOT_TOKEN",
    "owner_chat_id": "TELEGRAM_OWNER_CHAT_ID",
    "openai_api_key": "OPENAI_API_KEY",
    "openai_model": "OPENAI_MODEL",
}


class ConfigError(Exception):
    """A required setting is missing or invalid."""


@dataclass(frozen=True)
class Config:
    telegram_bot_token: str
    owner_chat_id: int | None
    openai_api_key: str
    openai_model: str
    daily_question_limit: int
    db_path: Path


def load_config(need: tuple[str, ...] = ()) -> Config:
    """Read .env and return a Config.

    `need` lists the fields this entrypoint cannot run without (for example
    ("telegram_bot_token",) for --whoami). Missing ones raise ConfigError
    naming the environment variables, never their values.
    """
    load_dotenv(ROOT / ".env")

    values = {field: os.getenv(env, "").strip() for field, env in ENV_NAMES.items()}

    missing = [ENV_NAMES[f] for f in need if not values[f]]
    if missing:
        raise ConfigError("Missing in .env: " + ", ".join(missing))

    owner_raw = values["owner_chat_id"]
    try:
        owner_chat_id = int(owner_raw) if owner_raw else None
    except ValueError:
        raise ConfigError("TELEGRAM_OWNER_CHAT_ID must be a number") from None

    limit_raw = os.getenv("DAILY_QUESTION_LIMIT", "60").strip() or "60"
    try:
        daily_limit = int(limit_raw)
    except ValueError:
        raise ConfigError("DAILY_QUESTION_LIMIT must be a number") from None

    return Config(
        telegram_bot_token=values["telegram_bot_token"],
        owner_chat_id=owner_chat_id,
        openai_api_key=values["openai_api_key"],
        openai_model=values["openai_model"],
        daily_question_limit=daily_limit,
        db_path=DEFAULT_DB_PATH,
    )
