from sqlalchemy.orm import Session

from app.models import Log


def create_log(db: Session, user_id, action: str, status: str) -> None:
    log = Log(user_id=user_id, action=action, status=status)
    db.add(log)
    db.commit()
