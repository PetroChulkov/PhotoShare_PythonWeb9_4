from datetime import date

from pydantic import BaseModel, Field, EmailStr


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


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User was created successfully"


class UserPublic(BaseModel):
    user_name: str
    created_at: date
    photos_published: int

    class Config:
        orm_mode = True


class UserResponseProfile(BaseModel):
    username: str
    email: EmailStr
    created_at: date
    photos_published: int

    class Config:
        orm_mode = True


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
