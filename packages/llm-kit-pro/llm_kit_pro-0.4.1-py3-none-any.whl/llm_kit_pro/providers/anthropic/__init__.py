from llm_kit_pro.core.registry import register_provider
from llm_kit_pro.providers.anthropic.client import AnthropicClient

register_provider("anthropic", AnthropicClient)

__all__ = ["AnthropicClient"]
