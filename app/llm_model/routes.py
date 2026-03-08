from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from typing import Annotated
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.session import get_session
from app.auth.dependency import get_current_user
from app.core.model import User
from app.llm_model.services import generate_response

conversation_router = APIRouter()
SessionDep = Annotated[AsyncSession, Depends(get_session)]

@conversation_router.post("/ask")
async def chat_endpoint(
    question: str, 
    session: SessionDep,
    user: Annotated[User, Depends(get_current_user)] # Bảo mật API bằng token
):
    # Gọi service sinh câu trả lời
    event_stream = await generate_response(query=question, session=session)
    
    # Trả về dạng Streaming (text/plain cho đơn giản)
    return StreamingResponse(event_stream(), media_type="text/plain")

@conversation_router.post("/ask/{chat_id}")
async def chat_endpoint(
    chat_id: str, 
    question: str, 
    session: SessionDep,
    user: Annotated[User, Depends(get_current_user)]
):
    event_stream = await generate_response(query=question, chat_id=chat_id, session=session)
    return StreamingResponse(event_stream(), media_type="text/plain")