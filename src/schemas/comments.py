from pydantic import BaseModel


class CommentModel(BaseModel):
    comment: str
    photo_id: int


class EditCommentModel(BaseModel):
    comment_id: int
    edited_comment: str


class CommentDb(BaseModel):
    id: int
    comment: str

    class Config:
        orm_mode = True


class CommentResponseModel(CommentDb):
    comment: CommentDb
    detail: str = "Comment was edited successfully"
