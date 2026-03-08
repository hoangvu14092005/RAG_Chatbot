import redis.asyncio as redis
import json
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, messages_to_dict, messages_from_dict

class SimpleRedisHistory(BaseChatMessageHistory):
    def __init__(self, session_id: str, redis_url: str, ttl: int = 3600):
        self.session_id = session_id
        self.r = redis.from_url(redis_url, decode_responses=True)
        self.ttl = ttl # Thời gian sống của cache (1 giờ)

    async def add_message(self, message: BaseMessage) -> None:
        key = f"history:{self.session_id}"
        msg_dict = messages_to_dict([message])[0]
        await self.r.rpush(key, json.dumps(msg_dict))
        await self.r.expire(key, self.ttl)

    async def get_messages(self, limit: int = 5) -> list[BaseMessage]:
        key = f"history:{self.session_id}"
        # Lấy N tin nhắn gần nhất để không làm tràn context window của LLM
        raw = [json.loads(m) for m in await self.r.lrange(key, -limit, -1)]
        return messages_from_dict(raw)

    async def clear(self) -> None:
        await self.r.delete(f"history:{self.session_id}")