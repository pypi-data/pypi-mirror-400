from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel

from llm_kit_pro.core.base import BaseLLMClient
from llm_kit_pro.core.inputs import LLMFile
from llm_kit_pro.providers.anthropic.config import AnthropicConfig
from llm_kit_pro.providers.anthropic.utils import build_content_blocks

try:
    import anthropic
except ImportError as e:
    raise ImportError(
        "Anthropic support is not installed.\n"
        "Install it with:\n"
        "  pip install llm-kit-pro[anthropic]"
    ) from e


class AnthropicClient(BaseLLMClient):
    """
    Anthropic Claude LLM client implementation.

    Args:
        config: AnthropicConfig instance with api_key and model (required).

    Example:
        >>> from llm_kit_pro.providers.anthropic import AnthropicClient
        >>> from llm_kit_pro.providers.anthropic.config import AnthropicConfig
        >>> client = AnthropicClient(AnthropicConfig(api_key="your-key", model="claude-sonnet-4-5-20250929"))
    """

    def __init__(self, config: AnthropicConfig):
        self.config = config
        self._client = anthropic.AsyncAnthropic(api_key=self.config.api_key)

    async def generate_text(
        self,
        prompt: str,
        *,
        files: Optional[List[LLMFile]] = None,
        **kwargs: Any,
    ) -> str:
        content = build_content_blocks(prompt, files, support_text_files=True)

        response = await self._client.messages.create(
            model=kwargs.get("model", self.config.model),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            temperature=kwargs.get("temperature", self.config.temperature),
            messages=[{"role": "user", "content": content}],
            **{
                k: v
                for k, v in kwargs.items()
                if k not in ["model", "max_tokens", "temperature"]
            },
        )

        return response.content[0].text

    async def generate_json(
        self,
        prompt: str,
        schema: Type[BaseModel],
        *,
        files: Optional[List[LLMFile]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Generate structured JSON output using Anthropic's tool use (forced).
        """
        tool_name = "format_output"
        tools: List[Dict[str, Any]] = [
            {
                "name": tool_name,
                "description": "Format the output as JSON according to the provided schema.",
                "input_schema": schema.model_json_schema(),
            }
        ]

        content = build_content_blocks(prompt, files, support_text_files=True)

        response = await self._client.messages.create(
            model=kwargs.get("model", self.config.model),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            temperature=kwargs.get("temperature", self.config.temperature),
            messages=[{"role": "user", "content": content}],
            tools=tools,
            tool_choice={"type": "tool", "name": tool_name},
            **{
                k: v
                for k, v in kwargs.items()
                if k
                not in ["model", "max_tokens", "temperature", "tools", "tool_choice"]
            },
        )

        # Find the tool use block in the response content
        for block in response.content:
            if block.type == "tool_use" and block.name == tool_name:
                return block.input

        raise ValueError(
            "Anthropic failed to return a tool use block for JSON generation."
        )
