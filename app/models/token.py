from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Token(Base):
    __tablename__ = 'tokens'

    id = Column(String, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)

    # Relationships
    activities = relationship('Activity', back_populates='token', cascade='all, delete-orphan')
