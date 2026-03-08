import tempfile
from pathlib import Path
from sqlmodel import insert, select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException
from app.core.model import Document, Chunk, Embedding
from app.core.minio import get_minio_client
from app.config import Config
from app.utility.doc_processor import DocProcessor
from app.core.model import User

doc_processor = DocProcessor()

class RAGPipelineService:

    async def process_chunking(self, document_id: str, user: User, session: AsyncSession):

        doc = await session.get(Document, document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Doc not found")

        minio_client = get_minio_client()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp_file:
            minio_client.fget_object(Config.BUCKET_NAME, doc.object_path, tmp_file.name)
            tmp_path = tmp_file.name

        try:
            with open(tmp_path, "r", encoding="utf-8") as f:
                content = f.read()

            chunks_text = doc_processor.split_text(content)

            chunk_objects = [
                Chunk(
                    document_id=doc.id,
                    username=user.username,
                    content=text
                )
                for text in chunks_text if text.strip()
            ]

            session.add_all(chunk_objects)
            doc.status = "chunking"

            await session.commit()

            return {"message": f"Tạo thành công {len(chunk_objects)} chunks"}

        finally:
            if Path(tmp_path).exists():
                Path(tmp_path).unlink()


    async def process_embedding(self, document_id: str, user: User, session: AsyncSession):

        statement = select(Chunk).where(Chunk.document_id == document_id)
        chunks = (await session.exec(statement)).all()

        if not chunks:
            raise HTTPException(status_code=400, detail="Document chưa được chunking")

        texts = [chunk.content for chunk in chunks]

        vectors = doc_processor.encode(texts)

        for chunk, vector in zip(chunks, vectors):
            new_embedding = Embedding(
                username=user.username,
                chunk_id=chunk.id,
                document_id=document_id,
                vector=vector
            )
            session.add(new_embedding)

        doc = await session.get(Document, document_id)
        doc.status = "embedding"

        await session.commit()

        return {"message": f"Đã mã hóa vector cho {len(chunks)} chunks"}