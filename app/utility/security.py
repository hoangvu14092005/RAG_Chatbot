from passlib.context import CryptContext
from datetime import timedelta, timezone, datetime
import jwt
from app.config import Config

# Sử dụng bcrypt thay vì sha512_crypt cho chuẩn hiện đại
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password: str) -> str:
    """Băm mật khẩu trước khi lưu vào DB"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kiểm tra mật khẩu người dùng nhập có khớp với DB không"""
    # plain_password la mk goc
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_data: dict, expire_delta: timedelta | None = None):
    """Tạo JWT Token"""
    payload = {"user": user_data} # thong tin nguoi dung
    if expire_delta:
        expire = datetime.now(timezone.utc) + expire_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload.update({"exp": expire})
    token = jwt.encode(
        payload=payload, key=Config.SECRET_KEY, algorithm=Config.ALGORITHM
    )
    return token