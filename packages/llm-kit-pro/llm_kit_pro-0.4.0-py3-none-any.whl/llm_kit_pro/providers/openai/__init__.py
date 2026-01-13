from llm_kit_pro.core.registry import register_provider
from llm_kit_pro.providers.openai.client import OpenAIClient

register_provider("openai", OpenAIClient)

__all__ = ["OpenAIClient"]
