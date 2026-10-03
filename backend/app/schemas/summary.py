from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

class SummaryRead(BaseModel):
    id: UUID
    conversation_id: UUID
    content: str
    start_message_id: UUID
    end_message_id: UUID
    start_sequence_number: int
    end_sequence_number: int
    total_prompt_tokens: int
    total_output_tokens: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)