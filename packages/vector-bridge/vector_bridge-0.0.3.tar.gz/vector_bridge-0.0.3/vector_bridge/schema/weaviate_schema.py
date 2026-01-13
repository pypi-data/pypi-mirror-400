from typing import Any

from pydantic import BaseModel, Field
from vector_bridge.schema.helpers.enums import FilterOperator, SchemaDiffState


class Filter(BaseModel):
    name: str
    description: str
    supported: bool
    operator: FilterOperator
    operator_settings: dict


class StateFullFilter(Filter):
    state: SchemaDiffState = Field(default=SchemaDiffState.DEFAULT)


class Filtering(BaseModel):
    operators: list[Filter]

    def get_filter_by_name(self, name: str):
        for _operator in self.operators:
            if _operator.name == name:
                return _operator


class StateFullFiltering(Filtering):
    operators: list[StateFullFilter]  # type: ignore


class Sorting(BaseModel):
    supported: bool


class Property(BaseModel):
    name: str
    description: str
    data_type: Any
    tokenization: Any
    filtering: Filtering
    sorting: Sorting
    returned: bool


class StateFullProperty(Property):
    state: SchemaDiffState
    filtering: StateFullFiltering


class Schema(BaseModel):
    name: str
    description: str
    properties: list[Property]
    vectorizer: str


class StateFullSchema(Schema):
    state: SchemaDiffState
    properties: list[StateFullProperty]  # type: ignore
