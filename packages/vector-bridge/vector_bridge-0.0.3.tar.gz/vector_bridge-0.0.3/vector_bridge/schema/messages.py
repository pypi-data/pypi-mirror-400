from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from vector_bridge.schema.helpers.enums import MessageType, UserType


class Meta(BaseModel):
    prompt_tokens: int = Field(default=0)
    completion_tokens: int = Field(default=0)
    total_tokens: int = Field(default=0)
    function_calls: list[Any] = Field(default_factory=list)  # "ToolCallKwargs"
    function_responses: list[Any] = Field(default_factory=list)  # "ToolResponseMessage"


class MessageBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    integration_id: str
    chat_created_by: str
    timestamp: datetime
    message_created_by: str
    message_creator_type: UserType
    message_type: MessageType
    content: str
    deleted: bool = False


class VectorAdditionalData(BaseModel):
    distance: float | None = None


class MessageInDB:
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    message_id: str
    data: dict | None
    meta: Meta

    @property
    def uuid(self):
        return self.message_id

    additional: VectorAdditionalData | None = Field(default=None)


class MessagesList(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    messages: list[MessageInDB]
    limit: int
    offset: int | None
    has_more: bool
