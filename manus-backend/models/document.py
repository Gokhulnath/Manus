from datetime import datetime, timezone
import uuid

class Document:
    def __init__(self, id: str = None, filename: str = None,
                 file_path: str = None, file_type: str = None,
                 file_hash: str = None, total_chunks: int = 0,
                 created_at: datetime = None, updated_at: datetime = None):
        self.id = id or str(uuid.uuid4())
        self.filename = filename
        self.file_path = file_path
        self.file_type = file_type
        self.file_hash = file_hash
        self.total_chunks = total_chunks
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "filename": self.filename,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "file_hash": self.file_hash,
            "total_chunks": self.total_chunks,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }