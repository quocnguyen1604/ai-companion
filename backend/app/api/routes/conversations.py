from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.conversation import ConversationRead
from app.schemas.message import MessageRead
from app.services.conversation import ConversationService

router = APIRouter()


@router.post("", response_model=ConversationRead, status_code=status.HTTP_201_CREATED)
def create_conversation(db: Session = Depends(get_db)) -> ConversationRead:
    return ConversationService(db).create_conversation()


@router.get("", response_model=list[ConversationRead])
def list_conversations(db: Session = Depends(get_db)) -> list[ConversationRead]:
    return ConversationService(db).list_conversations()


@router.get("/{conversation_id}", response_model=ConversationRead)
def get_conversation(conversation_id: UUID, db: Session = Depends(get_db)) -> ConversationRead:
    conversation = ConversationService(db).get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conversation


@router.get("/{conversation_id}/messages", response_model=list[MessageRead])
def list_messages(conversation_id: UUID, db: Session = Depends(get_db)) -> list[MessageRead]:
    service = ConversationService(db)
    if service.get_conversation(conversation_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return service.list_messages(conversation_id)
