from app.services.ai.base import AIProvider, MessageRole, ProviderMessage


class MockAIProvider:
    """A deterministic local provider used to exercise the chat workflow."""

    async def generate_response(self, messages: list[ProviderMessage]) -> str:
        latest_user_message = next((message.content for message in reversed(messages) if message.role == MessageRole.USER), "")
        return f"I hear you: {latest_user_message}"
