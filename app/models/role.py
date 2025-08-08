from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.user import user_roles


class Role(Base):
    __tablename__ = 'roles'

    id = Column(String, primary_key=True, index=True)
    role_name = Column(String, unique=True, index=True, nullable=False)
    role_description = Column(String, nullable=True)

    # Relationships
    users = relationship('User', secondary=user_roles, back_populates='roles', lazy='selectin')
