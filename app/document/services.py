import hashlib
from pathlib import Path
from io import BytesIO
from fastapi import UploadFile
from sqlmodel.ext.asyncio.session import AsyncSession

from app.document.schema import CreateDocumentDB
from app.core.minio import get_minio_client, init_minio
from app.config import Config
from app.core.model import Document, User

class DocumentServices:
    async def upload_document(
        self, file: UploadFile, kb_id: str, user: User, session: AsyncSession
    ):
        """Bước 1: Đọc và tính toán metadata của file"""
        content = await file.read()
        file_size = len(content)
        file_hash = hashlib.sha256(content).hexdigest()

        # Làm sạch tên file
        file_name = "".join(
            c for c in file.filename if c.isalnum() or c in ("-", "_", ".")
        ).strip()
        path = Path(file_name)
        object_path = f"tmp/{path.stem}_{file_hash}{path.suffix.lower()}"

        """Bước 2: Upload lên MinIO"""
        init_minio() # Đảm bảo bucket đã tồn tại
        minio_client = get_minio_client()
        
        minio_client.put_object(
            bucket_name=Config.BUCKET_NAME,
            object_name=object_path,
            data=BytesIO(content),
            length=file_size,
            content_type=file.content_type,
        )

        """Bước 3: Lưu Database"""
        new_doc_base = CreateDocumentDB(
            object_path=object_path,
            file_name=file_name,
            file_size=file_size,
            content_type=file.content_type,
            file_hash=file_hash,
            username=user.username, # Gắn với user đang đăng nhập
            knowledge_base_id=kb_id,
        )

        new_doc = Document(**new_doc_base.model_dump())
        session.add(new_doc)
        await session.commit()
        await session.refresh(new_doc)
        
        return new_doc