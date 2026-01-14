"""Clotion - Autonomous development automation with Claude Code and Notion."""
from __future__ import annotations

import asyncio
import logging
import signal
import sys
from pathlib import Path

from clotion.config import get_settings
from clotion.git.github import GitHubClient
from clotion.git.worktree import WorktreeManager
from clotion.notion.client import NotionClient
from clotion.tasks.manager import TaskManager
from clotion.tasks.store import TaskStore

logger = logging.getLogger(__name__)

def print_banner() -> None:
    """Print startup banner."""
    # Cyan color (to differentiate from Claudear's purple)
    CYAN = "\033[38;5;87m"
    RESET = "\033[0m"

    banner = f"""{CYAN}
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║   ██████╗██╗      ██████╗ ████████╗██╗ ██████╗ ███╗   ██╗          ║
║  ██╔════╝██║     ██╔═══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║          ║
║  ██║     ██║     ██║   ██║   ██║   ██║██║   ██║██╔██╗ ██║          ║
║  ██║     ██║     ██║   ██║   ██║   ██║██║   ██║██║╚██╗██║          ║
║  ╚██████╗███████╗╚██████╔╝   ██║   ██║╚██████╔╝██║ ╚████║          ║
║   ╚═════╝╚══════╝ ╚═════╝    ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝          ║
║                                                                    ║
║    Autonomous Development Automation with Claude Code & Notion     ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝{RESET}
"""
    print(banner)


def setup_logging(level: str) -> None:
    """Set up logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )

    # Reduce noise from httpx
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def validate_config() -> bool:
    """Validate the configuration.

    Returns:
        True if valid, False otherwise
    """
    try:
        settings = get_settings()
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        logger.error("Make sure .env file exists in the current directory")
        return False

    errors = []

    # Check required settings
    if not settings.notion_api_key:
        errors.append("NOTION_API_KEY is required")
    elif not (settings.notion_api_key.startswith("secret_") or settings.notion_api_key.startswith("ntn_")):
        errors.append("NOTION_API_KEY should start with 'secret_' or 'ntn_'")

    if not settings.notion_database_id:
        errors.append("NOTION_DATABASE_ID is required")

    if not settings.repo_path:
        errors.append("REPO_PATH is required")
    elif not Path(settings.repo_path).exists():
        errors.append(f"REPO_PATH does not exist: {settings.repo_path}")
    elif not (Path(settings.repo_path) / ".git").exists():
        errors.append(f"REPO_PATH is not a git repository: {settings.repo_path}")

    if errors:
        for error in errors:
            logger.error(f"Configuration error: {error}")
        return False

    return True


async def run() -> None:
    """Run the Clotion application."""
    print_banner()

    settings = get_settings()
    setup_logging(settings.log_level)

    logger.info("Starting Clotion...")

    if not validate_config():
        sys.exit(1)

    # Initialize components
    notion_client = NotionClient(
        api_key=settings.notion_api_key,
        database_id=settings.notion_database_id,
    )

    worktrees = WorktreeManager(
        repo_path=settings.repo_path,
        worktrees_dir=settings.effective_worktrees_dir,
    )

    github_client = GitHubClient()

    store = TaskStore(db_path=settings.db_path)

    # Create task manager
    task_manager = TaskManager(
        notion_client=notion_client,
        worktrees=worktrees,
        github=github_client,
        store=store,
        status_todo=settings.notion_status_todo,
        status_in_progress=settings.notion_status_in_progress,
        status_in_review=settings.notion_status_in_review,
        status_done=settings.notion_status_done,
        max_concurrent=settings.max_concurrent_tasks,
        blocked_timeout=settings.blocked_timeout,
    )

    # Set up signal handlers for graceful shutdown
    shutdown_event = asyncio.Event()

    def handle_signal(sig: signal.Signals) -> None:
        logger.info(f"Received {sig.name}, shutting down...")
        shutdown_event.set()

    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda s=sig: handle_signal(s))

    try:
        # Start task manager
        await task_manager.start(poll_interval=settings.poll_interval)

        print(f"\n📋 Database: {settings.notion_database_id[:8]}...")
        print(f"📂 Repository: {settings.repo_path}")
        print(f"🔄 Poll interval: {settings.poll_interval}s")
        print(f"⚡ Max concurrent tasks: {settings.max_concurrent_tasks}")
        print(f"⏱️  Blocked timeout: {settings.blocked_timeout}s")
        print()
        logger.info("Clotion is running! Move a Notion card to 'Todo' to start.")
        logger.info("Press Ctrl+C to stop")

        # Wait for shutdown signal
        await shutdown_event.wait()

    finally:
        # Graceful shutdown
        await task_manager.stop()
        await notion_client.close()
        logger.info("Clotion stopped")


def main() -> None:
    """Entry point for the clotion command."""
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
