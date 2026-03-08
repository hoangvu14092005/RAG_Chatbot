from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from sqlmodel.ext.asyncio.session import AsyncSession
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.utility.chat_history import SimpleRedisHistory
from app.core.model import Message

from app.config import Config
from app.utility.search import SearchServices
import re

search_services = SearchServices()

# Khởi tạo kết nối với Ollama Local
llm = ChatOllama(
    model=Config.LLM_MODEL,
    base_url=Config.OLLAMA_HOST,
    temperature=0.1,
    verbose=True,
)

def clean_think_tags(text: str) -> str:
    """Xóa các tag suy nghĩ <think> nếu dùng model DeepSeek (tùy chọn)"""
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

async def generate_response(query: str, session: AsyncSession):
    # Tìm kiếm tài liệu liên quan (Context)
    context = await search_services.search_context(query=query, session=session)

    # Thiết lập Prompt Template
    system_prompt = (
        "Bạn là một trợ lý AI chuyên nghiệp và tận tâm. "
        "Dựa trên dữ liệu tham khảo được cung cấp bên dưới, hãy trả lời câu hỏi của người dùng một cách chính xác bằng tiếng Việt.\n"
        "Nếu dữ liệu tham khảo không chứa thông tin để trả lời, hãy nói rằng bạn không biết, đừng bịaa ra thông tin.\n\n"
        "Dữ liệu tham khảo:\n{context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Câu hỏi: {input}")
    ])

    # Tạo chuỗi xử lý (Chain)
    chain = prompt | llm

    # Hàm Generator để Stream dữ liệu trả về từng chữ (SSE)
    async def event_stream():
        inputs = {
            "input": query,
            "context": context,
        }
        
        full_response = ""
        # Dùng astream để lấy dữ liệu từng phần tử (chunk) trả về từ LLM
        async for chunk in chain.astream(inputs):
            text = chunk.content
            if text:
                full_response += text
                yield text # Bắn từng chữ về cho client
                
        # (Ở Giai đoạn 6, chúng ta sẽ lưu full_response này vào DB ở đây)

    return event_stream

async def generate_response(query: str, chat_id: str, session: AsyncSession):
    # 1. Khởi tạo kết nối Redis History
    history_service = SimpleRedisHistory(
        session_id=chat_id, redis_url=Config.REDIS_URL
    )
    
    # 2. Lưu tin nhắn của User vào DB và Redis
    user_msg = Message(content=query, role="user", chat_id=chat_id)
    session.add(user_msg)
    await session.commit()
    await history_service.add_message(HumanMessage(content=query))

    # 3. Lấy lịch sử chat (3-5 tin nhắn gần nhất)
    messages = await history_service.get_messages(limit=4)
    chat_history = [(m.type, m.content) for m in messages]

    # 4. Tìm Context từ Vector DB
    context = await search_services.search_context(query=query, session=session)

    # 5. Cập nhật Prompt Template hỗ trợ Lịch sử
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Bạn là trợ lý AI. Dựa trên dữ liệu tham khảo, hãy trả lời bằng tiếng Việt.\n\nDữ liệu tham khảo:\n{context}"),
        MessagesPlaceholder("chat_history"), # Chèn lịch sử chat vào đây
        ("human", "Câu hỏi: {input}")
    ])

    chain = prompt | llm

    async def event_stream():
        inputs = {
            "chat_history": chat_history,
            "input": query,
            "context": context,
        }
        
        full_response = ""
        async for chunk in chain.astream(inputs):
            if chunk.content:
                full_response += chunk.content
                yield chunk.content
                
        # 6. Sau khi stream xong, lưu câu trả lời của Bot vào DB và Redis
        bot_msg = Message(content=full_response, role="bot", chat_id=chat_id)
        session.add(bot_msg)
        await session.commit()
        await history_service.add_message(AIMessage(content=full_response))

    return event_stream