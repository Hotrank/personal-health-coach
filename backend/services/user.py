import uuid

from database.db_models import User
from sqlalchemy.orm import Session


def get_or_create_user(db: Session, google_sub: str, name: str = None, email: str = None) -> uuid.UUID:
    user = db.query(User).filter(User.google_sub == google_sub).first()
    if user:
        return user.id
    # User does not exist, create one
    new_user = User(google_sub=google_sub, name=name, email=email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # load new_user.id
    return new_user.id
