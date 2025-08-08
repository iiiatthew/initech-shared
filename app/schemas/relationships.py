"""
Schemas for relationships between entities to avoid circular imports.
"""

from pydantic import Field

from app.schemas.role import RoleInDBBase
from app.schemas.user import UserInDBBase


class UserWithRoles(UserInDBBase):
    """User schema with their assigned roles."""
    role_ids: list[str] = Field(default_factory=list)


class RoleWithUsers(RoleInDBBase):
    """Role schema with its assigned users."""
    user_ids: list[str] = Field(default_factory=list)