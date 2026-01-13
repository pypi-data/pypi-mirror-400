from datetime import datetime, timezone

from pydantic import BaseModel, Field
from vector_bridge import AsyncVectorBridgeClient, VectorBridgeClient
from vector_bridge.schema.security_group import SecurityGroup


class APIKey(BaseModel):
    hash_key: str | None = Field(default=None)
    organization_id: str
    api_key: str
    key_name: str
    integration_name: str
    user_id: str = Field(default="")
    security_groups: list[SecurityGroup] = Field(default_factory=list)
    expire_timestamp: datetime
    monthly_request_limit: int
    created_by: str
    created_at: datetime

    def is_expired(self) -> bool:
        """Check if the API key is expired based on the expire_timestamp."""
        current_time = datetime.now(timezone.utc)
        return current_time >= self.expire_timestamp

    def delete(self, client: VectorBridgeClient) -> None:
        client.api_keys.delete_api_key(api_key=self.api_key)

    async def a_delete(self, client: AsyncVectorBridgeClient) -> None:
        await client.api_keys.delete_api_key(api_key=self.api_key)


class APIKeyCreate(BaseModel):
    key_name: str
    integration_name: str
    security_group_ids: list[str] = Field(default_factory=list)
    expire_days: int
    monthly_request_limit: int
