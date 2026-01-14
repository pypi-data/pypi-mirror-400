"""SQLite persistence for task state."""
from __future__ import annotations


import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import aiosqlite

from clotion.tasks.state import TaskState

logger = logging.getLogger(__name__)


@dataclass
class TaskRecord:
    """Database record for a task."""

    page_id: str  # Notion page ID
    task_identifier: str  # e.g., "CLO-001"
    title: str
    description: Optional[str]
    database_id: Optional[str]
    branch_name: str
    worktree_path: str
    state: TaskState
    blocked_reason: Optional[str]
    blocked_at: Optional[datetime]
    pr_number: Optional[int]
    pr_url: Optional[str]
    session_id: Optional[str]
    created_at: datetime
    updated_at: datetime


class TaskStore:
    """SQLite-based persistence for task records."""

    def __init__(self, db_path: str = "clotion.db"):
        """Initialize the task store.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self._initialized = False

    async def init(self) -> None:
        """Initialize database schema."""
        if self._initialized:
            return

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    page_id TEXT PRIMARY KEY,
                    task_identifier TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    database_id TEXT,
                    branch_name TEXT NOT NULL,
                    worktree_path TEXT NOT NULL,
                    state TEXT NOT NULL,
                    blocked_reason TEXT,
                    blocked_at TEXT,
                    pr_number INTEGER,
                    pr_url TEXT,
                    session_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            # Create indexes for common queries
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_tasks_state
                ON tasks(state)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_tasks_identifier
                ON tasks(task_identifier)
            """)

            await db.commit()

        self._initialized = True
        logger.info(f"Initialized task store at {self.db_path}")

    async def save(self, task: TaskRecord) -> None:
        """Save or update a task record.

        Args:
            task: Task record to save
        """
        await self.init()

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT OR REPLACE INTO tasks (
                    page_id, task_identifier, title, description, database_id,
                    branch_name, worktree_path, state, blocked_reason, blocked_at,
                    pr_number, pr_url, session_id, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    task.page_id,
                    task.task_identifier,
                    task.title,
                    task.description,
                    task.database_id,
                    task.branch_name,
                    task.worktree_path,
                    task.state.value,
                    task.blocked_reason,
                    task.blocked_at.isoformat() if task.blocked_at else None,
                    task.pr_number,
                    task.pr_url,
                    task.session_id,
                    task.created_at.isoformat(),
                    datetime.now().isoformat(),
                ),
            )
            await db.commit()

        logger.debug(f"Saved task {task.task_identifier} in state {task.state.value}")

    async def get(self, page_id: str) -> Optional[TaskRecord]:
        """Get a task by page ID.

        Args:
            page_id: Notion page ID

        Returns:
            TaskRecord if found, None otherwise
        """
        await self.init()

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM tasks WHERE page_id = ?", (page_id,)
            )
            row = await cursor.fetchone()

            if row:
                return self._row_to_record(row)
            return None

    async def get_by_identifier(self, identifier: str) -> Optional[TaskRecord]:
        """Get a task by task identifier (e.g., "CLO-001").

        Args:
            identifier: Task identifier

        Returns:
            TaskRecord if found, None otherwise
        """
        await self.init()

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM tasks WHERE task_identifier = ?", (identifier,)
            )
            row = await cursor.fetchone()

            if row:
                return self._row_to_record(row)
            return None

    async def get_by_state(self, state: TaskState) -> list[TaskRecord]:
        """Get all tasks in a specific state.

        Args:
            state: Task state to filter by

        Returns:
            List of matching task records
        """
        await self.init()

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM tasks WHERE state = ? ORDER BY updated_at DESC",
                (state.value,),
            )
            rows = await cursor.fetchall()
            return [self._row_to_record(row) for row in rows]

    async def get_blocked_tasks(self) -> list[TaskRecord]:
        """Get all blocked tasks.

        Returns:
            List of blocked task records
        """
        return await self.get_by_state(TaskState.BLOCKED)

    async def get_active_tasks(self) -> list[TaskRecord]:
        """Get all active (non-terminal) tasks.

        Returns:
            List of active task records
        """
        await self.init()

        active_states = [
            TaskState.PENDING.value,
            TaskState.IN_PROGRESS.value,
            TaskState.BLOCKED.value,
            TaskState.COMPLETED.value,
            TaskState.IN_REVIEW.value,
        ]

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            placeholders = ",".join(["?"] * len(active_states))
            cursor = await db.execute(
                f"SELECT * FROM tasks WHERE state IN ({placeholders}) ORDER BY updated_at DESC",
                active_states,
            )
            rows = await cursor.fetchall()
            return [self._row_to_record(row) for row in rows]

    async def get_all(self, limit: int = 100) -> list[TaskRecord]:
        """Get all tasks.

        Args:
            limit: Maximum number of tasks to return

        Returns:
            List of task records
        """
        await self.init()

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM tasks ORDER BY updated_at DESC LIMIT ?", (limit,)
            )
            rows = await cursor.fetchall()
            return [self._row_to_record(row) for row in rows]

    async def delete(self, page_id: str) -> bool:
        """Delete a task record.

        Args:
            page_id: Notion page ID

        Returns:
            True if deleted, False if not found
        """
        await self.init()

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "DELETE FROM tasks WHERE page_id = ?", (page_id,)
            )
            await db.commit()
            return cursor.rowcount > 0

    async def update_state(
        self,
        page_id: str,
        state: TaskState,
        blocked_reason: Optional[str] = None,
    ) -> bool:
        """Update just the state of a task.

        Args:
            page_id: Notion page ID
            state: New state
            blocked_reason: Reason if blocked

        Returns:
            True if updated
        """
        await self.init()

        blocked_at = datetime.now().isoformat() if state == TaskState.BLOCKED else None

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                UPDATE tasks
                SET state = ?, blocked_reason = ?, blocked_at = ?, updated_at = ?
                WHERE page_id = ?
            """,
                (
                    state.value,
                    blocked_reason,
                    blocked_at,
                    datetime.now().isoformat(),
                    page_id,
                ),
            )
            await db.commit()
            return cursor.rowcount > 0

    async def update_pr_info(
        self, page_id: str, pr_number: int, pr_url: str
    ) -> bool:
        """Update PR information for a task.

        Args:
            page_id: Notion page ID
            pr_number: GitHub PR number
            pr_url: GitHub PR URL

        Returns:
            True if updated
        """
        await self.init()

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                UPDATE tasks
                SET pr_number = ?, pr_url = ?, updated_at = ?
                WHERE page_id = ?
            """,
                (pr_number, pr_url, datetime.now().isoformat(), page_id),
            )
            await db.commit()
            return cursor.rowcount > 0

    async def update_session_id(self, page_id: str, session_id: str) -> bool:
        """Update Claude session ID for a task.

        Args:
            page_id: Notion page ID
            session_id: Claude session ID

        Returns:
            True if updated
        """
        await self.init()

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                UPDATE tasks
                SET session_id = ?, updated_at = ?
                WHERE page_id = ?
            """,
                (session_id, datetime.now().isoformat(), page_id),
            )
            await db.commit()
            return cursor.rowcount > 0

    def _row_to_record(self, row: aiosqlite.Row) -> TaskRecord:
        """Convert a database row to a TaskRecord.

        Args:
            row: Database row

        Returns:
            TaskRecord instance
        """
        return TaskRecord(
            page_id=row["page_id"],
            task_identifier=row["task_identifier"],
            title=row["title"],
            description=row["description"],
            database_id=row["database_id"],
            branch_name=row["branch_name"],
            worktree_path=row["worktree_path"],
            state=TaskState(row["state"]),
            blocked_reason=row["blocked_reason"],
            blocked_at=(
                datetime.fromisoformat(row["blocked_at"])
                if row["blocked_at"]
                else None
            ),
            pr_number=row["pr_number"],
            pr_url=row["pr_url"],
            session_id=row["session_id"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
