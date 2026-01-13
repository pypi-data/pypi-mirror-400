from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from vector_bridge.schema.helpers.weaviate_schema import WeaviateInternals


class Weaviate(BaseModel):
    api_key: str = Field(default="")
    url: str = Field(default="")
    max_similarity_distance: float = Field(default=0.75)
    internals: WeaviateInternals


DEFAULT_INTEGRATION = "default"


class DB(BaseModel):
    weaviate: Weaviate


class Integration(BaseModel):
    organization_id: str
    integration_id: str
    integration_name: str
    integration_description: str
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str
    published: bool
    db: DB
    env_variables: dict

    @property
    def uuid(self):
        return self.integration_id


class IntegrationCreate(BaseModel):
    integration_name: str
    integration_description: str
    weaviate_url: str
    weaviate_api_key: str = Field(default="")


class IntegrationUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    integration_name: str | None = None
    integration_description: str | None = None
    published: bool | None = None

    db: DB | None = None
    env_variables: dict[str, str] | None = None
