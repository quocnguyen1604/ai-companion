from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Conversation, Message, MessageRole, utc_now
from app.schemas.message import ChatTurn
from app.services.ai.base import AIProvider, MessageRole as ProviderRole, ProviderMessage


class ConversationService:
    def __init__(self, db: Session, provider: AIProvider | None = None) -> None:
        self.db = db
        self.provider = provider

    def create_conversation(self) -> Conversation:
        conversation = Conversation()
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def get_conversation(self, conversation_id: UUID) -> Conversation | None:
        return self.db.get(Conversation, conversation_id)

    def list_conversations(self) -> list[Conversation]:
        return list(self.db.scalars(select(Conversation).order_by(Conversation.updated_at.desc())))

    def list_messages(self, conversation_id: UUID) -> list[Message]:
        return list(self.db.scalars(select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at, Message.id)))

    async def send_message(self, conversation_id: UUID, content: str) -> ChatTurn:
        if self.provider is None:
            raise RuntimeError("An AI provider is required to send a message")
        conversation = self.db.get(Conversation, conversation_id)
        if conversation is None:
            raise LookupError("Conversation not found")

        user_message = Message(conversation_id=conversation_id, role=MessageRole.USER, content=content)
        self.db.add(user_message)
        self.db.flush()
        history = self.list_messages(conversation_id)
        provider_history = [ProviderMessage(role=ProviderRole(message.role.value), content=message.content) for message in history]
        response = await self.provider.generate_response(provider_history)
        assistant_message = Message(conversation_id=conversation_id, role=MessageRole.ASSISTANT, content=response)
        self.db.add(assistant_message)
        conversation.updated_at = utc_now()
        self.db.commit()
        self.db.refresh(user_message)
        self.db.refresh(assistant_message)
        return ChatTurn(user_message=user_message, assistant_message=assistant_message)
