from pydantic import BaseModel, Field, EmailStr

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


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User was created successfully"


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
