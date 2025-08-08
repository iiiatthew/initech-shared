from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TokenBase(BaseModel):
    token: str


class TokenCreate(BaseModel):
    pass  # Token is generated automatically


class Token(TokenBase):
    id: str
    model_config = ConfigDict(from_attributes=True)


class TokenWithActivities(Token):
    activities: list['ActivityBase'] = []


class BearerTokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'


# For API activity
class ActivityBase(BaseModel):
    id: str
    endpoint: str
    timestamp: datetime
    request: Optional[str]
    response: Optional[str]
    status_code: int
    model_config = ConfigDict(from_attributes=True)


TokenWithActivities.model_rebuild()
