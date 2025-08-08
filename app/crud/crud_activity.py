
import ksuid
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.activity import Activity
from app.schemas.activity import ActivityCreate


class CRUDActivity(CRUDBase[Activity, ActivityCreate, dict]):
    def create(self, db: Session, *, obj_in: ActivityCreate) -> Activity:
        # Generate KSUID
        activity_id = str(ksuid.ksuid())

        db_obj = Activity(
            id=activity_id,
            endpoint=obj_in.endpoint,
            request=obj_in.request,
            response=obj_in.response,
            status_code=obj_in.status_code,
            token_id=obj_in.token_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_token(
        self, db: Session, *, token_id: str, skip: int = 0, limit: int = 100
    ) -> list[Activity]:
        return (
            db.query(Activity)
            .filter(Activity.token_id == token_id)
            .order_by(Activity.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


activity = CRUDActivity(Activity)
