from sqlmodel import SQLModel, Field, Column, Relationship
from sqlalchemy import DateTime, func, column, Column, text 
from typing import Optional, List, Optional, Any
from uuid import UUID, uuid4
from datetime import datetime
from pgvector.sqlalchemy import Vector


class User(SQLModel, table=True):
    __tablename__ = "user"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True)
    hashed_password: str = Field(exclude=True) 
    is_verified: bool = Field(default=False)
    role: str = Field(default="user", max_length=32)
    
    # Tự động cập nhật thời gian
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )


class KnowledgeBase(SQLModel, table=True):
    __tablename__ = "knowledge_base"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=1024)
    username: str = Field(nullable=False) # Gắn với người tạo
    
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    
    documents: list["Document"] = Relationship(back_populates="knowledge_base", cascade_delete=True)

class Document(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(nullable=False)
    knowledge_base_id: UUID = Field(foreign_key="knowledge_base.id", nullable=False)
    
    object_path: str = Field(max_length=255) # Đường dẫn file trên MinIO
    file_name: str = Field(max_length=255)
    file_size: int = Field(nullable=False)
    content_type: str = Field(max_length=128)
    file_hash: str = Field(index=True, max_length=64) # Hash để tránh trùng lặp
    status: str = Field(default="pending") # Trạng thái: pending, chunking, embedding
    
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    
    knowledge_base: Optional["KnowledgeBase"] = Relationship(back_populates="documents")

class Chunk(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(nullable=False)
    document_id: UUID = Field(foreign_key="document.id", nullable=False)
    content: str = Field(max_length=1024, index=True) # Lưu nội dung text đã băm
    
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    
    embedding: Optional["Embedding"] = Relationship(back_populates="chunk", cascade_delete=True)

class Embedding(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(nullable=False)
    chunk_id: UUID = Field(foreign_key="chunk.id", nullable=False, index=True)
    document_id: UUID = Field(foreign_key="document.id", nullable=False)
    
    # Cột quan trọng nhất: Lưu mảng float 384 hoặc 768 chiều tùy model
    vector: Any | None = Field(sa_column=Column(Vector(768))) 
    
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    
    chunk: Optional["Chunk"] = Relationship(back_populates="embedding")

class Chat(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(nullable=False)
    
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    
    messages: list["Message"] = Relationship(back_populates="chat", cascade_delete=True)

class Message(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    content: str | None = Field(sa_column=sa.Column(Text, nullable=False))
    role: str = Field(max_length=32, nullable=False) # 'user' hoặc 'bot'
    chat_id: UUID = Field(foreign_key="chat.id", nullable=False)
    
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    
    chat: Optional["Chat"] = Relationship(back_populates="messages")