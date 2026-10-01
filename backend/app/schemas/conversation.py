from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ConversationRead(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    previous_response_id: str | None = None

    model_config = ConfigDict(from_attributes=True)
