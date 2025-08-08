from typing import Any, Optional, Union

import ksuid
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.security import generate_password, get_password_hash
from app.crud.base import CRUDBase
from app.models.user import User, UserStatus
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        # Generate username
        base_username = f'{obj_in.first_name[0].lower()}{obj_in.last_name.lower()}'
        username = base_username
        counter = 1

        # Check if username exists and append number if needed
        while self.get_by_username(db, username=username):
            username = f'{base_username}{counter}'
            counter += 1

        # Generate display name
        display_name = f'{obj_in.first_name} {obj_in.last_name}'

        # Generate KSUID
        user_id = str(ksuid.ksuid())

        # Handle password - use provided or generate
        if obj_in.password:
            hashed_password = get_password_hash(obj_in.password)
        else:
            # Generate a random password
            generated_password = generate_password()
            hashed_password = get_password_hash(generated_password)

        db_obj = User(
            id=user_id,
            username=username,
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            email=obj_in.email,
            display_name=display_name,
            hashed_password=hashed_password,
            status=UserStatus.active,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        # If password was generated, temporarily store it in a non-persisted attribute
        if not obj_in.password:
            db_obj.generated_password = generated_password

        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, dict[str, Any]]
    ) -> User:
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)

        # Handle password update separately
        if 'password' in update_data:
            if update_data['password']:  # Only hash if password is not empty
                hashed_password = get_password_hash(update_data['password'])
                update_data['hashed_password'] = hashed_password
            del update_data['password']  # Always remove password from update_data

        # Handle username update if names change
        if 'first_name' in update_data or 'last_name' in update_data:
            first_name = update_data.get('first_name', db_obj.first_name)
            last_name = update_data.get('last_name', db_obj.last_name)

            # Generate new username
            base_username = f'{first_name[0].lower()}{last_name.lower()}'
            username = base_username
            counter = 1

            # Check if username exists and append number if needed (excluding current user)
            while True:
                existing_user = self.get_by_username(db, username=username)
                if not existing_user or existing_user.id == db_obj.id:
                    break
                username = f'{base_username}{counter}'
                counter += 1

            update_data['username'] = username

        # Update the user
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def search(self, db: Session, *, query: str, skip: int = 0, limit: int = 100) -> list[User]:
        return (
            db.query(User)
            .filter(
                or_(
                    User.username.contains(query),
                    User.first_name.contains(query),
                    User.last_name.contains(query),
                    User.email.contains(query),
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def remove_from_all_roles(self, db: Session, *, user: User) -> None:
        # Remove user from all roles they are currently assigned to
        for role in user.roles:
            role.users.remove(user)
            db.add(role)
        db.commit()


user = CRUDUser(User)
