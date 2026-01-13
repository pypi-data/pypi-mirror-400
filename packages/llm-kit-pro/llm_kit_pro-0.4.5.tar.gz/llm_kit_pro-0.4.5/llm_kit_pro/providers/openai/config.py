from pydantic import BaseModel, Field


class OpenAIConfig(BaseModel):
    """
    Configuration for OpenAI client.

    Attributes:
        api_key: OpenAI API key (required)
        model: OpenAI model identifier (required), e.g., "gpt-4o-mini", "gpt-4o"
        temperature: Sampling temperature for generation (default: 0.2)
    """

    api_key: str = Field(..., description="OpenAI API key")
    model: str = Field(..., description="OpenAI model to use")
    temperature: float = Field(default=0.2)
