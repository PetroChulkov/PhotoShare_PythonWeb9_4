from sqlalchemy.orm import Session

from src.database.models import Comment, Photo
from src.schemas import CommentModel


async def get_comment(comment_id: int, db: Session) -> Comment | None:
    return db.query(Comment).filter(Comment.id == comment_id).first()


async def create_comment(body: CommentModel, db: Session) -> Comment:
    photo = db.query(Photo).filter(Photo.id(body.comment)).all()
    comment = Comment(name=body.id, photo=photo)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


async def update_comment(comment_id: int, body: CommentModel, db: Session) -> Comment | None:
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment:
        comment .name = body.comment
        db.commit()
    return comment


async def remove_comment(comment_id: int, db: Session) -> Comment | None:
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment:
        db.delete(comment)
        db.commit()
    return comment
