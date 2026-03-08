from pydantic import BaseModel
from uuid import UUID

class UploadDocument(BaseModel):
    object_path: str
    file_name: str
    file_size: int
    content_type: str
    file_hash: str

class CreateDocumentDB(UploadDocument):
    username: str
    knowledge_base_id: UUID