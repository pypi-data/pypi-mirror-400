from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from vector_bridge.schema.helpers.enums import UserStatus, UserType
from vector_bridge.schema.security_group import SecurityGroup


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    full_name: str | None
    email: str | None
    phone_number: str | None = ""
    country: str | None = ""
    state_region: str | None = ""
    city: str | None = ""
    address: str | None = ""
    zip_code: str | None = ""
    company_name: str | None = ""
    user_role: str | None = ""  # job title
    avatar_url: str | None = ""
    user_type: UserType
    user_status: UserStatus
    organization_id: str | None = "None"
    ws_connections: dict[str, bool] = Field(default_factory=dict)

    @property
    def uuid(self):
        return self.id

    def __init__(self, **data):
        for key, value in data.items():
            if value == "":
                data[key] = None
            elif value == str(None):
                data[key] = None

        super().__init__(**data)
        if self.id == self.email:
            self.email = None

    @property
    def is_owner(self):
        return self.user_type == UserType.OWNER


class UserWithSecurityGroup(User):
    model_config = ConfigDict(from_attributes=True)

    security_group: SecurityGroup | None = Field(default=None)

    def __init__(self, **data):
        super().__init__(**data)


class UserInDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    full_name: str | None
    email: str | None
    phone_number: str | None = None
    country: str | None = None
    state_region: str | None = None
    city: str | None = None
    address: str | None = None
    zip_code: str | None = None
    company_name: str | None = None
    user_role: str | None = None
    avatar_url: str | None = None
    user_type: UserType
    user_status: UserStatus
    organization_id: str
    hashed_password: str | None
    user_data: dict[str, Any] | None
    ws_connections: dict[str, bool] = Field(default_factory=dict)

    @property
    def uuid(self):
        return self.id


class UserPrivate(User):
    model_config = ConfigDict(from_attributes=True)

    hashed_password: str | None
    user_data: dict[str, Any] | None
    ws_connections: dict[str, bool] = Field(default_factory=dict)


class UserCreate(BaseModel):
    first_name: str | None = Field(None)
    last_name: str | None = Field(None)
    email: str
    password: str
    user_type: UserType = Field(default=UserType.USER)


class ConfirmUserEmail(BaseModel):
    email: str
    code: str


class ForgotUserPassword(BaseModel):
    email: str
    code: str
    password: str


class ChangeUserPassword(BaseModel):
    old_password: str
    new_password: str


class UserUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    full_name: str | None
    phone_number: str | None = None
    country: str | None = None
    state_region: str | None = None
    city: str | None = None
    address: str | None = None
    zip_code: str | None = None
    company_name: str | None = None
    user_role: str | None = None
    avatar_url: str | None = None


class OtherUserUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    full_name: str | None
    email: str | None
    phone_number: str | None = None
    country: str | None = None
    state_region: str | None = None
    city: str | None = None
    address: str | None = None
    zip_code: str | None = None
    company_name: str | None = None
    user_role: str | None = None
    organization_id: str | None


class UsersList(BaseModel):
    users: list[User]
    limit: int
    last_evaluated_key: str | None
    has_more: bool = Field(default=False)
