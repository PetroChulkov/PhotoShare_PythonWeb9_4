from sqlalchemy.orm import Session

from src.database.models import Comment
from src.schemas.comments import CommentModel, EditCommentModel


async def create_comment(user_id: int, body: CommentModel, db: Session) -> Comment:
    comment = Comment(comment=body.comment, photo_id=body.photo_id, user_id=user_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


async def get_comment(comment_id: int, db: Session) -> Comment | None:
    return db.query(Comment).filter(Comment.id == comment_id).first()


async def update_comment(body: EditCommentModel, db: Session) -> Comment | None:
    comment = db.query(Comment).filter(Comment.id == body.comment_id).first()
    if comment:
        comment.comment = body.edited_comment
        db.commit()
    return comment


async def remove_comment(comment_id: int, db: Session) -> None:
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment:
        db.delete(comment)
        db.commit()
