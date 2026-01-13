from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from vector_bridge.schema.integrations import Integration
from vector_bridge.schema.security_group import SecurityGroup
from vector_bridge.schema.user import User


class Role(StrEnum):
    user = "user"
    admin = "admin"


class UserIntegrationWithPermissions(BaseModel):
    integration_id: str
    integration_name: str
    security_group: SecurityGroup


class IntegrationSecurityGroup(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    integration: Integration
    security_groups: list[SecurityGroup]


class UserWithIntegrationsAndPermissions(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user: User
    integrations_permissions: list[IntegrationSecurityGroup]


class UserIntegrationSecurityGroup(IntegrationSecurityGroup):
    model_config = ConfigDict(from_attributes=True)

    user: User


class UserIntegrationList(BaseModel):
    user_integrations: list[UserIntegrationSecurityGroup]
    limit: int
    last_evaluated_key: str | None = Field(default=None)
