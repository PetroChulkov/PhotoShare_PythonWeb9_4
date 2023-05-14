from fastapi import Depends

from sqlalchemy.orm import Session

from src.database.models import Photo, User
from src.schemas import PhotoModel
from src.database.connect import get_db


async def upload_photo(
    user_id: int, src_url: str, description: str, db: Session
) -> Photo:
    new_photo = Photo(photo=src_url, user_id=user_id, description=description)
    db.add(new_photo)
    db.commit()
    db.refresh(new_photo)
    return new_photo

async def get_photo(
        photo_id: int, db: Session
) -> Photo:
    return db.query(Photo).filter(Photo.id == photo_id).first()

async def remove_photo(photo_id: int, user: User, db: Session) -> Photo | None:
    photo = db.query(Photo).filter(Photo.id == photo_id, Photo.user_id == user.id).first()
    if photo:
        db.delete(photo)
        db.commit()
    return photo
