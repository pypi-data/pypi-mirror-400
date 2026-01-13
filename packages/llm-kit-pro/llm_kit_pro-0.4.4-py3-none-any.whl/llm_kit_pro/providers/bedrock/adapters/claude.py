import json
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel

from llm_kit_pro.core.inputs import LLMFile
from llm_kit_pro.providers.anthropic.utils import build_content_blocks
from llm_kit_pro.providers.bedrock.adapters.base import BedrockModelAdapter
from llm_kit_pro.providers.bedrock.constants import ANTHROPIC_BEDROCK_VERSION


class ClaudeAdapter(BedrockModelAdapter):
    # ---------- internal helpers ----------

    def _build_request(
        self,
        prompt: str,
        *,
        files: Optional[List[LLMFile]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        temperature = kwargs.get("temperature")
        max_tokens = kwargs.get("max_tokens", 1024)

        # Use shared utility for building content blocks
        # Bedrock doesn't support text/plain files, so we pass support_text_files=False
        content_blocks = build_content_blocks(prompt, files, support_text_files=False)

        payload: Dict[str, Any] = {
            "anthropic_version": ANTHROPIC_BEDROCK_VERSION,
            "max_tokens": max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": content_blocks,
                }
            ],
        }

        if temperature is not None:
            payload["temperature"] = temperature

        return {
            "modelId": self.model_id,
            "contentType": "application/json",
            "accept": "application/json",
            "body": json.dumps(payload),
        }

    # ---------- public API ----------

    def build_text_request(
        self,
        prompt: str,
        *,
        files: Optional[List[LLMFile]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        return self._build_request(prompt, files=files, **kwargs)

    def build_json_request(
        self,
        prompt: str,
        schema: Type[BaseModel],
        *,
        files: Optional[List[LLMFile]] = None,
        inject_schema: bool = True,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        if inject_schema:
            json_schema = schema.model_json_schema()
            schema_prompt = (
                f"{prompt}\n\n"
                f"Return ONLY valid JSON matching this schema:\n"
                f"{json.dumps(json_schema)}"
            )
        else:
            schema_prompt = prompt
        return self._build_request(schema_prompt, files=files, **kwargs)

    def parse_response(self, response: Dict[str, Any]) -> str:
        body = json.loads(response["body"].read())
        return body["content"][0]["text"]
