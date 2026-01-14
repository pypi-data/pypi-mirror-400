"""Task manager for orchestrating the task lifecycle."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from clotion.claude.activity import ActivityLabel, get_activity_for_tool
from clotion.claude.runner import ClaudeRunnerPool, SessionResult
from clotion.git.github import GitHubClient
from clotion.git.worktree import WorktreeManager
from clotion.notion.client import NotionClient, NotionPage
from clotion.notion.poller import NotionPoller, StatusChange
from clotion.notion.properties import PropertyManager
from clotion.tasks.state import TaskContext, TaskState, TaskStateMachine
from clotion.tasks.store import TaskRecord, TaskStore

logger = logging.getLogger(__name__)


class TaskManager:
    """Orchestrates the full task lifecycle from Notion to PR."""

    def __init__(
        self,
        notion_client: NotionClient,
        worktrees: WorktreeManager,
        github: GitHubClient,
        store: TaskStore,
        status_todo: str = "Todo",
        status_in_progress: str = "In Progress",
        status_in_review: str = "In Review",
        status_done: str = "Done",
        max_concurrent: int = 5,
        blocked_timeout: int = 3600,
    ):
        """Initialize the task manager.

        Args:
            notion_client: Notion API client
            worktrees: Git worktree manager
            github: GitHub client
            store: Task persistence store
            status_todo: Notion status value for Todo
            status_in_progress: Notion status value for In Progress
            status_in_review: Notion status value for In Review
            status_done: Notion status value for Done
            max_concurrent: Maximum concurrent tasks
            blocked_timeout: Timeout for blocked tasks in seconds
        """
        self.notion = notion_client
        self.worktrees = worktrees
        self.github = github
        self.store = store

        self.status_todo = status_todo
        self.status_in_progress = status_in_progress
        self.status_in_review = status_in_review
        self.status_done = status_done

        self.max_concurrent = max_concurrent
        self.blocked_timeout = blocked_timeout

        self._property_manager = PropertyManager(notion_client)
        self._runner_pool = ClaudeRunnerPool(max_concurrent)
        self._poller: Optional[NotionPoller] = None
        self._active_tasks: dict[str, TaskContext] = {}
        self._timeout_task: Optional[asyncio.Task] = None

    async def start(self, poll_interval: int = 5) -> None:
        """Start the task manager.

        Args:
            poll_interval: Polling interval in seconds
        """
        logger.info("Starting task manager...")

        # Initialize database
        await self.store.init()

        # Ensure Notion properties exist
        await self._property_manager.ensure_properties_exist()

        # Recover any existing tasks
        await self._recover_tasks()

        # Start poller
        self._poller = NotionPoller(
            self.notion,
            interval=poll_interval,
            on_status_change=self._handle_status_change,
            on_new_comment=self._handle_new_comment,
        )

        # Initialize poller state to avoid triggering on existing pages
        await self._poller.initialize_state(trigger_todo=True)
        await self._poller.start()

        # Start timeout checker
        self._timeout_task = asyncio.create_task(self._check_timeouts())

        logger.info("Task manager started")

    async def stop(self) -> None:
        """Stop the task manager."""
        logger.info("Stopping task manager...")

        if self._poller:
            await self._poller.stop()

        if self._timeout_task:
            self._timeout_task.cancel()
            try:
                await self._timeout_task
            except asyncio.CancelledError:
                pass

        # Cancel any running tasks
        for page_id in list(self._active_tasks.keys()):
            await self._runner_pool.cancel_runner(page_id)

        logger.info("Task manager stopped")

    async def _handle_status_change(self, change: StatusChange) -> None:
        """Handle a status change from the poller.

        Args:
            change: Status change information
        """
        page = change.page
        old_status = change.old_status
        new_status = change.new_status

        logger.info(f"Handling status change: {page.title} ({old_status} -> {new_status})")

        # Task moved to Todo -> Start working
        if new_status == self.status_todo:
            await self._start_task(page)

        # Task moved to Done -> Merge PR and cleanup
        elif new_status == self.status_done:
            await self._handle_done(page)

    async def _handle_new_comment(self, page_id: str, comment_text: str) -> None:
        """Handle a new comment on a watched page.

        Args:
            page_id: Page ID
            comment_text: Comment text
        """
        task = await self.store.get(page_id)
        if not task or task.state != TaskState.BLOCKED:
            return

        logger.info(f"Received comment for blocked task {task.task_identifier}")

        # Unblock and resume
        await self._resume_task(page_id, comment_text)

    async def _start_task(self, page: NotionPage) -> None:
        """Start working on a task.

        Args:
            page: Notion page representing the task
        """
        # Check if already working on this task
        if page.id in self._active_tasks:
            logger.warning(f"Task {page.id} already active, skipping")
            return

        # Check concurrency limit
        if len(self._active_tasks) >= self.max_concurrent:
            logger.warning(f"Concurrency limit reached, cannot start {page.title}")
            await self.notion.add_comment(
                page.id,
                "⏳ Clotion is at capacity. This task will be picked up when a slot opens.",
            )
            return

        logger.info(f"Starting task: {page.title}")

        # Generate Clotion ID if not set
        clotion_id = page.clotion_id
        if not clotion_id:
            clotion_id = await self._property_manager.get_next_clotion_id()
            await self.notion.set_clotion_id(page.id, clotion_id)

        # Update status to In Progress
        await self.notion.set_status(page.id, self.status_in_progress)
        await self.notion.set_current_status(page.id, "🚀 Starting...")

        # Create worktree
        branch_name = self.worktrees.get_branch_name(clotion_id)
        worktree_path = await self.worktrees.create(clotion_id)

        # Update page with branch info
        await self.notion.set_branch(page.id, branch_name)

        # Create task context
        context = TaskContext(
            page_id=page.id,
            task_identifier=clotion_id,
            title=page.title,
            description=None,  # Could fetch from page content
            database_id=self.notion.database_id,
            branch_name=branch_name,
            worktree_path=str(worktree_path),
        )
        context.state_machine.start()
        self._active_tasks[page.id] = context

        # Save to store
        await self._save_task(context)

        # Post starting comment
        await self.notion.add_comment(
            page.id,
            f"🤖 **Clotion started working**\n\nTask ID: {clotion_id}\nBranch: `{branch_name}`",
        )

        # Start Claude runner
        asyncio.create_task(self._run_claude(page.id, context))

    async def _run_claude(self, page_id: str, context: TaskContext) -> None:
        """Run Claude on a task.

        Args:
            page_id: Notion page ID
            context: Task context
        """
        try:
            # Create callbacks
            async def on_tool_use(tool_name: str) -> None:
                activity = get_activity_for_tool(tool_name)
                if activity:
                    await self.notion.set_current_status(page_id, activity.display_text)

            def on_tool_use_sync(tool_name: str) -> None:
                asyncio.create_task(on_tool_use(tool_name))

            # Run Claude
            result = await self._runner_pool.start_runner(
                page_id=page_id,
                working_dir=Path(context.worktree_path),
                task_identifier=context.task_identifier,
                title=context.title,
                description=context.description,
                on_tool_use=on_tool_use_sync,
            )

            # Update session ID
            context.session_id = result.session_id
            await self.store.update_session_id(page_id, result.session_id)

            # Handle result
            if result.is_blocked:
                await self._handle_blocked(page_id, context, result.blocked_reason)
            elif result.error:
                await self._handle_error(page_id, context, result.error)
            else:
                await self._handle_complete(page_id, context)

        except Exception as e:
            logger.error(f"Error running Claude for {context.task_identifier}: {e}")
            await self._handle_error(page_id, context, str(e))

    async def _handle_blocked(
        self, page_id: str, context: TaskContext, reason: Optional[str]
    ) -> None:
        """Handle a blocked task.

        Args:
            page_id: Page ID
            context: Task context
            reason: Blocked reason
        """
        logger.info(f"Task {context.task_identifier} is blocked: {reason}")

        context.state_machine.block(reason or "Unknown reason")
        await self.store.update_state(page_id, TaskState.BLOCKED, reason)

        # Update Notion
        await self.notion.set_blocked(page_id, True)
        await self.notion.set_current_status(page_id, "❓ Waiting for input...")

        # Post comment asking for help
        await self.notion.add_comment(
            page_id,
            f"🤖 **Clotion needs help**\n\n{reason or 'I encountered an issue and need clarification.'}\n\n"
            "Please reply to this comment with guidance to continue.",
        )

        # Watch for comments
        if self._poller:
            self._poller.watch_comments(page_id)

    async def _resume_task(self, page_id: str, user_input: str) -> None:
        """Resume a blocked task.

        Args:
            page_id: Page ID
            user_input: User's input
        """
        context = self._active_tasks.get(page_id)
        if not context:
            logger.warning(f"No active context for page {page_id}")
            return

        logger.info(f"Resuming task {context.task_identifier}")

        # Update state
        context.state_machine.unblock()
        await self.store.update_state(page_id, TaskState.IN_PROGRESS)

        # Update Notion
        await self.notion.set_blocked(page_id, False)
        await self.notion.set_current_status(page_id, "🔄 Resuming...")

        # Stop watching comments
        if self._poller:
            self._poller.unwatch_comments(page_id)

        # Resume Claude
        result = await self._runner_pool.resume_runner(page_id, user_input)

        if result:
            if result.is_blocked:
                await self._handle_blocked(page_id, context, result.blocked_reason)
            elif result.error:
                await self._handle_error(page_id, context, result.error)
            else:
                await self._handle_complete(page_id, context)

    async def _handle_complete(self, page_id: str, context: TaskContext) -> None:
        """Handle task completion.

        Args:
            page_id: Page ID
            context: Task context
        """
        logger.info(f"Task {context.task_identifier} completed")

        context.state_machine.complete()

        await self.notion.set_current_status(page_id, "📤 Creating PR...")

        # Push and create PR
        try:
            worktree_path = Path(context.worktree_path)

            # Push branch
            await self.github.push_branch(worktree_path, context.branch_name)

            # Create PR
            pr_body = self.github.format_pr_body(context.task_identifier, context.title)
            pr_title = self.github.format_pr_title(context.task_identifier, context.title)

            pr = await self.github.create_pr(
                worktree_path,
                title=pr_title,
                body=pr_body,
            )

            # Update context
            context.pr_number = pr.number
            context.pr_url = pr.url
            context.state_machine.submit_for_review()

            # Update store
            await self.store.update_pr_info(page_id, pr.number, pr.url)
            await self.store.update_state(page_id, TaskState.IN_REVIEW)

            # Update Notion
            await self.notion.set_status(page_id, self.status_in_review)
            await self.notion.set_pr_url(page_id, pr.url)
            await self.notion.set_current_status(page_id, "✅ PR created")
            await self.notion.set_blocked(page_id, False)

            # Post completion comment
            await self.notion.add_comment(
                page_id,
                f"🤖 **Clotion completed the task**\n\n"
                f"Pull request: [{pr_title}]({pr.url})\n\n"
                f"Move this card to **Done** to merge the PR.",
            )

            # Clean up active task (but keep in store for Done handling)
            self._active_tasks.pop(page_id, None)

        except Exception as e:
            logger.error(f"Failed to create PR: {e}")
            await self._handle_error(page_id, context, f"Failed to create PR: {e}")

    async def _handle_done(self, page: NotionPage) -> None:
        """Handle task moved to Done - merge PR and cleanup.

        Args:
            page: Notion page
        """
        task = await self.store.get(page.id)
        if not task:
            logger.warning(f"No stored task for page {page.id}")
            return

        if task.state != TaskState.IN_REVIEW:
            logger.warning(f"Task {task.task_identifier} not in review state, skipping merge")
            return

        logger.info(f"Handling Done for {task.task_identifier}")

        await self.notion.set_current_status(page.id, "🔀 Merging PR...")

        try:
            # Clean up worktree FIRST to free the branch
            # (gh merge --delete-branch fails if worktree still uses the branch)
            await self.worktrees.remove(task.task_identifier, force=True)

            # Merge PR from main repo (not worktree)
            if task.pr_number:
                await self.github.merge_pr(self.worktrees.repo_path, task.pr_number)

            # Update state
            await self.store.update_state(page.id, TaskState.DONE)

            # Update Notion
            await self.notion.set_current_status(page.id, "✨ Merged!")
            await self.notion.set_blocked(page.id, False)

            # Post completion comment
            await self.notion.add_comment(
                page.id,
                f"🤖 **PR merged successfully**\n\nTask {task.task_identifier} is complete!",
            )

        except Exception as e:
            logger.error(f"Failed to merge PR: {e}")
            await self.notion.add_comment(
                page.id,
                f"🤖 **Failed to merge PR**\n\nError: {e}\n\nPlease merge manually.",
            )

    async def _handle_error(self, page_id: str, context: TaskContext, error: str) -> None:
        """Handle task error.

        Args:
            page_id: Page ID
            context: Task context
            error: Error message
        """
        logger.error(f"Task {context.task_identifier} failed: {error}")

        context.state_machine.fail(error)
        await self.store.update_state(page_id, TaskState.FAILED, error)

        # Update Notion
        await self.notion.set_current_status(page_id, "❌ Failed")
        await self.notion.set_blocked(page_id, False)

        # Post error comment
        await self.notion.add_comment(
            page_id,
            f"🤖 **Clotion encountered an error**\n\n```\n{error}\n```\n\n"
            "Please check the logs for more details.",
        )

        # Clean up
        self._active_tasks.pop(page_id, None)
        if self._poller:
            self._poller.unwatch_comments(page_id)

    async def _save_task(self, context: TaskContext) -> None:
        """Save task context to store.

        Args:
            context: Task context
        """
        record = TaskRecord(
            page_id=context.page_id,
            task_identifier=context.task_identifier,
            title=context.title,
            description=context.description,
            database_id=context.database_id,
            branch_name=context.branch_name or "",
            worktree_path=context.worktree_path or "",
            state=context.state,
            blocked_reason=context.state_machine.blocked_reason,
            blocked_at=context.state_machine.blocked_at,
            pr_number=context.pr_number,
            pr_url=context.pr_url,
            session_id=context.session_id,
            created_at=context.created_at,
            updated_at=datetime.now(),
        )
        await self.store.save(record)

    async def _recover_tasks(self) -> None:
        """Recover tasks from store on startup."""
        logger.info("Recovering tasks from store...")

        active_tasks = await self.store.get_active_tasks()

        for task in active_tasks:
            if task.state == TaskState.IN_PROGRESS:
                # Can't resume mid-session, mark as failed
                logger.warning(f"Marking interrupted task {task.task_identifier} as failed")
                await self.store.update_state(task.page_id, TaskState.FAILED, "Interrupted by restart")

            elif task.state == TaskState.BLOCKED:
                # Re-watch for comments
                if self._poller:
                    self._poller.watch_comments(task.page_id)
                logger.info(f"Watching blocked task {task.task_identifier} for comments")

        logger.info(f"Recovered {len(active_tasks)} tasks")

    async def _check_timeouts(self) -> None:
        """Check for blocked task timeouts."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute

                blocked_tasks = await self.store.get_blocked_tasks()

                for task in blocked_tasks:
                    if task.blocked_at:
                        duration = (datetime.now() - task.blocked_at).total_seconds()
                        if duration > self.blocked_timeout:
                            logger.warning(
                                f"Task {task.task_identifier} timed out after {duration}s"
                            )
                            await self.store.update_state(
                                task.page_id, TaskState.FAILED, "Blocked timeout exceeded"
                            )
                            await self.notion.add_comment(
                                task.page_id,
                                "🤖 **Task timed out**\n\n"
                                f"No response received after {self.blocked_timeout // 60} minutes.",
                            )
                            if self._poller:
                                self._poller.unwatch_comments(task.page_id)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error checking timeouts: {e}")
