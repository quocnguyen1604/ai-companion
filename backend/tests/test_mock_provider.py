import pytest

from app.services.ai.base import MessageRole, ProviderMessage
from app.services.ai.mock import MockAIProvider


@pytest.mark.asyncio
async def test_mock_provider_responds_to_latest_user_message():
    provider = MockAIProvider()
    response = await provider.generate_response([
        ProviderMessage(role=MessageRole.USER, content="first"),
        ProviderMessage(role=MessageRole.ASSISTANT, content="earlier"),
        ProviderMessage(role=MessageRole.USER, content="latest"),
    ])
    assert response == "I hear you: latest"
