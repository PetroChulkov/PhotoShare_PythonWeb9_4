from fastapi import Depends

from sqlalchemy.orm import Session
from src.database.models import User, Photo
from src.schemas import UserModel, UserPublic
from src.database.connect import get_db


async def get_user_by_username(username: str, db: Session) -> User:
    return db.query(User).filter(User.user_name == username).first()


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
    return user


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


async def get_user_profile(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_name == username).first()
    if user:
        photos_amount = db.query(Photo).filter(Photo.user_id == user.id).count()
        public_profile = UserPublic(
            user_name=user.user_name,
            photos_published=photos_amount,
            created_at=user.created_at,
        )
    return public_profile


async def get_amount_photos(username: str, db: Session = Depends(get_db)):
    user = await get_user_by_username(username=username, db=db)
    if user:
        photos_amount = db.query(Photo).filter(Photo.user_id == user.id).count()
        return photos_amount


async def change_password(user: User, new_password: str, db: Session = Depends(get_db)):
    user.password = new_password
    db.commit()
    return user


# async def confirmed_email(email: str, db: Session):
#     user = await search_by_mail(email, db)
#     user.confirmed = True
#     db.commit()
