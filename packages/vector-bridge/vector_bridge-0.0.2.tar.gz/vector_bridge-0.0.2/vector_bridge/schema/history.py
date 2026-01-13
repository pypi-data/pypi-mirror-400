from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ItemType(str):
    """Types of items that can have history."""

    TASK = "task"
    USER = "user"
    USER_INTEGRATION = "user_integration"
    FUNCTION = "function"
    INTEGRATION = "integration"
    INSTRUCTION = "instruction"
    SECURITY_GROUP = "security_group"


class HistoryChangeType(str):
    """Types of history changes."""

    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    FIELD_CHANGED = "field_changed"
    COMMENT_ADDED = "comment_added"
    COMMENT_UPDATED = "comment_updated"
    COMMENT_DELETED = "comment_deleted"
    SUBTASK_ADDED = "subtask_added"
    SUBTASK_UPDATED = "subtask_updated"
    SUBTASK_DELETED = "subtask_deleted"
    SUBTASK_COMPLETED = "subtask_completed"
    SUBTASK_REOPENED = "subtask_reopened"
    LABELS_ADDED = "labels_added"
    LABELS_REMOVED = "labels_removed"
    LABELS_UPDATED = "labels_updated"
    TASK_ASSIGNED = "task_assigned"
    TASK_UNASSIGNED = "task_unassigned"
    STATUS_CHANGED = "status_changed"
    PRIORITY_CHANGED = "priority_changed"
    BULK_UPDATE = "bulk_update"
    BULK_DELETE = "bulk_delete"


class HistoryEntry(BaseModel):
    """A single history entry."""

    history_id: str
    item_id: str = Field(description="The ID of the item this history belongs to")
    item_type: ItemType = Field(description="The type of item this history belongs to")
    integration_id: str | None = Field(None, description="The ID of the integration")
    change_type: HistoryChangeType = Field(description="The type of change")
    field_name: str | None = Field(None, description="The name of the field that changed")
    old_value: str | int | float | bool | list | dict | None = Field(None, description="The old value")
    new_value: str | int | float | bool | list | dict | None = Field(None, description="The new value")
    changed_by: str = Field(description="The ID of the user who made the change")
    changed_at: datetime = Field(description="When the change was made")
    additional_data: dict[str, Any] | None = Field(None, description="Additional data related to the change")
    meta: dict[str, Any] | None = Field(None, description="Metadata about the change context")


class PaginatedHistory(BaseModel):
    """Paginated history response."""

    item_id: str | None = Field(None, description="The ID of the item")
    item_type: ItemType | None = Field(None, description="The type of item")
    history: list[HistoryEntry] = Field(description="The history entries")
    limit: int = Field(description="The maximum number of entries")
    last_evaluated_key: str | None = Field(None, description="The key for pagination")
    has_more: bool = Field(description="Whether there are more history entries")
