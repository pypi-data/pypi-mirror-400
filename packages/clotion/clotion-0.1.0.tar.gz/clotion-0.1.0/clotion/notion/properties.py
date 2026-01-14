"""Notion database property management."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from clotion.notion.client import NotionClient, NotionAPIError

logger = logging.getLogger(__name__)


@dataclass
class PropertyDefinition:
    """Definition of a Notion property to create."""

    name: str
    type: str
    config: Optional[dict] = None


# Properties that Clotion needs to manage tasks
CLOTION_PROPERTIES: list[PropertyDefinition] = [
    # Status property - Select type with predefined options
    PropertyDefinition(
        name="Status",
        type="select",
        config={
            "options": [
                {"name": "Backlog", "color": "gray"},
                {"name": "Todo", "color": "yellow"},
                {"name": "In Progress", "color": "blue"},
                {"name": "In Review", "color": "purple"},
                {"name": "Done", "color": "green"},
            ]
        },
    ),
    # Blocked checkbox - for indicating when Claude needs help
    PropertyDefinition(name="Blocked", type="checkbox"),
    # Current Status - real-time activity text
    PropertyDefinition(name="Current Status", type="rich_text"),
    # Clotion ID - unique task identifier
    PropertyDefinition(name="Clotion ID", type="rich_text"),
    # Branch - git branch name
    PropertyDefinition(name="Branch", type="rich_text"),
    # PR URL - link to GitHub PR
    PropertyDefinition(name="PR URL", type="url"),
]


class PropertyManager:
    """Manages Notion database properties for Clotion."""

    def __init__(self, client: NotionClient):
        """Initialize the property manager.

        Args:
            client: Notion client
        """
        self.client = client
        self._initialized = False

    async def ensure_properties_exist(self) -> None:
        """Ensure all required Clotion properties exist in the database.

        Creates missing properties automatically.
        """
        if self._initialized:
            return

        logger.info("Checking Notion database properties...")

        # Get current database schema
        database = await self.client.get_database()
        existing_props = database.get("properties", {})

        # Check which properties need to be created
        properties_to_create = {}
        for prop_def in CLOTION_PROPERTIES:
            if prop_def.name not in existing_props:
                logger.info(f"Property '{prop_def.name}' not found, will create it")
                properties_to_create[prop_def.name] = self._build_property_schema(prop_def)
            else:
                existing_type = existing_props[prop_def.name].get("type")
                if existing_type != prop_def.type:
                    logger.warning(
                        f"Property '{prop_def.name}' exists but has type '{existing_type}' "
                        f"instead of '{prop_def.type}'. Skipping creation."
                    )

        # Create missing properties
        if properties_to_create:
            logger.info(f"Creating {len(properties_to_create)} properties...")
            await self._update_database_properties(properties_to_create)
            logger.info("Properties created successfully")
        else:
            logger.info("All required properties already exist")

        self._initialized = True

    def _build_property_schema(self, prop_def: PropertyDefinition) -> dict:
        """Build the schema for a property.

        Args:
            prop_def: Property definition

        Returns:
            Property schema for Notion API
        """
        schema: dict = {prop_def.type: prop_def.config or {}}
        return schema

    async def _update_database_properties(self, properties: dict) -> None:
        """Update database properties.

        Args:
            properties: Properties to add/update

        Raises:
            NotionAPIError: If update fails
        """
        await self.client._request(
            "PATCH",
            f"/databases/{self.client.database_id}",
            json={"properties": properties},
        )

    async def get_next_clotion_id(self) -> str:
        """Generate the next Clotion ID.

        Queries existing pages to find the highest ID and increments it.

        Returns:
            Next Clotion ID (e.g., "CLO-001", "CLO-002")
        """
        # Query pages to find existing Clotion IDs
        pages = await self.client.query_pages()

        max_num = 0
        for page in pages:
            if page.clotion_id and page.clotion_id.startswith("CLO-"):
                try:
                    num = int(page.clotion_id.split("-")[1])
                    max_num = max(max_num, num)
                except (IndexError, ValueError):
                    pass

        next_num = max_num + 1
        return f"CLO-{next_num:03d}"
