import secrets
from typing import Optional

import ksuid
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.token import Token
from app.schemas.token import TokenCreate


class CRUDToken(CRUDBase[Token, TokenCreate, dict]):
    def get_by_token(self, db: Session, *, token: str) -> Optional[Token]:
        return db.query(Token).filter(Token.token == token).first()

    def create(self, db: Session) -> Token:
        # Generate KSUID for token ID
        token_id = str(ksuid.ksuid())

        # Generate 32-character random token
        token_value = secrets.token_urlsafe(24)[:32]

        db_obj = Token(
            id=token_id,
            token=token_value,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


token = CRUDToken(Token)
