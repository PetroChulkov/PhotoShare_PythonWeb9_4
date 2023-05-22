import calendar
import time

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Form,
)
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
from src.database.connect import get_db
from src.database.models import User, Role
from src.schemas.comments import CommentModel, EditCommentModel, CommentDb

from src.repository import photos as repository_photos
from src.repository import comments as repository_comments
from src.services.auth import auth_service
from src.services.roles import RolesChecker

current_GMT = time.gmtime()
time_stamp = calendar.timegm(current_GMT)

router = APIRouter(prefix="/comments", tags=["comments"])

allowed_post_comment = RolesChecker([Role.admin, Role.moderator, Role.user])
allowed_remove_comment = RolesChecker([Role.admin, Role.moderator])
allowed_update_comment = RolesChecker([Role.admin, Role.moderator, Role.user])


@router.post(
    "/add_comment",
    name="add comment",
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(allowed_post_comment),
        Depends(RateLimiter(times=2, seconds=5)),
    ],
)
async def add_comment(
    body: CommentModel,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    photo = await repository_photos.get_photo(body.photo_id, db)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Such photo is not exist in db",
        )
    comment = await repository_comments.create_comment(current_user.id, body, db)
    return {"comment": comment, "detail": "Comment was added successfully"}


@router.put(
    "/{comment_id}",
    response_model=CommentDb,
    dependencies=([Depends(allowed_update_comment)]),
)
async def edit_comment(
    body: EditCommentModel,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    check_comment = await repository_comments.get_comment(body.comment_id, db)
    if not check_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Such comment is not exist in db",
        )
    if check_comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can edit only own comments",
        )
    comment = await repository_comments.update_comment(body, db)
    return comment


@router.delete(
    "/{comment_id}", dependencies=([Depends(allowed_remove_comment)])
)
async def remove_comment_sw(
    body: int = Form(),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    check_comment = await repository_comments.get_comment(body, db)
    if not check_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Such comment is not exist in db",
        )
    await repository_comments.remove_comment(body, db)
    return {"detail": "Comment was removed successfully"}
