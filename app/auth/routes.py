from fastapi import APIRouter, status, Depends, HTTPException
from typing import Annotated
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.auth.schema import CreateUserModel, TokenModel, UserLoginModel, UserModel
from app.core.session import get_session
from app.core.model import User
from app.utility.security import get_hashed_password, verify_password, create_access_token
from app.auth.dependency import get_current_user
from app.celery_task import send_email

oauth_router = APIRouter()
SessionDep = Annotated[AsyncSession, Depends(get_session)]

@oauth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user(user_data: CreateUserModel, session: SessionDep):
    # Kiểm tra email tồn tại chưa
    existing_user = await session.exec(select(User).where(User.email == user_data.email))
    if existing_user.first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Tạo user mới với is_verified = True (Tạm thời bỏ qua Celery gửi mail)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_hashed_password(user_data.password),
        is_verified=True,
        role="user"
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    html_content = f"<h1>Chào {user_data.username}</h1><p>Cảm ơn bạn đã đăng ký!</p>"
    send_email.delay([user_data.email], "Xác thực tài khoản", html_content)

    return {"message": "Account created! Check email to verify."}

@oauth_router.post("/login", response_model=TokenModel)
async def login(login_data: UserLoginModel, session: SessionDep):
    # Tìm user
    result = await session.exec(select(User).where(User.email == login_data.email))
    user = result.first()

    # Kiểm tra mật khẩu
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    # Tạo token
    access_token = create_access_token(
        user_data={"email": user.email, "user_id": str(user.id), "role": user.role}
    )
    return TokenModel(access_token=access_token)

@oauth_router.get("/me", response_model=UserModel)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    """API này bị khóa, chỉ có token hợp lệ mới vào được"""
    return current_user

