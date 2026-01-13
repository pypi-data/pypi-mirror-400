"""
Shared utilities for building Anthropic-style content blocks.
Used by both the direct Anthropic provider and Bedrock's Claude adapter.
"""

import base64
from typing import Any, Dict, List, Optional

from llm_kit_pro.core.inputs import LLMFile


def file_to_content_block(
    file: LLMFile, support_text_files: bool = True
) -> Dict[str, Any]:
    """
    Convert an LLMFile to an Anthropic-style content block.

    Args:
        file: The file to convert
        support_text_files: Whether to support text/plain files (not supported on Bedrock)

    Returns:
        A content block dictionary in Anthropic's format

    Raises:
        ValueError: If the file type is unsupported
    """
    encoded = base64.b64encode(file.content).decode("utf-8")

    if file.mime_type.startswith("image/"):
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": file.mime_type,
                "data": encoded,
            },
        }

    if file.mime_type == "application/pdf":
        return {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": "application/pdf",
                "data": encoded,
            },
        }

    if file.mime_type == "text/plain" and support_text_files:
        text_content = file.content.decode("utf-8")
        return {
            "type": "text",
            "text": f"\n\n--- Attached File: {file.filename or 'unnamed'} ---\n{text_content}",
        }

    raise ValueError(f"Unsupported file type: {file.mime_type}")


def build_content_blocks(
    prompt: str, files: Optional[List[LLMFile]] = None, support_text_files: bool = True
) -> List[Dict[str, Any]]:
    """
    Build a list of Anthropic-style content blocks from a prompt and optional files.

    Args:
        prompt: The text prompt
        files: Optional list of files to include
        support_text_files: Whether to support text/plain files (not supported on Bedrock)

    Returns:
        A list of content block dictionaries
    """
    content: List[Dict[str, Any]] = [{"type": "text", "text": prompt}]

    if files:
        for file in files:
            content.append(file_to_content_block(file, support_text_files))

    return content
