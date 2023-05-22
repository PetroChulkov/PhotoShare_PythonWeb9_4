import calendar
import time
from typing import List

import cloudinary
import cloudinary.uploader
from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
    Form,
    Query,
)
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.connect import get_db
from src.database.models import User, Role
from src.schemas.photos import PhotoModel, PhotoDb, PhotoResponse, PhotoSearch
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


@router.get(
    "/",
    response_model=List[PhotoResponse],
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def get_photos(
    limit: int = Query(10, le=100),
    offset: int = 0,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    photos = await repository_photos.get_all_photos(limit, offset, db)
    return photos


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
    effects: str = Query(
        None,
        enum=[
            "grayscale",
            "sepia",
            "vignette",
            "cartoonify",
            "blur",
            "art:athena",
            "art:eucalyptus",
            "art:frost",
            "art:zorro",
            "art:sizzle",
        ],
    ),
    round_image: str = Query(None, enum=["yes"]),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    if round_image:
        radius = "max"
    else:
        radius = None

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
    ).build_url(
        width=500,
        height=500,
        crop="fill",
        effect=effects,
        radius=radius,
        fetch_format="auto",
        version=r.get("version"),
    )

    photo = await repository_photos.upload_photo(
        current_user.id, src_url, body, tags, db
    )
    return {"photo": photo, "detail": "Photo has been upload successfully"}


@router.get("/{photo_id}", response_model=PhotoDb)
async def get_photo_by_id(
    photo_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    photo = await repository_photos.get_photo(photo_id, db)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    return photo


@router.delete(
    "/{photo_id}",
    response_model=PhotoDb,
    dependencies=[Depends(allowed_remove_photo)],
)
async def remove_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    photo = await repository_photos.remove_photo(photo_id, current_user, db)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    return photo


@router.put(
    "/{photo_id}",
    response_model=PhotoDb,
    dependencies=([Depends(allowed_update_photo)]),
)
async def update_photo_description(
    body: PhotoModel,
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    photo = await repository_photos.update_description(photo_id, body, current_user, db)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    return photo


@router.post(
    "/get_qr_code/{photo_id}", response_model=PhotoDb, name="Get QR code for photo"
)
async def get_qr_code(
    photo_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    photo = await repository_photos.get_photo(photo_id, db)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    qr_code = await repository_photos.create_qr_code(
        photo_id, photo.photo, current_user, db
    )
    return qr_code


@router.get("/search_keyword/", name="Search photos by keyword", response_model=List[PhotoSearch])
async def search_photo_by_keyword(
    search_by: str,
    filter_by: str = Query(None, enum=["rating", "created_at"]),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    if search_by:
        photo = await repository_photos.search_photo_by_keyword(search_by, filter_by, db)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    return photo


@router.get("/search_tag/", name="Search photos by tag", response_model=List[PhotoSearch])
async def search_photo_by_tag(
    search_by: str,
    filter_by: str = Query(None, enum=["rating", "created_at"]),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    if search_by:
        photo = await repository_photos.search_photo_by_tag(
            search_by, filter_by, db)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    return photo
