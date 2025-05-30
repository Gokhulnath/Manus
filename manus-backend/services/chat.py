from typing import List, Optional
from supabase import Client
from datetime import datetime, timezone
import uuid

from schemas.chat import ChatCreate, ChatUpdate, ChatResponse
from models.chat import Chat


class ChatService:
    def __init__(self, db: Client):
        self.db = db
        self.table_name = "chat"

    async def create_chat(self, chat_data: ChatCreate) -> ChatResponse:
        """Create a new chat."""
        chat = Chat(title=chat_data.title)

        result = self.db.table(self.table_name).insert(chat.to_dict()).execute()

        if not result.data:
            raise ValueError("Failed to create chat")

        return ChatResponse(**result.data[0])

    async def get_chats(self, skip: int = 0, limit: int = 100) -> List[ChatResponse]:
        """Get all chats with pagination."""
        result = self.db.table(self.table_name).select("*").range(skip, skip + limit - 1).order("created_at",
                                                                                                desc=True).execute()

        return [ChatResponse(**chat) for chat in result.data]

    async def get_chat_by_id(self, chat_id: str) -> Optional[ChatResponse]:
        """Get a chat by ID."""
        try:
            uuid.UUID(chat_id)
        except ValueError:
            raise ValueError("Invalid chat ID format")

        result = self.db.table(self.table_name).select("*").eq("id", chat_id).execute()

        if not result.data:
            return None

        return ChatResponse(**result.data[0])

    async def update_chat(self, chat_id: str, chat_update: ChatUpdate) -> Optional[ChatResponse]:
        """Update a chat."""
        try:
            uuid.UUID(chat_id)
        except ValueError:
            raise ValueError("Invalid chat ID format")

        existing = await self.get_chat_by_id(chat_id)
        if not existing:
            return None

        update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}

        if chat_update.title is not None:
            update_data["title"] = chat_update.title

        result = self.db.table(self.table_name).update(update_data).eq("id", chat_id).execute()

        if not result.data:
            raise ValueError("Failed to update chat")

        return ChatResponse(**result.data[0])

    async def delete_chat(self, chat_id: str) -> bool:
        """Delete a chat."""
        try:
            uuid.UUID(chat_id)
        except ValueError:
            raise ValueError("Invalid chat ID format")

        existing = await self.get_chat_by_id(chat_id)
        if not existing:
            return False

        self.db.table(self.table_name).delete().eq("id", chat_id).execute()
        return True