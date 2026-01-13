from typing import Optional

from pydantic import BaseModel, Field


class BedrockConfig(BaseModel):
    """
    Configuration for AWS Bedrock client.

    Attributes:
        access_key: AWS Access Key (required)
        secret_key: AWS Secret Key (required)
        region: AWS Region (required), e.g., "us-east-1", "us-west-2"
        model: Bedrock Model ID (required), e.g., "global.anthropic.claude-sonnet-4-5-20250929-v1:0"
    """

    access_key: str = Field(..., description="AWS Access Key")
    secret_key: str = Field(..., description="AWS Secret Key")
    region: str = Field(..., description="AWS Region")
    model: str = Field(..., description="Bedrock Model ID")

    temperature: Optional[float] = Field(
        default=None, description="Sampling temperature (model-dependent)"
    )

    max_tokens: Optional[int] = Field(
        default=None, description="Maximum tokens to generate (model-dependent)"
    )
