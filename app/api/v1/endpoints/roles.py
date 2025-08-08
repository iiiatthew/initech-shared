from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.models.token import Token

router = APIRouter()


@router.get('/', response_model=list[schemas.Role])
def read_roles(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_token: Token = Depends(deps.get_current_token),
) -> Any:
    roles = crud.role.get_multi(db, skip=skip, limit=limit)
    return roles


@router.get('/{role_id}', response_model=schemas.RoleWithUsers)
def read_role(
    role_id: str,
    db: Session = Depends(deps.get_db),
    current_token: Token = Depends(deps.get_current_token),
) -> Any:
    role = crud.role.get(db, id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail='Role not found')
    
    # Convert to response model with user IDs
    role_dict = role.__dict__.copy()
    role_dict['user_ids'] = [user.id for user in role.users]
    
    return schemas.RoleWithUsers(**role_dict)


@router.get('/{role_id}/users', response_model=list[schemas.User])
def get_role_users(
    role_id: str,
    db: Session = Depends(deps.get_db),
    current_token: Token = Depends(deps.get_current_token),
) -> Any:
    """Get all users assigned to a specific role."""
    role = crud.role.get(db, id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail='Role not found')
    
    return role.users