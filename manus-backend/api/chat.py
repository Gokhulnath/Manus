from fastapi import APIRouter, HTTPException, Depends
from typing import List
from core.database import get_chat_service
from schemas.chat import ChatCreate, ChatUpdate, ChatResponse
from services.chat import ChatService


router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def create_chat(
    chat: ChatCreate,
    service: ChatService = Depends(get_chat_service)
):
    """Create a new chat."""
    try:
        return await service.create_chat(chat)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/", response_model=List[ChatResponse])
async def get_chats(
    skip: int = 0,
    limit: int = 100,
    service: ChatService = Depends(get_chat_service)
):
    """Get all chats with pagination."""
    try:
        return await service.get_chats(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch chats: {str(e)}")

@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(
    chat_id: str,
    service: ChatService = Depends(get_chat_service)
):
    """Get a specific chat by ID."""
    try:
        chat = await service.get_chat_by_id(chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        return chat
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch chat: {str(e)}")

@router.put("/{chat_id}", response_model=ChatResponse)
async def update_chat(
    chat_id: str,
    chat_update: ChatUpdate,
    service: ChatService = Depends(get_chat_service)
):
    """Update a specific chat."""
    try:
        chat = await service.update_chat(chat_id, chat_update)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        return chat
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update chat: {str(e)}")

@router.delete("/{chat_id}")
async def delete_chat(
    chat_id: str,
    service: ChatService = Depends(get_chat_service)
):
    """Delete a specific chat."""
    try:
        success = await service.delete_chat(chat_id)
        if not success:
            raise HTTPException(status_code=404, detail="Chat not found")
        return {"message": "Chat deleted successfully", "id": chat_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete chat: {str(e)}")