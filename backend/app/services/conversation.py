import json
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Conversation, Message, MessageRole, utc_now
from app.schemas.message import ChatTurn
from app.services.ai.base import AIProvider, MessageRole as ProviderRole, ProviderMessage

from app.tokenizers.tokenizer import Tokenizer


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
        return list(self.db.scalars(select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at, Message.sequence_number)))

    async def send_message(self, conversation_id: UUID, content: str) -> ChatTurn:
        if self.provider is None:
            raise RuntimeError("An AI provider is required to send a message")
        conversation = self.db.get(Conversation, conversation_id)
        if conversation is None:
            raise LookupError("Conversation not found")
        
        tokenizer = Tokenizer()
        history = self.list_messages(conversation_id)
        user_message = Message(conversation_id=conversation_id, 
                               role=MessageRole.USER, 
                               content=content, 
                               response_id=None, 
                               previous_message_id=history[-1].id if history else None, 
                               sequence_number=(history[-1].sequence_number + 1) if history else 0,
                               token_count=tokenizer.count_tokens(content),
                               prompt_token_count=(history[-1].prompt_token_count + tokenizer.count_tokens(content)) if history else tokenizer.count_tokens(content))
        self.db.add(user_message)
        self.db.flush()
        history = self.list_messages(conversation_id)
        provider_history = [ProviderMessage(role=ProviderRole(message.role.value), content=message.content) for message in history]
        response_stream = self.provider.stream_response(provider_history, previous_response_id=conversation.previous_response_id)
        response = None
        final_chunk = None
        async for chunk in response_stream:
            if chunk.type == "response.output_text.delta" and chunk.delta is not None:
                yield f"data: {json.dumps({
                'type': chunk.type,
                'delta': chunk.delta,
                })}\n\n"
            if chunk.type == "response.completed":
                final_chunk = chunk
                response = chunk.response
                break
        assistant_message = Message(conversation_id=conversation_id, 
                                    role=MessageRole.ASSISTANT, content=response.output_text, 
                                    response_id=response.id, 
                                    previous_message_id=user_message.id,
                                    sequence_number=user_message.sequence_number + 1,
                                    token_count=response.usage.output_tokens if response and response.usage 
                                    else tokenizer.count_tokens(response.output_text),
                                    prompt_token_count=response.usage.input_tokens if response and response.usage
                                    else tokenizer.count_tokens(content))
        self.db.add(assistant_message)
        conversation.updated_at = utc_now()
        conversation.previous_response_id = response.id
        self.db.commit()
        self.db.refresh(user_message)
        self.db.refresh(assistant_message)
        print("saved")
        yield f"data: {json.dumps({
            'type': final_chunk.type,
            'turn': ChatTurn(
                user_message=user_message,
                assistant_message=assistant_message
            ).model_dump(mode="json")
        })}\n\n"

