from enum import StrEnum

from pydantic import BaseModel, Field


class DistributionType(StrEnum):
    SELF_HOSTED = "self_hosted"


class FilesConfig(BaseModel):
    max_size_bytes: int = Field(default=500000000)
    types: list[str] = Field(default=["txt", "csv", "xlsx", "docx", "pdf", "pptx", "md", "json"])
    mime_types: dict[str, list[str]] = Field(
        default={
            "text/csv": [".csv"],
            "text/plain": [".txt"],
            "text/markdown": [".md"],
            "application/json": [".json"],
            "application/pdf": [".pdf"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
            "application/vnd.openxmlformats-officedocument.presentationml.presentation": [".pptx"],
        }
    )


class Settings(BaseModel):
    files: FilesConfig = Field(default_factory=FilesConfig)
    distribution_type: DistributionType = Field(default=DistributionType.SELF_HOSTED)
