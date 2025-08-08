from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ActivityBase(BaseModel):
    endpoint: str
    request: Optional[str] = None
    response: Optional[str] = None
    status_code: int


class ActivityCreate(ActivityBase):
    token_id: str


class Activity(ActivityBase):
    id: str
    timestamp: datetime
    token_id: str
    model_config = ConfigDict(from_attributes=True)
