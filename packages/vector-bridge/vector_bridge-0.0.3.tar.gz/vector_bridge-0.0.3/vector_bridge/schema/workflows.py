import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class WorkflowStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
    ON_HOLD = "on_hold"


class WorkflowCache(BaseModel):
    method_name: str
    args: list
    kwargs: dict
    started_at: datetime
    processed_at: datetime
    processing_time: float
    logs: str | None = ""
    traceback: str | None = ""
    result: str | None = ""


class WorkflowBase(BaseModel):
    workflow_id: str
    workflow_name: str
    description: str
    cache: dict[str, WorkflowCache] = Field(default_factory=dict)
    status: WorkflowStatus = Field(default=WorkflowStatus.PENDING)


class WorkflowCreate(WorkflowBase):
    pass


class WorkflowUpdate(BaseModel):
    cache: dict[str, WorkflowCache] = Field(default_factory=dict)
    status: WorkflowStatus | None = Field(default=None)


class WorkflowData(WorkflowBase):
    integration_id: str
    expire_at: int
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str


class PaginatedWorkflows(BaseModel):
    workflows: list[WorkflowData] = Field(default_factory=list)
    limit: int
    last_evaluated_key: str | None = None
    has_more: bool = False


def serialize_result(result: Any) -> dict[str, Any]:
    """Serialize result handling Pydantic models, dataclasses, and regular objects."""
    if result is None:
        return {"type": "none", "data": None}

    # Handle Pydantic models
    if hasattr(result, "model_dump"):  # Pydantic v2
        return {
            "type": "pydantic",
            "class_module": result.__class__.__module__,
            "class_name": result.__class__.__name__,
            "data": result.model_dump(),
        }
    elif hasattr(result, "dict"):  # Pydantic v1
        return {
            "type": "pydantic",
            "class_module": result.__class__.__module__,
            "class_name": result.__class__.__name__,
            "data": result.dict(),
        }

    # Handle dataclasses
    elif is_dataclass(result):
        return {
            "type": "dataclass",
            "class_module": result.__class__.__module__,
            "class_name": result.__class__.__name__,
            "data": asdict(result),  # type: ignore
        }

    # Handle lists/tuples of serializable objects
    elif isinstance(result, (list, tuple)):
        serialized_items = [serialize_result(item) for item in result]
        return {
            "type": "list" if isinstance(result, list) else "tuple",
            "data": serialized_items,
        }

    # Handle dictionaries
    elif isinstance(result, dict):
        serialized_dict = {k: serialize_result(v) for k, v in result.items()}
        return {"type": "dict", "data": serialized_dict}

    # Handle regular JSON-serializable objects
    else:
        try:
            json.dumps(result)  # Test if it's JSON serializable
            return {"type": "json", "data": result}
        except (TypeError, ValueError):
            # Fallback to string representation
            return {"type": "string", "data": str(result)}


def deserialize_result(serialized_data: dict[str, Any]) -> Any:
    """Deserialize result back to original type."""
    if not isinstance(serialized_data, dict) or "type" not in serialized_data:
        return serialized_data

    result_type = serialized_data["type"]
    data = serialized_data["data"]

    if result_type == "none":
        return None

    elif result_type == "pydantic":
        try:
            # Import the class dynamically
            module_name = serialized_data["class_module"]
            class_name = serialized_data["class_name"]

            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            return cls(**data)
        except Exception as e:
            from vector_bridge.sync_io.client.workflows import log_message

            log_message(
                f"Failed to deserialize Pydantic model {class_name}: {str(e)}",
                "WARNING",
            )
            return data

    elif result_type == "dataclass":
        try:
            # Import the class dynamically
            module_name = serialized_data["class_module"]
            class_name = serialized_data["class_name"]

            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            return cls(**data)
        except Exception as e:
            from vector_bridge.sync_io.client.workflows import log_message

            log_message(f"Failed to deserialize dataclass {class_name}: {str(e)}", "WARNING")
            return data

    elif result_type == "list":
        return [deserialize_result(item) for item in data]

    elif result_type == "tuple":
        return tuple(deserialize_result(item) for item in data)

    elif result_type == "dict":
        return {k: deserialize_result(v) for k, v in data.items()}

    elif result_type == "json":
        return data

    elif result_type == "string":
        return data

    else:
        return data
