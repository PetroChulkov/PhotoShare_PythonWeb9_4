from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.database.models import Photo, User
from src.repository import tags as repository_tags
from src.schemas import PhotoModel, DescriptionUpdate
from src.database.connect import get_db
from typing import List


async def upload_photo(
    user_id: int, src_url: str, description: str, tags: List, db: Session
) -> Photo:
    if tags:
        tag_list = await repository_tags.create_tags_for_photo(tags[0].split(","), db)
    new_photo = Photo(photo=src_url, user_id=user_id, description=description, tags=tag_list)
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

async def update_description(contact_id: int, body: DescriptionUpdate, user: User, db: Session) -> Photo | None:
    photo = db.query(Photo).filter(Photo.id == contact_id, Photo.user_id == user.id).first()
    if photo:
        photo.description = body.description
        db.commit()
    return photo
