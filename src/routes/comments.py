from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from src.database.connect import get_db
from src.schemas import CommentModel, CommentResponse
from src.repository import comments as repository_comments

router = APIRouter(prefix='/comments', tags=["comment"])


@router.get("/{comment_id}", response_model=CommentResponse)
async def read_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = await repository_comments.get_comment(comment_id, db)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment


@router.post("/", response_model=CommentResponse)
async def create_comment(body: CommentModel, db: Session = Depends(get_db)):
    return await repository_comments.create_comment(body, db)


@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(body: CommentModel, comment_id: int, db: Session = Depends(get_db)):
    comment = await repository_comments.update_comment(comment_id, body, db)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment


@router.delete("/{comment_id}", response_model=CommentResponse)
async def remove_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = await repository_comments.remove_comment(comment_id, db)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment
