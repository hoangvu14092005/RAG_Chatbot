from fastapi import FastAPI
from app.config import Config

app = FastAPI(title="RAG Chatbot Backend")

@app.get(f"/{Config.VERSION}/health", tags=["Health"])
async def health_check():
    return {"status": "Database and Server are ready!"}