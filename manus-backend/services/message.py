from typing import List, Optional
from supabase import Client
from datetime import datetime, timezone
import uuid
from schemas.message import (
    MessageCreate,
    MessageUpdate,
    MessageResponse
)
from models.message import Message


class MessageService:
    def __init__(self, db: Client):
        self.db = db
        self.table_name = "messages"

    async def create_message(self, message_data: MessageCreate) -> MessageResponse:
        """Create a new message."""
        message = Message(
            chat_id=message_data.chat_id,
            chunk_id=message_data.chunk_id,
            content=message_data.content,
            role=message_data.role,
            task=message_data.task,
            status=message_data.status,
        )

        result = self.db.table(self.table_name).insert(message.to_dict()).execute()

        if not result.data:
            raise ValueError("Failed to create message")

        return MessageResponse(**result.data[0])

    async def get_messages(self, skip: int = 0, limit: int = 100) -> List[MessageResponse]:
        """Get all messages with pagination."""
        result = self.db.table(self.table_name).select("*").range(skip, skip + limit - 1).order("created_at", desc=True).execute()

        return [MessageResponse(**msg) for msg in result.data]

    async def get_messages_by_chat_id(self, chat_id: str, skip: int = 0, limit: int = 100) -> List[MessageResponse]:
        """Get all messages by chat id with pagination."""
        result = self.db.table(self.table_name).select("*").eq("chat_id", chat_id).range(skip, skip + limit - 1).order("created_at", desc=True).execute()

        return [MessageResponse(**msg) for msg in result.data]

    async def get_message_by_id(self, message_id: str) -> Optional[MessageResponse]:
        """Get a message by ID."""
        try:
            uuid.UUID(message_id)
        except ValueError:
            raise ValueError("Invalid message ID format")

        result = self.db.table(self.table_name).select("*").eq("id", message_id).execute()

        if not result.data:
            return None

        return MessageResponse(**result.data[0])

    async def update_message(self, message_id: str, message_update: MessageUpdate) -> Optional[MessageResponse]:
        """Update a message."""
        try:
            uuid.UUID(message_id)
        except ValueError:
            raise ValueError("Invalid message ID format")

        existing = await self.get_message_by_id(message_id)
        if not existing:
            return None

        update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}

        if message_update.content is not None:
            update_data["content"] = message_update.content
        if message_update.status is not None:
            update_data["status"] = message_update.status.value
        if message_update.task is not None:
            update_data["task"] = message_update.task.value
        if message_update.chunk_id is not None:
            update_data["chunk_id"] = message_update.chunk_id

        result = self.db.table(self.table_name).update(update_data).eq("id", message_id).execute()

        if not result.data:
            raise ValueError("Failed to update message")

        return MessageResponse(**result.data[0])

    async def delete_message(self, message_id: str) -> bool:
        """Delete a message."""
        try:
            uuid.UUID(message_id)
        except ValueError:
            raise ValueError("Invalid message ID format")

        existing = await self.get_message_by_id(message_id)
        if not existing:
            return False

        self.db.table(self.table_name).delete().eq("id", message_id).execute()
        return True
