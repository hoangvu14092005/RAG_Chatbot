from minio import Minio
from app.config import Config

def get_minio_client() -> Minio:
    """Khởi tạo MinIO client"""
    return Minio(
        endpoint=Config.MINIO_URL,
        access_key=Config.MINIO_ACCESS_KEY,
        secret_key=Config.MINIO_SECRET_KEY,
        secure=False # Dùng HTTP ở local
    )

def init_minio():
    """Tạo bucket nếu chưa tồn tại"""
    client = get_minio_client()
    found = client.bucket_exists(Config.BUCKET_NAME)
    if not found:
        client.make_bucket(Config.BUCKET_NAME)