from fastapi import Depends

from sqlalchemy.orm import Session

from src.database.models import Photo
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