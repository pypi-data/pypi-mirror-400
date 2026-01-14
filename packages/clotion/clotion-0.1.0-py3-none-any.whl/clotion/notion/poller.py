"""Notion database polling for change detection."""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Optional

from clotion.notion.client import NotionClient, NotionPage

logger = logging.getLogger(__name__)


@dataclass
class StatusChange:
    """Represents a status change for a page."""

    page: NotionPage
    old_status: Optional[str]
    new_status: str


class NotionPoller:
    """Polls Notion database for status changes."""

    def __init__(
        self,
        client: NotionClient,
        interval: int = 5,
        on_status_change: Optional[Callable[[StatusChange], None]] = None,
        on_new_comment: Optional[Callable[[str, str], None]] = None,
    ):
        """Initialize the poller.

        Args:
            client: Notion client
            interval: Polling interval in seconds
            on_status_change: Callback for status changes (receives StatusChange)
            on_new_comment: Callback for new comments (receives page_id, comment_text)
        """
        self.client = client
        self.interval = interval
        self.on_status_change = on_status_change
        self.on_new_comment = on_new_comment

        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._page_states: dict[str, str] = {}  # page_id -> status
        self._comment_timestamps: dict[str, datetime] = {}  # page_id -> last checked
        self._pages_to_watch_comments: set[str] = set()  # blocked pages

    async def start(self) -> None:
        """Start the polling loop."""
        if self._running:
            logger.warning("Poller already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._poll_loop())
        logger.info(f"Started Notion poller (interval: {self.interval}s)")

    async def stop(self) -> None:
        """Stop the polling loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("Stopped Notion poller")

    def watch_comments(self, page_id: str) -> None:
        """Start watching a page for new comments.

        Args:
            page_id: Page ID to watch
        """
        self._pages_to_watch_comments.add(page_id)
        self._comment_timestamps[page_id] = datetime.now()
        logger.debug(f"Now watching page {page_id} for comments")

    def unwatch_comments(self, page_id: str) -> None:
        """Stop watching a page for comments.

        Args:
            page_id: Page ID to stop watching
        """
        self._pages_to_watch_comments.discard(page_id)
        self._comment_timestamps.pop(page_id, None)
        logger.debug(f"Stopped watching page {page_id} for comments")

    async def _poll_loop(self) -> None:
        """Main polling loop."""
        while self._running:
            try:
                await self._poll_once()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in poll loop: {e}")

            await asyncio.sleep(self.interval)

    async def _poll_once(self) -> None:
        """Perform a single poll iteration."""
        # Query all non-backlog pages (active cards)
        pages = await self.client.query_pages(
            filter={
                "property": "Status",
                "status": {"does_not_equal": "Backlog"},
            }
        )

        # Check for status changes
        for page in pages:
            old_status = self._page_states.get(page.id)
            new_status = page.status

            # First time seeing this page (likely moved from Backlog)
            # Treat as a status change from Backlog to trigger task pickup
            if old_status is None:
                self._page_states[page.id] = new_status
                # Trigger callback as if moved from Backlog
                old_status = "Backlog"

            # Status changed (or newly appeared from Backlog)
            if old_status != new_status:
                self._page_states[page.id] = new_status

                change = StatusChange(
                    page=page,
                    old_status=old_status,
                    new_status=new_status,
                )

                logger.info(
                    f"Status change detected: {page.title} ({old_status} -> {new_status})"
                )

                if self.on_status_change:
                    try:
                        # Handle async or sync callbacks
                        result = self.on_status_change(change)
                        if asyncio.iscoroutine(result):
                            await result
                    except Exception as e:
                        logger.error(f"Error in status change callback: {e}")

        # Also check backlog pages that might have been moved TO backlog
        # (to clean up our state tracking)
        backlog_pages = await self.client.query_pages(
            filter={
                "property": "Status",
                "status": {"equals": "Backlog"},
            }
        )

        for page in backlog_pages:
            if page.id in self._page_states:
                old_status = self._page_states.pop(page.id)
                if old_status != "Backlog":
                    logger.info(f"Page {page.title} moved back to Backlog")

        # Check for new comments on watched pages
        await self._check_comments()

    async def _check_comments(self) -> None:
        """Check for new comments on watched pages."""
        if not self._pages_to_watch_comments or not self.on_new_comment:
            return

        for page_id in list(self._pages_to_watch_comments):
            since = self._comment_timestamps.get(page_id, datetime.now())

            try:
                comments = await self.client.get_new_human_comments(page_id, since)

                for comment in comments:
                    logger.info(f"New comment on page {page_id}: {comment.text[:50]}...")

                    try:
                        result = self.on_new_comment(page_id, comment.text)
                        if asyncio.iscoroutine(result):
                            await result
                    except Exception as e:
                        logger.error(f"Error in comment callback: {e}")

                # Update timestamp
                self._comment_timestamps[page_id] = datetime.now()

            except Exception as e:
                logger.warning(f"Failed to check comments for page {page_id}: {e}")

    async def initialize_state(self, trigger_todo: bool = False) -> None:
        """Initialize state by reading current page statuses.

        Call this before starting the poller to avoid triggering
        callbacks for existing pages.

        Args:
            trigger_todo: If True, trigger callbacks for pages already in ToDo status
        """
        logger.info("Initializing poller state...")

        pages = await self.client.query_pages(
            filter={
                "property": "Status",
                "status": {"does_not_equal": "Backlog"},
            }
        )

        todo_pages = []
        for page in pages:
            self._page_states[page.id] = page.status
            # Collect ToDo pages to trigger after initialization
            if trigger_todo and page.status == "ToDo":
                todo_pages.append(page)

        logger.info(f"Initialized state for {len(pages)} pages")

        # Trigger callbacks for existing ToDo pages
        if trigger_todo and self.on_status_change:
            for page in todo_pages:
                logger.info(f"Triggering callback for existing ToDo page: {page.title}")
                change = StatusChange(
                    page=page,
                    old_status="Backlog",
                    new_status="ToDo",
                )
                try:
                    result = self.on_status_change(change)
                    if asyncio.iscoroutine(result):
                        await result
                except Exception as e:
                    logger.error(f"Error in status change callback: {e}")
