import secrets
import string

from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app import crud
from app.models.token import Token

security = HTTPBearer()
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def verify_token(db: Session, credentials: HTTPAuthorizationCredentials) -> Token:
    token = credentials.credentials
    db_token = crud.token.get_by_token(db, token=token)

    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid authentication credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    return db_token


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def generate_password(length: int = 12) -> str:
    """Generate a random password with letters, digits, and special characters."""
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password
