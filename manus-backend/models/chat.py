from datetime import datetime, timezone
import uuid

class Chat:
    def __init__(self, id: str = None, title: str = None, created_at: datetime = None, updated_at: datetime = None):
        self.id = id or str(uuid.uuid4())
        self.title = title
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }