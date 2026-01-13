import base64
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel

from llm_kit_pro.core.base import BaseLLMClient
from llm_kit_pro.core.inputs import LLMFile
from llm_kit_pro.providers.anthropic.config import AnthropicConfig

try:
    import anthropic
except ImportError as e:
    raise ImportError(
        "Anthropic support is not installed.\n"
        "Install it with:\n"
        "  pip install llm-kit-pro[anthropic]"
    ) from e


class AnthropicClient(BaseLLMClient):
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
        content = self._build_contents(prompt, files)

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

        content = self._build_contents(prompt, files)

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

    def _build_contents(
        self, prompt: str, files: Optional[List[LLMFile]]
    ) -> List[Dict[str, Any]]:
        content: List[Dict[str, Any]] = [{"type": "text", "text": prompt}]

        if not files:
            return content

        for file in files:
            encoded = base64.b64encode(file.content).decode("utf-8")
            if file.mime_type.startswith("image/"):
                content.append(
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": file.mime_type,
                            "data": encoded,
                        },
                    }
                )
            elif file.mime_type == "application/pdf":
                content.append(
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": encoded,
                        },
                    }
                )
            elif file.mime_type == "text/plain":
                text_content = file.content.decode("utf-8")
                content.append(
                    {
                        "type": "text",
                        "text": f"\n\n--- Attached File: {file.filename or 'unnamed'} ---\n{text_content}",
                    }
                )
            # Add more types as needed or silently skip unsupported ones

        return content
