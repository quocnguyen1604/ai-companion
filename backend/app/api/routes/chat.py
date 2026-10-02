from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.message import ChatTurn, MessageCreate
from app.services.ai.base import AIProvider
from app.services.conversation import ConversationService
from app.services.providers import get_ai_provider

router = APIRouter()


@router.post("/{conversation_id}/messages", response_model=ChatTurn, status_code=status.HTTP_201_CREATED)
async def send_message(
    conversation_id: UUID,
    request: MessageCreate,
    db: Session = Depends(get_db),
    provider: AIProvider = Depends(get_ai_provider),
) -> StreamingResponse:
    service = ConversationService(db, provider)
    if service.get_conversation(conversation_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return StreamingResponse(
        service.send_message(conversation_id, request.content),
        media_type="text/event-stream"
    )