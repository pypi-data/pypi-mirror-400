from typing import List

from pydantic import BaseModel, Field


class AnthropicConfig(BaseModel):
    """
    Configuration for Anthropic Claude client.

    Attributes:
        api_key: Anthropic API key (required)
        model: Claude model identifier (required), e.g., "claude-sonnet-4-5-20250929", "claude-3-5-sonnet-20241022"
        temperature: Sampling temperature for generation (default: 0.2)
    """

    api_key: str = Field(..., description="Anthropic API key")
    model: str = Field(..., description="Anthropic model to use")
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
