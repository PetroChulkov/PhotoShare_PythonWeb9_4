from fastapi import Depends

from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel
from src.database.connect import get_db


async def get_user_by_username(username: str, db: Session) -> User:
    return db.query(User).filter(User.username == username).first()


async def get_user_by_email(email: str, db: Session) -> User:
    return db.query(User).filter(User.email == email).first()


async def check_quantity_of_users(db: Session = Depends(get_db)) -> list:
    users = db.query(User).all()
    return users


async def create_user(body: UserModel, db: Session) -> User:
    users_list = await check_quantity_of_users(db)
    if len(users_list) == 0:
        user_data = body.dict()
        user_data["roles"] = "admin"
        new_user = User(**user_data)
    else:
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


async def check_exist_mail(body: UserModel, db: Session = Depends(get_db)):
    check_mail = db.query(User).filter_by(email=body.email).first()
    return check_mail


async def check_exist_username(body: UserModel, db: Session = Depends(get_db)):
    check_username = db.query(User).filter_by(user_name=body.user_name).first()
    return check_username


async def to_ban_user(body: UserModel, email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=email).first()
    user.ban_status = True
    db.commit()
    return user


async def check_ban_status(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=username).first()
    return user.ban_status
