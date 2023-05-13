import cloudinary
import cloudinary.uploader
from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, Path, UploadFile, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.connect import get_db
from src.database.models import User, Role
from src.schemas import UserModel, UserResponse, UserDb

# UpdateContactRoleModel
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.roles import RolesChecker
from src.conf.config import settings

router = APIRouter(prefix="/users", tags=["users"])

allowed_get_users = RolesChecker([Role.admin, Role.moderator, Role.user])
allowed_create_users = RolesChecker([Role.admin, Role.moderator, Role.user])
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
    check_mail = repository_users.check_exist_mail(body, db)
    if check_mail:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Such mail already registered",
        )
    body.password = auth_service.get_password_hash(body.password)
    user = await repository_users.create_user(body, db)
    return {"user": user, "detail": "User was created"}
