import re
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserStatus(str, Enum):
    active = "active"
    disabled = "disabled"
    terminated = "terminated"



class UserBase(BaseModel):
    first_name: str = Field(..., min_length=1, description="User's first name")
    last_name: str = Field(..., min_length=1, description="User's last name")
    email: str = Field(..., description="User's email address")

    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z]+$', v):
            raise ValueError('Names must contain only letters')
        return v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v


class UserCreate(UserBase):
    password: Optional[str] = Field(
        None,
        min_length=6,
        description="User's password (optional, will be auto-generated if not provided)",
    )


class UserUpdate(UserBase):
    first_name: Optional[str] = Field(None, min_length=1)
    last_name: Optional[str] = Field(None, min_length=1)
    email: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6, description='New password (optional)')
    status: Optional[UserStatus] = Field(None, description='User status')


class UserInDBBase(UserBase):
    id: str
    username: str
    display_name: str
    status: UserStatus = Field(default=UserStatus.active, description='User status')
    model_config = ConfigDict(from_attributes=True)


class User(UserInDBBase):
    pass


class UserCreateResponse(UserInDBBase):
    generated_password: Optional[str] = Field(
        None, description='Auto-generated password (only shown on creation)'
    )


