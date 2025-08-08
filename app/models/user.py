import enum

from sqlalchemy import Column, Enum, ForeignKey, String, Table
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserStatus(str, enum.Enum):
    active = "active"
    disabled = "disabled"
    terminated = "terminated"

# Association table for many-to-many relationship between users and roles
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', String, ForeignKey('users.id'), primary_key=True),
    Column('role_id', String, ForeignKey('roles.id'), primary_key=True),
)


class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.active)

    # Relationships
    roles = relationship('Role', secondary=user_roles, back_populates='users', lazy='selectin')
