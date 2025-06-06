import os
from dotenv import load_dotenv
from fastapi import Depends
from supabase import create_client, Client
from services.chat import ChatService
from services.message import MessageService

load_dotenv()

def get_supabase_client() -> Client:
    return create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

def get_chat_service(db: Client = Depends(get_supabase_client)) -> ChatService:
    return ChatService(db)

def get_message_service(db: Client = Depends(get_supabase_client)) -> MessageService:
    return MessageService(db)