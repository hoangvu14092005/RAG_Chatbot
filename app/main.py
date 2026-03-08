from fastapi import FastAPI
from app.config import Config
from app.auth.routes import oauth_router
from app.document.routes import document_router
from app.chunks.routes import chunks_router
from app.llm_model.routes import conversation_router

app = FastAPI(title="RAG Chatbot Backend")

@app.get(f"/{Config.VERSION}/health", tags=["Health"])
async def health_check():
    return {"status": "Database and Server are ready!"}

app.include_router(
    oauth_router,
    prefix=f"/{Config.VERSION}/auth",
    tags=["Authentication"]
)

app.include_router(
    document_router,
    prefix=f"/{Config.VERSION}/documents",
    tags=["Documents"]
)

app.include_router(
    chunks_router,
    prefix=f"/{Config.VERSION}/chunking",
    tags=["chunking"]
)

app.include_router(
    conversation_router,
    prefix=f"/{Config.VERSION}/conversation",       
    tags=["conversation"]
)