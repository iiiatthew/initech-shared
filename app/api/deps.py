from collections.abc import Generator
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import security, verify_token
from app.models.token import Token


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_token(
    db: Session = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Token:
    return verify_token(db, credentials)


def get_current_token_optional(
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
) -> Optional[Token]:
    if credentials:
        try:
            return verify_token(db, credentials)
        except HTTPException:
            return None
    return None
