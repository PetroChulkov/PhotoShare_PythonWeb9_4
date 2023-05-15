from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, EmailStr, FilePath

from src.database.models import Role


class UserModel(BaseModel):
    user_name: str = Field()
    email: EmailStr
    password: str = Field()


class UserDb(BaseModel):
    id: int
    user_name: str
    email: str

    class Config:
        orm_mode = True


class DescriptionUpdate(BaseModel):
    done: bool


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User was created successfully"


class PhotoModel(BaseModel):
    description: str


class PhotoDb(BaseModel):
    id: int
    photo: str
    description: str | None

    class Config:
        orm_mode = True


class PhotoResponse(BaseModel):
    photo: PhotoDb
    detail: str = "Photo was created successfully"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr


class ForgotPasswordModel(BaseModel):
    email: str


class ResetPasswordModel(BaseModel):
    email: EmailStr
    reset_password_token: str
    password: str
    confirm_password: str


class CommentModel(BaseModel):
    id: int
    comment: str = Field(max_length=100)


class CommentResponse(CommentModel):
    id: int

    class Config:
        orm_mode = True
