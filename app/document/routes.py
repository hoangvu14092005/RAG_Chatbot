from fastapi import APIRouter, UploadFile, Depends
from typing import Annotated
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.session import get_session
from app.auth.dependency import get_current_user
from app.core.model import User
from app.document.services import DocumentServices

document_router = APIRouter()
document_services = DocumentServices()
SessionDep = Annotated[AsyncSession, Depends(get_session)]

@document_router.post("/")
async def upload_file(
    file: UploadFile,
    kb_id: str, # ID của Knowledge Base bạn muốn nhét file vào
    user: Annotated[User, Depends(get_current_user)], # chèn dependency get_current_user để bắt buộc người dùng phải gửi kèm token mới được upload file.
    session: SessionDep,
):
    uploaded_file = await document_services.upload_document(
        file=file, kb_id=kb_id, user=user, session=session
    )
    return {"message": "Upload thành công", "document_id": uploaded_file.id}