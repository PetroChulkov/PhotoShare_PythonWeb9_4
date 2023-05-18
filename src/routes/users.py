import cloudinary
import cloudinary.uploader
from typing import List
from fastapi import (
    APIRouter,
    Form,
    Depends,
    File,
    HTTPException,
    Path,
    UploadFile,
    status,
)
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.connect import get_db
from src.database.models import User, Role
from src.schemas import UserModel, UserResponse, UserDb, UserPublic, UserResponseProfile, ChangePasswordRequest

# UpdateContactRoleModel
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.roles import RolesChecker
from src.conf.config import settings

router = APIRouter(prefix="/users", tags=["users"])

allowed_get_users = RolesChecker([Role.admin, Role.moderator, Role.user])
allowed_create_users = RolesChecker([Role.admin, Role.moderator, Role.user])
allowed_ban_users = RolesChecker([Role.admin])


# allowed_get_contact_by_id = RolesChecker([Role.admin, Role.moderator, Role.user])
# allowed_update_contact = RolesChecker([Role.admin, Role.moderator])
# allowed_change_contact_role = RolesChecker([Role.admin, Role.moderator])
# allowed_delete_contact = RolesChecker([Role.admin])
# allowed_search_first_name = RolesChecker([Role.admin, Role.moderator, Role.user])
# allowed_search_last_name = RolesChecker([Role.admin, Role.moderator, Role.user])
# allowed_search_email = RolesChecker([Role.admin, Role.moderator, Role.user])
# allowed_search = RolesChecker([Role.admin, Role.moderator, Role.user])


@router.post(
    "/create",
    response_model=UserResponse,
    name="Create user",
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(allowed_create_users),
        Depends(RateLimiter(times=2, seconds=5)),
    ],
)
async def create_user(body: UserModel, db: Session = Depends(get_db)):
    check_mail = await repository_users.check_exist_mail(body, db)
    if check_mail:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Such mail already registered",
        )
    check_username = await repository_users.check_exist_username(body, db)
    if check_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Such username already registered",
        )
    body.password = auth_service.get_password_hash(body.password)
    user = await repository_users.create_user(body, db)
    return {"user": user, "detail": "User was created"}


@router.patch(
    "/ban_user/{user_id}",
    name="Ban user",
    response_model=UserResponse,
    dependencies=[
        Depends(allowed_ban_users),
        Depends(RateLimiter(times=2, seconds=5)),
    ],
)
async def ban_user(email: str = Form(), db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_email(email, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Such user is not found",
        )
    user = await repository_users.to_ban_user(user, email, db)
    return {"user": user, "detail": "User was banned"}


@router.get("/profile/{searched_user}", response_model=UserPublic)
async def get_user_profile(
        searched_user: str,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)):
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED)
    user = await repository_users.get_user_profile(searched_user, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    return user


@router.get("/me", response_model=UserResponseProfile)
async def get_me(current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    photos_published = await repository_users.get_amount_photos(current_user.user_name, db)
    user_profile = UserResponseProfile(username=current_user.user_name, email=current_user.email,
                                       created_at=current_user.created_at,
                                       photos_published=photos_published)
    return user_profile


@router.put("/me/change_password")
async def change_password(request: ChangePasswordRequest,
                          current_user: User = Depends(auth_service.get_current_user),
                          db: Session = Depends(get_db)):
    if not auth_service.verify_password(request.old_password, current_user.password):
        raise HTTPException(status_code=400, detail="Invalid old password")
    new_password = auth_service.get_password_hash(request.new_password)
    await repository_users.change_password(current_user, new_password, db)
    return {"message": "Password updated successfully"}
