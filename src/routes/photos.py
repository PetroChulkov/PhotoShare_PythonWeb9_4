import calendar
import time

import cloudinary
import cloudinary.uploader
from typing import List
from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Path,
    UploadFile,
    status,
    Form,
)
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.connect import get_db
from src.database.models import User, Role
from src.schemas import PhotoModel, PhotoDb, PhotoResponse
from typing import List
# UpdateContactRoleModel
from src.repository import photos as repository_photos
from src.services.auth import auth_service
from src.services.roles import RolesChecker
from src.conf.config import settings

current_GMT = time.gmtime()
time_stamp = calendar.timegm(current_GMT)

router = APIRouter(prefix="/photos", tags=["photos"])

allowed_post_photo = RolesChecker([Role.admin, Role.moderator, Role.user])
allowed_remove_photo = RolesChecker([Role.admin, Role.user])
allowed_update_photo = RolesChecker([Role.admin, Role.user])


@router.post(
    "/upload",
    response_model=PhotoResponse,
    name="Upload photo",
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(allowed_post_photo),
        Depends(RateLimiter(times=2, seconds=5)),
    ],
)
async def add_photo(
    body: str = Form(default=None),
    tags: List = Form(default=None),
    file: UploadFile = File(),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_secret,
        secure=True,
    )

    r = cloudinary.uploader.upload(
        file.file,
        public_id=f"photo_share_team4/{current_user.user_name}_{time_stamp}",
        overwrite=True,
    )
    src_url = cloudinary.CloudinaryImage(
        f"photo_share_team4/{current_user.user_name}_{time_stamp}"
    ).build_url(width=250, height=250, crop="fill", version=r.get("version"))

    photo = await repository_photos.upload_photo(current_user.id, src_url, body, tags, db)
    return {"photo": photo, "detail": "Photo has been upload successfully"}


@router.get("/{photo_id}", response_model=PhotoDb)
async def get_photo_by_id(
        photo_id: int,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)):
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED)
    photo = await repository_photos.get_photo(photo_id, db)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    return photo

  
@router.delete("/delete/{photo_id}", response_model=PhotoDb, dependencies=[Depends(allowed_remove_photo)])
async def remove_photo(
        photo_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)):
    photo = await repository_photos.remove_photo(photo_id, current_user, db)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    return photo


@router.put("/update/{photo_id}", response_model=PhotoDb, dependencies=([Depends(allowed_update_photo)]))
async def update_photo_description(
        body: PhotoModel,
        photo_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)):

    photo = await repository_photos.update_description(photo_id, body, current_user, db)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    return photo
