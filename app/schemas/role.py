from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RoleBase(BaseModel):
    role_name: str = Field(..., min_length=1, description='Name of the role')
    role_description: Optional[str] = Field(None, description='Description of the role')


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    role_name: Optional[str] = Field(None, min_length=1)
    role_description: Optional[str] = None
    user_ids: Optional[list[str]] = Field(
        None, description='List of user IDs to assign to this role'
    )


class RoleInDBBase(RoleBase):
    id: str
    model_config = ConfigDict(from_attributes=True)


class Role(RoleInDBBase):
    pass


