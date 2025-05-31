import logging
from dotenv import load_dotenv

from agent.reasoning_processor import ReasoningProcessor
from core.database import get_supabase_client
from core.enums import MessageRole, MessageStatus, MessageTask
from schemas.chat import ChatUpdate
from schemas.message import MessageUpdate, MessageCreate
from services.chat import ChatService
from services.message import MessageService

load_dotenv()

logger = logging.getLogger(__name__)

class ChatProcessor:
    def __init__(self):
        self.processor = ReasoningProcessor()
        self.message_service = MessageService(get_supabase_client())
        self.chat_service = ChatService(get_supabase_client())

    async def process_chat(self, chat_id :str):
        messages = await self.message_service.get_messages_by_chat_id(chat_id)
        if len(messages) == 1:
            preview = messages[0].content
            title = preview[:27] + "..." if len(preview) > 27 else preview
            self._rename_chat(chat_id, title)
        for message in messages:
            if message.role == MessageRole.USER and message.status == MessageStatus.PENDING:
                result = await self.processor.answer_question(message = message)
                await self.message_service.update_message(message.id, MessageUpdate(status=MessageStatus.COMPLETED))
                await self.message_service.create_message(MessageCreate(chat_id=message.chat_id,
                                                                        role=MessageRole.ASSISTANT,
                                                                        content=result['answer'],
                                                                        task=MessageTask.SUMMARIZE,
                                                                        status=MessageStatus.COMPLETED))

    async def _rename_chat(self, chat_id :str, title : str):
        await self.chat_service.update_chat(chat_id=chat_id, chat_update=ChatUpdate(title=title))

