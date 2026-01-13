import asyncio
import base64
from typing import Any, Dict, List, Optional, Type, Union

from pydantic import BaseModel

from llm_kit_pro.core.base import BaseLLMClient
from llm_kit_pro.core.inputs import LLMFile
from llm_kit_pro.providers.openai.config import OpenAIConfig

try:
    import openai
except ImportError as e:
    raise ImportError(
        "OpenAI support is not installed.\n"
        "Install it with:\n"
        "  pip install llm-kit-pro[openai]"
    ) from e


class OpenAIClient(BaseLLMClient):
    """
    OpenAI LLM client implementation.

    Args:
        config: OpenAIConfig instance with api_key and model (required).

    Example:
        >>> from llm_kit_pro.providers.openai import OpenAIClient
        >>> from llm_kit_pro.providers.openai.config import OpenAIConfig
        >>> client = OpenAIClient(OpenAIConfig(api_key="your-key", model="gpt-4o-mini"))
    """

    def __init__(self, config: OpenAIConfig):
        self.config = config
        self._client = self._create_client()

    def _create_client(self):
        return openai.OpenAI(api_key=self.config.api_key)

    async def generate_text(
        self,
        prompt: str,
        *,
        files: Optional[List[LLMFile]] = None,
        **kwargs: Any,
    ) -> str:
        messages = [{"role": "user", "content": self._build_contents(prompt, files)}]

        response = await asyncio.to_thread(
            self._client.chat.completions.create,
            model=kwargs.get("model", self.config.model),
            messages=messages,
            temperature=kwargs.get("temperature", self.config.temperature),
            **{k: v for k, v in kwargs.items() if k not in ["model", "temperature"]},
        )

        return response.choices[0].message.content or ""

    async def generate_json(
        self,
        prompt: str,
        schema: Type[BaseModel],
        *,
        files: Optional[List[LLMFile]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        messages = [{"role": "user", "content": self._build_contents(prompt, files)}]

        # OpenAI's native Pydantic support handles strict mode transformation and validation
        response = await asyncio.to_thread(
            self._client.beta.chat.completions.parse,
            model=kwargs.get("model", self.config.model),
            messages=messages,
            temperature=kwargs.get("temperature", self.config.temperature),
            response_format=schema,
            **{
                k: v
                for k, v in kwargs.items()
                if k not in ["model", "temperature", "response_format"]
            },
        )

        message = response.choices[0].message
        if message.refusal:
            raise ValueError(f"Model refused to generate output: {message.refusal}")

        if not message.parsed:
            raise ValueError("Failed to parse response into the provided schema.")

        return message.parsed.model_dump()

    def _build_contents(
        self, prompt: str, files: Optional[List[LLMFile]]
    ) -> Union[str, List[Dict[str, Any]]]:
        if not files:
            return prompt

        content: List[Dict[str, Any]] = [{"type": "text", "text": prompt}]

        for file in files:
            if file.mime_type in ["image/png", "image/jpeg"]:
                encoded = base64.b64encode(file.content).decode("utf-8")
                content.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{file.mime_type};base64,{encoded}"},
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

        return content
