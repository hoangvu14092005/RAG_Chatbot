import jwt
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.session import get_session
from app.config import Config
from app.core.model import User

oauth_scheme = OAuth2PasswordBearer(tokenUrl=f"/{Config.VERSION}/oauth/login")

async def get_current_user(
    token: Annotated[str, Depends(oauth_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Giải mã token
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
        user_email = payload.get("user", {}).get("email")
        if user_email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    # Tìm user trong DB
    statement = select(User).where(User.email == user_email)
    result = await session.exec(statement)
    user = result.first()

    if user is None:
        raise credentials_exception

    return user