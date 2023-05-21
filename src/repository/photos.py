import time
import calendar
import io
from typing import List

import cloudinary
import cloudinary.uploader
import qrcode
from sqlalchemy.orm import Session
from qrcode.image.pure import PyPNGImage

from src.database.models import Photo, User, Role, Tag
from src.repository import tags as repository_tags
from src.schemas import DescriptionUpdate
from src.conf.config import settings


current_GMT = time.gmtime()
time_stamp = calendar.timegm(current_GMT)


async def upload_photo(
    user_id: int, src_url: str, description: str, tags: List, db: Session
) -> Photo:
    if tags:
        tag_list = await repository_tags.create_tags_for_photo(tags[0].split(","), db)
    new_photo = Photo(
        photo=src_url, user_id=user_id, description=description, tags=tag_list
    )
    db.add(new_photo)
    db.commit()
    db.refresh(new_photo)
    return new_photo


async def get_all_photos(limit: int, offset: int, db: Session):
    photos = db.query(Photo).limit(limit).offset(offset).all()
    return photos


async def get_photo(photo_id: int, db: Session) -> Photo:
    return db.query(Photo).filter(Photo.id == photo_id).first()


async def remove_photo(photo_id: int, user: User, db: Session) -> Photo | None:
    if user.roles == Role.admin:
        photo = db.query(Photo).filter(Photo.id == photo_id).first()
    else:
        photo = (
            db.query(Photo)
            .filter(Photo.id == photo_id, user.id == Photo.user_id)
            .first()
        )
    if photo:
        db.delete(photo)
        db.commit()
    return photo


async def update_description(
    photo_id: int, body: DescriptionUpdate, user: User, db: Session
) -> Photo | None:
    if user.roles == Role.admin:
        photo = db.query(Photo).filter(Photo.id == photo_id).first()
    else:
        photo = (
            db.query(Photo)
            .filter(Photo.id == photo_id, user.id == Photo.user_id)
            .first()
        )
    if photo:
        photo.description = body.description
        db.commit()
    return photo


async def create_qr_code(
    photo_id: int, url: str, user: User, db: Session
) -> Photo | None:
    photo = (
        db.query(Photo).filter(Photo.id == photo_id, user.id == Photo.user_id).first()
    )
    if photo:
        code = qrcode.make(url, image_factory=PyPNGImage)
        buffer = io.BytesIO()
        code.save(buffer)
        buffer.seek(0)

    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_secret,
        secure=True,
    )
    r = cloudinary.uploader.upload(
        buffer,
        public_id=f"photo_share_team4/qrcode/{user.user_name}_{time_stamp}",
        overwrite=True,
    )
    src_url = cloudinary.CloudinaryImage(
        f"photo_share_team4/qrcode/{user.user_name}_{time_stamp}"
    ).build_url(width=500, height=500, crop="fill", version=r.get("version"))

    photo.qr_code = src_url
    db.commit()
    return photo


async def search_photo_by_keyword(search_by: str, filter_by: str, db: Session) -> List[Photo]:
    if filter_by == "creation_date":
            result = db.query(Photo).filter(Photo.description.like(search_by)).order_by(Photo.created_at).all()
    elif filter_by == "rating":
            result = db.query(Photo).filter(Photo.description.like(search_by)).order_by(Photo.average_rating).all()
    else:
        result = db.query(Photo).filter(Photo.description == search_by).all()
    return result

async def search_photo_by_tag(search_by: str, filter_by: str, db: Session) -> List[Photo]:
    if filter_by == "creation_date":
        result = db.query(Photo).join(Photo.tags).filter(Tag.tag_name == search_by).order_by(Photo.created_at).all()
    elif filter_by == "rating":
        result = db.query(Photo).join(Photo.tags).filter(Tag.tag_name == search_by).order_by(Photo.average_rating).all()
    else:
        result = db.query(Photo).join(Photo.tags).filter(Tag.tag_name == search_by).all()
    return result