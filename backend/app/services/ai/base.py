from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


@dataclass(frozen=True)
class ProviderMessage:
    role: MessageRole
    content: str


@dataclass(frozen=True)
class ProviderSummary:
    content: str
    prompt_token_count: int | None = None
    token_count: int | None = None


class AIProvider(Protocol):
    async def generate_response(self, messages: list[ProviderMessage], previous_response_id: str | None) -> str:
        """Return an assistant response for the supplied conversation history."""
    async def stream_response(self, messages: list[ProviderMessage], previous_response_id: str | None) -> str:
        """Stream an assistant response for the supplied conversation history."""
