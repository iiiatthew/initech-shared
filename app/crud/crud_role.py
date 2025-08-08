from typing import Optional

import ksuid
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.role import Role
from app.models.user import User
from app.schemas.role import RoleCreate, RoleUpdate


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    def get_by_name(self, db: Session, *, role_name: str) -> Optional[Role]:
        return db.query(Role).filter(Role.role_name == role_name).first()

    def create(self, db: Session, *, obj_in: RoleCreate) -> Role:
        # Generate KSUID
        role_id = str(ksuid.ksuid())

        db_obj = Role(
            id=role_id,
            role_name=obj_in.role_name,
            role_description=obj_in.role_description,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_users(self, db: Session, *, db_obj: Role, user_ids: list[str]) -> Role:
        # Get users by IDs
        users = db.query(User).filter(User.id.in_(user_ids)).all()

        # Check if any user IDs were not found
        found_user_ids = {user.id for user in users}
        missing_user_ids = set(user_ids) - found_user_ids
        if missing_user_ids:
            from fastapi import HTTPException

            raise HTTPException(
                status_code=400, detail=f'Users not found: {", ".join(missing_user_ids)}'
            )

        db_obj.users = users
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def add_user(self, db: Session, *, db_obj: Role, user: User) -> Role:
        if user not in db_obj.users:
            db_obj.users.append(user)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        else:
            from fastapi import HTTPException

            raise HTTPException(
                status_code=400,
                detail=f'User {user.username} already exists in role {db_obj.role_name}',
            )
        return db_obj

    def remove_user(self, db: Session, *, db_obj: Role, user: User) -> Role:
        if user in db_obj.users:
            db_obj.users.remove(user)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj


role = CRUDRole(Role)
