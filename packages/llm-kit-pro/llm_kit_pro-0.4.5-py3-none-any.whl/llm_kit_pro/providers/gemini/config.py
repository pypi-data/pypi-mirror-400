from pydantic import BaseModel, Field


class GeminiConfig(BaseModel):
    """
    Configuration for Google Gemini client.

    Attributes:
        api_key: Google Gemini API key (required)
        model: Gemini model identifier (required), e.g., "gemini-2.5-flash", "gemini-pro"
        temperature: Sampling temperature for generation (default: 0.2)
    """

    api_key: str = Field(..., description="Gemini API key")
    model: str = Field(..., description="Gemini model to use")
    temperature: float = Field(default=0.2)
