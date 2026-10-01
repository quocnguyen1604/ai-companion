from functools import lru_cache

from app.services.ai.base import AIProvider
from app.services.ai.mock import MockAIProvider
from app.services.ai.lmstudio import LMStudioAIProvider


@lru_cache
def get_ai_provider() -> AIProvider:
    return LMStudioAIProvider()  # Replace with MockAIProvider() for testing without an actual AI provider
