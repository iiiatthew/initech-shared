from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.models.token import Token

router = APIRouter()


@router.get('/', response_model=list[schemas.User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_token: Token = Depends(deps.get_current_token),
) -> Any:
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users


@router.get('/{user_id}', response_model=schemas.UserWithRoles)
def read_user(
    user_id: str,
    db: Session = Depends(deps.get_db),
    current_token: Token = Depends(deps.get_current_token),
) -> Any:
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    
    # Convert to response model with role IDs
    user_dict = user.__dict__.copy()
    user_dict['role_ids'] = [role.id for role in user.roles]
    
    return schemas.UserWithRoles(**user_dict)


@router.post('/', response_model=schemas.UserCreateResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(deps.get_db),
    current_token: Token = Depends(deps.get_current_token),
) -> Any:
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail='A user with this email already exists.',
        )
    user = crud.user.create(db, obj_in=user_in)

    # Create response with generated password if applicable
    user_response = schemas.UserCreateResponse.model_validate(user)
    if hasattr(user, 'generated_password'):
        user_response.generated_password = user.generated_password

    return user_response


@router.patch('/{user_id}', response_model=schemas.User)
def update_user(
    user_id: str,
    user_in: schemas.UserUpdate,
    db: Session = Depends(deps.get_db),
    current_token: Token = Depends(deps.get_current_token),
) -> Any:
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    # Check email uniqueness if email is being updated
    if user_in.email and user_in.email != user.email:
        existing_user = crud.user.get_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail='A user with this email already exists.',
            )

    # Update display_name if names are changed
    update_data = user_in.model_dump(exclude_unset=True)
    if 'first_name' in update_data or 'last_name' in update_data:
        first_name = update_data.get('first_name', user.first_name)
        last_name = update_data.get('last_name', user.last_name)
        update_data['display_name'] = f'{first_name} {last_name}'

    user = crud.user.update(db, db_obj=user, obj_in=update_data)
    return user


@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    db: Session = Depends(deps.get_db),
    current_token: Token = Depends(deps.get_current_token),
) -> None:
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    # Remove user from all roles before deletion
    crud.user.remove_from_all_roles(db, user=user)

    crud.user.remove(db, id=user_id)


@router.post('/{user_id}/roles/{role_id}', status_code=status.HTTP_201_CREATED)
def assign_role_to_user(
    user_id: str,
    role_id: str,
    db: Session = Depends(deps.get_db),
    current_token: Token = Depends(deps.get_current_token),
) -> Any:
    """Assign a role to a user."""
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    
    role = crud.role.get(db, id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail='Role not found')
    
    # Check if already assigned
    if role in user.roles:
        raise HTTPException(status_code=400, detail='User already has this role')
    
    # Add role to user
    user.roles.append(role)
    db.add(user)
    db.commit()
    
    return {'message': f'Role {role.role_name} assigned to user {user.display_name}'}


@router.delete('/{user_id}/roles/{role_id}', status_code=status.HTTP_204_NO_CONTENT)
def remove_role_from_user(
    user_id: str,
    role_id: str,
    db: Session = Depends(deps.get_db),
    current_token: Token = Depends(deps.get_current_token),
) -> None:
    """Remove a role from a user."""
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    
    role = crud.role.get(db, id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail='Role not found')
    
    # Check if user has the role
    if role not in user.roles:
        raise HTTPException(status_code=400, detail='User does not have this role')
    
    # Remove role from user
    user.roles.remove(role)
    db.add(user)
    db.commit()
