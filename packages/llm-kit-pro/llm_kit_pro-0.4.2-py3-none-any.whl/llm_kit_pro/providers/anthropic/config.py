from typing import List

from pydantic import BaseModel, Field


class AnthropicConfig(BaseModel):
    api_key: str = Field(..., description="Anthropic API key")
    model: str = Field(default="claude-sonnet-4-5-20250929-v1")
    temperature: float = Field(default=0.2)
    max_tokens: int = Field(default=1000)
    top_p: float = Field(default=1.0)
    frequency_penalty: float = Field(default=0.0)
    presence_penalty: float = Field(default=0.0)
    stop_sequences: List[str] = Field(default=[])
    stop_token_ids: List[int] = Field(default=[])
    stop_words: List[str] = Field(default=[])
    stop_word_ids: List[int] = Field(default=[])
    stop_word_tokens: List[str] = Field(default=[])
