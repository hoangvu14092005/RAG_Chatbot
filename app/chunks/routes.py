from fastapi import APIRouter, Depends
from typing import Annotated
from app.core.session import get_session
from app.auth.dependency import get_current_user
from app.core.model import User
from sqlmodel.ext.asyncio.session import AsyncSession
from app.chunks.services import RAGPipelineService

chunks_router = APIRouter()
chunks_service = RAGPipelineService()

SessionDep = Annotated[AsyncSession, Depends(get_session)]

@chunks_router.post("/chunking/{document_id}")
async def do_chunking(
    document_id: str,
    user: Annotated[User, Depends(get_current_user)],
    session: SessionDep
):
    return await chunks_service.process_chunking(document_id, user, session)


@chunks_router.post("/embedding/{document_id}")
async def do_embedding(
    document_id: str,
    user: Annotated[User, Depends(get_current_user)],
    session: SessionDep
):
    return await chunks_service.process_embedding(document_id, user, session)