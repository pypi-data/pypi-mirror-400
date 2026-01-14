"""Configuration management using pydantic-settings."""
from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


def _find_env_file() -> Optional[str]:
    """Find .env file in current working directory.

    Returns:
        Path to .env file if found, None otherwise
    """
    env_path = Path.cwd() / ".env"
    if env_path.exists():
        return str(env_path)
    return None


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=_find_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Notion Integration
    notion_api_key: str
    notion_database_id: str

    # Notion Status Values (must match your Status property options)
    notion_status_backlog: str = "Backlog"
    notion_status_todo: str = "Todo"
    notion_status_in_progress: str = "In Progress"
    notion_status_in_review: str = "In Review"
    notion_status_done: str = "Done"

    # Repository
    repo_path: str
    worktrees_dir: Optional[str] = None

    # Polling
    poll_interval: int = 5  # seconds

    # Task Settings
    max_concurrent_tasks: int = 5
    blocked_timeout: int = 3600  # 1 hour

    # Database
    db_path: str = "clotion.db"

    # Logging
    log_level: str = "INFO"

    @property
    def effective_worktrees_dir(self) -> Path:
        """Get the effective worktrees directory.

        Returns:
            Path to worktrees directory
        """
        if self.worktrees_dir:
            return Path(self.worktrees_dir)
        return Path(self.repo_path) / ".worktrees"


# Global settings instance (cached)
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the application settings (singleton).

    Returns:
        Settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings() -> None:
    """Reset cached settings (useful for testing)."""
    global _settings
    _settings = None
