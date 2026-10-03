from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.db.models import MessageRole


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=20_000)


class MessageRead(BaseModel):
    id: UUID
    conversation_id: UUID
    role: MessageRole
    content: str
    created_at: datetime
    response_id: str | None = None
    previous_message_id: UUID | None = None
    sequence_number: int = 0
    token_count: int = 0
    prompt_token_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class ChatTurn(BaseModel):
    user_message: MessageRead
    assistant_message: MessageRead
