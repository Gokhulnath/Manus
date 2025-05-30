import logging
from dotenv import load_dotenv

from agent.reasoning_processor import ReasoningProcessor
from core.database import get_supabase_client
from core.enums import MessageRole, MessageStatus
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
                print(result)