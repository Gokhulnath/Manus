import logging
from dotenv import load_dotenv

from agent.reasoning_processor import ReasoningProcessor
from core.database import get_supabase_client
from core.enums import MessageRole, MessageStatus, MessageTask
from schemas.message import MessageUpdate, MessageCreate
from services.message import MessageService

load_dotenv()

logger = logging.getLogger(__name__)

class ChatProcessor:
    def __init__(self):
        self.processor = ReasoningProcessor()
        self.service = MessageService(get_supabase_client())

    async def process_chat(self, chat_id :str):
        messages = await self.service.get_messages_by_chat_id(chat_id)
        for message in messages:
            if message.role == MessageRole.USER and message.status == MessageStatus.PENDING:
                result = await self.processor.answer_question(question=message.content)
                await self.service.update_message(message.id, MessageUpdate(status=MessageStatus.COMPLETED))
                await self.service.create_message(MessageCreate(chat_id=message.chat_id,
                                                                role=MessageRole.ASSISTANT,
                                                                content=result['answer'],
                                                                task=MessageTask.SUMMARIZE,
                                                                status=MessageStatus.COMPLETED))