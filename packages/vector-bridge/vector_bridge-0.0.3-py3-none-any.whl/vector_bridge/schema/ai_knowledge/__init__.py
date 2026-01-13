from pydantic import BaseModel, ConfigDict, Field


class PresignedUploadUrl(BaseModel):
    url: str
    body: dict


class BaseAIKnowledgeChunk(BaseModel):
    item_id: str
    index: int
    content: str

    @property
    def uuid(self):
        return self.item_id


class BaseAIKnowledge(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    schema_name: str = Field(default="")
    unique_identifier: str = Field(default="")
    content: str | None = None
    timestamp: str | None = None

    # _chunk_size: int = 384
    # _chunk_overlap: int = 76


class BaseSchemalessAIKnowledge(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    schema_name: str = Field(default="")
    unique_identifier: str = Field(default="")
    content: str | None = None

    # _chunk_size: int = 384
    # _chunk_overlap: int = 76
