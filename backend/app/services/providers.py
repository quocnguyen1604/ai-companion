from functools import lru_cache

from app.services.ai.base import AIProvider
from app.services.ai.mock import MockAIProvider


@lru_cache
def get_ai_provider() -> AIProvider:
    return MockAIProvider()
