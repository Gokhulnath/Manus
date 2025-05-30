from fastapi import Depends
from supabase import Client
from core.database import get_supabase_client
from services.chat import ChatService

def get_supabase() -> Client:
    return get_supabase_client()

def get_chat_service(db: Client = Depends(get_supabase)) -> ChatService:
    return ChatService(db)