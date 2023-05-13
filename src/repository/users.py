from fastapi import Depends

from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel
from src.database.connect import get_db


async def get_user_by_email(email: str, db: Session) -> User:
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    new_user = User(**body.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def search_by_mail(inquiry: str, db: Session = Depends(get_db)):
    contacts = db.query(User).filter_by(email=inquiry).first()
    return contacts


def check_exist_mail(body: UserModel, db: Session = Depends(get_db)):
    check_mail = db.query(User).filter_by(email=body.email).first()
    return check_mail
