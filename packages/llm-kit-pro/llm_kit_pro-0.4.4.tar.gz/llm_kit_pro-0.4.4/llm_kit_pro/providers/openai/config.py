from pydantic import BaseModel, Field


class OpenAIConfig(BaseModel):
    api_key: str = Field(..., description="OpenAI API key")
    model: str = Field(default="gpt-4o-mini")
    temperature: float = Field(default=0.2)
