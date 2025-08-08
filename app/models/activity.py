from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Activity(Base):
    __tablename__ = 'activities'

    id = Column(String, primary_key=True, index=True)
    endpoint = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    request = Column(Text, nullable=True)
    response = Column(Text, nullable=True)
    status_code = Column(Integer, nullable=False)
    token_id = Column(String, ForeignKey('tokens.id'), nullable=False)

    # Relationships
    token = relationship('Token', back_populates='activities')
