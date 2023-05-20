import uuid
from typing import List


from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Security,
    BackgroundTasks,
    Request,
)
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from fastapi_limiter.depends import RateLimiter

from sqlalchemy.orm import Session

from src.database.connect import get_db
from src.schemas import (
    UserModel,
    UserResponse,
    UserDb,
    TokenModel,
    RequestEmail,
    ResetPasswordModel,
)

from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.email import send_email, send_email_reset_password_token


router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(
    body: UserModel,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    exist_user = await repository_users.search_by_mail(body.email, db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )
    check_username = await repository_users.check_exist_username(body, db)
    if check_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Such username already registered",
        )
    body.password = auth_service.get_password_hash(body.password)
    user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, user.email, user.user_name, request.base_url)
    return {"user": user, "detail": "User successfully created"}


@router.post("/login", response_model=TokenModel)
async def login(
    body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = await repository_users.search_by_mail(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email"
        )
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed"
        )
    user_status = await repository_users.check_ban_status(body.username, db)
    if user_status == True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Your account is banned"
        )
    # Generate JWT
    access_token = await auth_service.create_access_token(
        data={"sub": user.email}, expires_delta=7200
    )
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/refresh_token", response_model=TokenModel)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.search_by_mail(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    contact = await repository_users.search_by_mail(body.email, db)

    if contact.confirmed:
        return {"message": "Your email is already confirmed."}
    if contact:
        background_tasks.add_task(
            send_email, contact.email, contact.user_name, request.base_url
        )
    return {"message": "Check your email for confirmation."}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    email = await auth_service.get_email_from_token(token)
    contact = await repository_users.search_by_mail(email, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if contact.confirmed:
        return {"message": "Your e-mail is already confirmed."}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.get(
    "/forgot_password",
    name="Forgot password",
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def forgot_password(
    email: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    user = await repository_users.search_by_mail(email, db)
    if bool(user) == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found or doesn't exist."
        )
    reset_password_token = uuid.uuid1()
    background_tasks.add_task(
        send_email_reset_password_token,
        reset_password_token,
        user.email,
        user.user_name,
    )

    user.reset_password_token = reset_password_token
    db.commit()

    return {
        "message": f"Reset password token has been sent to your e-email.{reset_password_token}"
    }


@router.patch(
    "/reset_password",
    name="Reset password",
    response_model=UserDb,
    dependencies=[
        Depends(RateLimiter(times=2, seconds=5)),
    ],
)
async def reset_password(
    body: ResetPasswordModel,
    db: Session = Depends(get_db),
):
    user = await repository_users.search_by_mail(body.email, db)
    if bool(user) == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found or doesn't exist."
        )

    if body.reset_password_token != user.reset_password_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Password reset tokens doesn't match.",
        )

    if body.password != body.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="New password is not match."
        )

    body.password = auth_service.get_password_hash(body.password)
    user.password = body.password
    user.reset_password_token = None
    db.commit()

    return user
