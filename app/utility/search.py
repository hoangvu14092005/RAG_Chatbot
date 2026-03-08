import psycopg
from pgvector.psycopg import register_vector
import numpy as np
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.config import Config
from app.core.model import Chunk
from app.utility.doc_processor import DocProcessor
import logging

logger = logging.getLogger(__name__)
doc_processor = DocProcessor()

class SearchServices:
    def __init__(self):
        self.db_url = Config.PSYCOPG_CONNECT

    async def get_content_by_chunk_id(self, chunks_id: list, session: AsyncSession) -> str:
        """Truy xuất nội dung text từ danh sách ID của Chunk"""
        statement = select(Chunk).where(Chunk.id.in_(chunks_id))
        results = await session.exec(statement)
        contents = [chunk.content for chunk in results]
        return "\n\n".join(contents)

    async def search_context(self, query: str, session: AsyncSession, top_k: int = 4) -> str:
        """Tìm kiếm Top K Chunk có vector gần giống với câu hỏi nhất"""
        try:
            # 1. Mã hóa câu hỏi thành Vector
            vector = doc_processor.encode(texts=query)
            np_vector = np.array(vector, dtype=np.float32)

            # 2. Query DB bằng pgvector (Toán tử <=> là Cosine Distance)
            with psycopg.connect(self.db_url, autocommit=True) as conn:
                register_vector(conn) # Đăng ký kiểu vector cho psycopg
                cur = conn.cursor()
                
                # Bảng của bạn là embedding, cột vector
                cur.execute(
                    f"""
                    SELECT chunk_id FROM embedding 
                    ORDER BY vector <=> %s 
                    LIMIT {top_k}
                    """,
                    (np_vector,),
                )
                results = cur.fetchall()
            
            if not results:
                return ""

            # 3. Lấy UUID của các Chunk
            chunk_ids = [row[0] for row in results]
            
            # 4. Lấy nội dung text tương ứng
            context = await self.get_content_by_chunk_id(chunk_ids, session)
            return context

        except Exception as e:
            logger.error(f"Vector search failed: {str(e)}")
            return ""