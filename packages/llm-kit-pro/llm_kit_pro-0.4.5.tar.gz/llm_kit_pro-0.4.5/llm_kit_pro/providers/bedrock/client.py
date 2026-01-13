import asyncio
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel

try:
    import boto3
except ImportError as e:
    raise ImportError(
        "Bedrock support is not installed.\n"
        "Install it with:\n"
        "  pip install llm-kit-pro[bedrock]"
    ) from e

from llm_kit_pro.core.base import BaseLLMClient
from llm_kit_pro.core.helpers import extract_json
from llm_kit_pro.core.inputs import LLMFile
from llm_kit_pro.providers.bedrock.adapters.claude import ClaudeAdapter
from llm_kit_pro.providers.bedrock.config import BedrockConfig


class BedrockClient(BaseLLMClient):
    """
    AWS Bedrock LLM client implementation.

    Args:
        config: BedrockConfig instance with access_key, secret_key, region, and model (all required).

    Example:
        >>> from llm_kit_pro.providers.bedrock import BedrockClient
        >>> from llm_kit_pro.providers.bedrock.config import BedrockConfig
        >>> client = BedrockClient(BedrockConfig(
        ...     access_key="your-access-key",
        ...     secret_key="your-secret-key",
        ...     region="us-east-1",
        ...     model="global.anthropic.claude-sonnet-4-5-20250929-v1:0"
        ... ))
    """

    def __init__(self, config: BedrockConfig):
        self.config = config
        self._runtime = boto3.client(
            "bedrock-runtime",
            aws_access_key_id=config.access_key,
            aws_secret_access_key=config.secret_key,
            region_name=config.region,
        )

        self._adapter = self._resolve_adapter()

    def _resolve_adapter(self):
        if self.config.model.startswith("anthropic.") or self.config.model.startswith(
            "global.anthropic."
        ):
            return ClaudeAdapter(self.config.model)

        raise ValueError(f"Unsupported Bedrock model: {self.config.model}")

    async def generate_text(
        self,
        prompt: str,
        *,
        files: Optional[List[LLMFile]] = None,
        **kwargs: Any,
    ) -> str:
        request = self._adapter.build_text_request(prompt, files=files, **kwargs)

        response = await asyncio.to_thread(self._runtime.invoke_model, **request)

        return self._adapter.parse_response(response)

    async def generate_json(
        self,
        prompt: str,
        schema: Type[BaseModel],
        *,
        files: Optional[List[LLMFile]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        request = self._adapter.build_json_request(
            prompt, schema, files=files, **kwargs
        )

        response = await asyncio.to_thread(self._runtime.invoke_model, **request)

        raw = self._adapter.parse_response(response)
        parsed = extract_json(raw)

        # Validate against the Pydantic model and return as dict
        return schema.model_validate(parsed).model_dump()
