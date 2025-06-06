from datetime import datetime, timezone
import uuid

class Chunk:
    def __init__(self, id: str = None, document_id: str = None, chunk_index: int = None,
                 content: str = None, token_count: int = None, start_char_index: int = None,
                 end_char_index: int = None, vector_id: str = None,
                 created_at: datetime = None, updated_at: datetime = None):
        self.id = id or str(uuid.uuid4())
        self.document_id = document_id
        self.chunk_index = chunk_index
        self.content = content
        self.token_count = token_count
        self.start_char_index = start_char_index
        self.end_char_index = end_char_index
        self.vector_id = vector_id
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "document_id": self.document_id,
            "chunk_index": self.chunk_index,
            "content": self.content,
            "token_count": self.token_count,
            "start_char_index": self.start_char_index,
            "end_char_index": self.end_char_index,
            "vector_id": self.vector_id,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }