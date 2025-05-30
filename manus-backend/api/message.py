import asyncio
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from agent.chat_processor import ChatProcessor
from core.database import get_message_service
from schemas.message import MessageCreate, MessageUpdate, MessageResponse
from services.message import MessageService

router = APIRouter()

@router.post("/", response_model=MessageResponse)
async def create_message(
    message: MessageCreate,
    service: MessageService = Depends(get_message_service)
):
    """Create a new message."""
    try:
        result =  await service.create_message(message)
        processor = ChatProcessor()
        asyncio.create_task(processor.process_chat(chat_id=result.chat_id))
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/", response_model=List[MessageResponse])
async def get_messages(
    skip: int = 0,
    limit: int = 100,
    service: MessageService = Depends(get_message_service)
):
    """Get all messages with pagination."""
    try:
        return await service.get_messages(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch messages: {str(e)}")

@router.get("/chat/{chat_id}", response_model=List[MessageResponse])
async def get_messages_by_chat_id(
    chat_id: str,
    skip: int = 0,
    limit: int = 100,
    service: MessageService = Depends(get_message_service)
):
    """Get all messages by chat id with pagination."""
    try:
        return await service.get_messages_by_chat_id(chat_id, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch messages: {str(e)}")


@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: str,
    service: MessageService = Depends(get_message_service)
):
    """Get a specific message by ID."""
    try:
        message = await service.get_message_by_id(message_id)
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        return message
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch message: {str(e)}")

@router.put("/{message_id}", response_model=MessageResponse)
async def update_message(
    message_id: str,
    message_update: MessageUpdate,
    service: MessageService = Depends(get_message_service)
):
    """Update a specific message."""
    try:
        message = await service.update_message(message_id, message_update)
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        return message
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update message: {str(e)}")

@router.delete("/{message_id}")
async def delete_message(
    message_id: str,
    service: MessageService = Depends(get_message_service)
):
    """Delete a specific message."""
    try:
        success = await service.delete_message(message_id)
        if not success:
            raise HTTPException(status_code=404, detail="Message not found")
        return {"message": "Message deleted successfully", "id": message_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete message: {str(e)}")