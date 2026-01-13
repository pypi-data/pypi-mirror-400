"""Helper utilities for converting files from local paths or URLs to LLMFile objects."""

import mimetypes
from pathlib import Path
from typing import Literal, Optional, Union
from urllib.parse import urlparse

import httpx

from llm_kit_pro.core.inputs import LLMFile

# Supported MIME types (matching LLMFile definition)
SUPPORTED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/jpg",  # Common alias
    "text/plain",
}

# MIME type normalization map
MIME_TYPE_ALIASES = {
    "image/jpg": "image/jpeg",
}


class FileLoadError(Exception):
    """Raised when file loading fails."""

    pass


class UnsupportedMimeTypeError(Exception):
    """Raised when the detected MIME type is not supported."""

    pass


def _normalize_mime_type(
    mime_type: str,
) -> Literal["application/pdf", "image/png", "image/jpeg", "text/plain"]:
    """
    Normalize and validate MIME type.

    Args:
        mime_type: The detected MIME type string

    Returns:
        Normalized MIME type that matches LLMFile's Literal type

    Raises:
        UnsupportedMimeTypeError: If the MIME type is not supported
    """
    # Normalize the MIME type
    normalized = MIME_TYPE_ALIASES.get(mime_type.lower(), mime_type.lower())

    # Map to LLMFile's Literal types
    valid_types = {
        "application/pdf": "application/pdf",
        "image/png": "image/png",
        "image/jpeg": "image/jpeg",
        "text/plain": "text/plain",
    }

    if normalized not in valid_types:
        raise UnsupportedMimeTypeError(
            f"MIME type '{mime_type}' is not supported. "
            f"Supported types: {', '.join(valid_types.keys())}"
        )

    return valid_types[normalized]  # type: ignore


def _detect_mime_type(content: bytes, filename: Optional[str] = None) -> str:
    """
    Detect MIME type from content and/or filename.

    Args:
        content: File content as bytes
        filename: Optional filename for extension-based detection

    Returns:
        Detected MIME type string

    Raises:
        UnsupportedMimeTypeError: If MIME type cannot be detected
    """
    mime_type = None

    # First, try to detect from filename extension
    if filename:
        mime_type, _ = mimetypes.guess_type(filename)

    # If still not detected, try common file signatures (magic numbers)
    if not mime_type and len(content) >= 4:
        # PDF signature
        if content.startswith(b"%PDF"):
            mime_type = "application/pdf"
        # PNG signature
        elif content.startswith(b"\x89PNG\r\n\x1a\n"):
            mime_type = "image/png"
        # JPEG signature
        elif content.startswith(b"\xff\xd8\xff"):
            mime_type = "image/jpeg"
        # Plain text (heuristic: check if content is valid UTF-8)
        else:
            try:
                content.decode("utf-8")
                mime_type = "text/plain"
            except UnicodeDecodeError:
                pass

    if not mime_type:
        raise UnsupportedMimeTypeError(
            "Could not detect MIME type. Please provide a file with a clear extension "
            "or ensure the file has proper magic bytes."
        )

    return mime_type


def _is_url(path: str) -> bool:
    """
    Check if a string is a URL.

    Args:
        path: The path string to check

    Returns:
        True if the string appears to be a URL, False otherwise
    """
    try:
        result = urlparse(path)
        return bool(result.scheme and result.scheme in ("http", "https", "file"))
    except Exception:
        return False


def load_file_from_path(
    file_path: str,
    mime_type: Optional[str] = None,
    filename: Optional[str] = None,
) -> LLMFile:
    """
    Load a file from a local filesystem path and convert to LLMFile.

    Args:
        file_path: Path to the local file
        mime_type: Optional explicit MIME type. If not provided, will be auto-detected
        filename: Optional filename override. If not provided, uses the file's basename

    Returns:
        LLMFile object containing the file content and metadata

    Raises:
        FileLoadError: If the file cannot be read
        UnsupportedMimeTypeError: If the MIME type is not supported
    """
    try:
        path = Path(file_path).expanduser().resolve()

        if not path.exists():
            raise FileLoadError(f"File not found: {file_path}")

        if not path.is_file():
            raise FileLoadError(f"Path is not a file: {file_path}")

        # Read file content
        with open(path, "rb") as f:
            content = f.read()

        # Use provided filename or extract from path
        final_filename = filename or path.name

        # Detect or validate MIME type
        if mime_type:
            detected_mime = mime_type
        else:
            detected_mime = _detect_mime_type(content, final_filename)

        # Normalize and validate
        normalized_mime = _normalize_mime_type(detected_mime)

        return LLMFile(
            content=content,
            mime_type=normalized_mime,
            filename=final_filename,
        )

    except (OSError, IOError) as e:
        raise FileLoadError(f"Failed to read file '{file_path}': {e}") from e


def load_file_from_url(
    url: str,
    mime_type: Optional[str] = None,
    filename: Optional[str] = None,
    timeout: float = 30.0,
) -> LLMFile:
    """
    Download a file from a URL and convert to LLMFile (synchronous).

    Args:
        url: URL to download the file from
        mime_type: Optional explicit MIME type. If not provided, will be auto-detected
        filename: Optional filename override. If not provided, extracts from URL
        timeout: Request timeout in seconds (default: 30.0)

    Returns:
        LLMFile object containing the downloaded file content and metadata

    Raises:
        FileLoadError: If the download fails
        UnsupportedMimeTypeError: If the MIME type is not supported
    """
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
            content = response.content

        # Extract filename from URL if not provided
        if not filename:
            parsed = urlparse(url)
            filename = Path(parsed.path).name or "downloaded_file"

        # Try to get MIME type from response headers if not provided
        if not mime_type and "content-type" in response.headers:
            content_type = response.headers["content-type"].split(";")[0].strip()
            mime_type = content_type

        # Detect or validate MIME type
        if mime_type:
            detected_mime = mime_type
        else:
            detected_mime = _detect_mime_type(content, filename)

        # Normalize and validate
        normalized_mime = _normalize_mime_type(detected_mime)

        return LLMFile(
            content=content,
            mime_type=normalized_mime,
            filename=filename,
        )

    except httpx.HTTPError as e:
        raise FileLoadError(f"Failed to download file from '{url}': {e}") from e
    except Exception as e:
        raise FileLoadError(f"Unexpected error downloading '{url}': {e}") from e


async def load_file_from_url_async(
    url: str,
    mime_type: Optional[str] = None,
    filename: Optional[str] = None,
    timeout: float = 30.0,
) -> LLMFile:
    """
    Download a file from a URL and convert to LLMFile (asynchronous).

    Args:
        url: URL to download the file from
        mime_type: Optional explicit MIME type. If not provided, will be auto-detected
        filename: Optional filename override. If not provided, extracts from URL
        timeout: Request timeout in seconds (default: 30.0)

    Returns:
        LLMFile object containing the downloaded file content and metadata

    Raises:
        FileLoadError: If the download fails
        UnsupportedMimeTypeError: If the MIME type is not supported
    """
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            content = response.content

        # Extract filename from URL if not provided
        if not filename:
            parsed = urlparse(url)
            filename = Path(parsed.path).name or "downloaded_file"

        # Try to get MIME type from response headers if not provided
        if not mime_type and "content-type" in response.headers:
            content_type = response.headers["content-type"].split(";")[0].strip()
            mime_type = content_type

        # Detect or validate MIME type
        if mime_type:
            detected_mime = mime_type
        else:
            detected_mime = _detect_mime_type(content, filename)

        # Normalize and validate
        normalized_mime = _normalize_mime_type(detected_mime)

        return LLMFile(
            content=content,
            mime_type=normalized_mime,
            filename=filename,
        )

    except httpx.HTTPError as e:
        raise FileLoadError(f"Failed to download file from '{url}': {e}") from e
    except Exception as e:
        raise FileLoadError(f"Unexpected error downloading '{url}': {e}") from e


def load_file(
    source: Union[str, Path],
    mime_type: Optional[str] = None,
    filename: Optional[str] = None,
    timeout: float = 30.0,
) -> LLMFile:
    """
    Universal file loader that handles both local paths and URLs (synchronous).

    This is the main entry point for loading files. It automatically detects
    whether the source is a local file path or a URL and handles it accordingly.

    Args:
        source: Either a local file path or a URL (http://, https://, or file://)
        mime_type: Optional explicit MIME type. If not provided, will be auto-detected
        filename: Optional filename override
        timeout: Request timeout in seconds for URL downloads (default: 30.0)

    Returns:
        LLMFile object containing the file content and metadata

    Raises:
        FileLoadError: If the file cannot be loaded
        UnsupportedMimeTypeError: If the MIME type is not supported

    Examples:
        >>> # Load from local path
        >>> file = load_file("/path/to/document.pdf")
        >>>
        >>> # Load from URL
        >>> file = load_file("https://example.com/image.png")
        >>>
        >>> # Load with explicit MIME type
        >>> file = load_file("/path/to/file", mime_type="text/plain")
        >>>
        >>> # Load with custom filename
        >>> file = load_file("https://example.com/doc", filename="my_doc.pdf")
    """
    source_str = str(source)

    if _is_url(source_str):
        return load_file_from_url(
            url=source_str,
            mime_type=mime_type,
            filename=filename,
            timeout=timeout,
        )
    else:
        return load_file_from_path(
            file_path=source_str,
            mime_type=mime_type,
            filename=filename,
        )


async def load_file_async(
    source: Union[str, Path],
    mime_type: Optional[str] = None,
    filename: Optional[str] = None,
    timeout: float = 30.0,
) -> LLMFile:
    """
    Universal file loader that handles both local paths and URLs (asynchronous).

    This is the async version of load_file(). It automatically detects
    whether the source is a local file path or a URL and handles it accordingly.

    Args:
        source: Either a local file path or a URL (http://, https://, or file://)
        mime_type: Optional explicit MIME type. If not provided, will be auto-detected
        filename: Optional filename override
        timeout: Request timeout in seconds for URL downloads (default: 30.0)

    Returns:
        LLMFile object containing the file content and metadata

    Raises:
        FileLoadError: If the file cannot be loaded
        UnsupportedMimeTypeError: If the MIME type is not supported

    Examples:
        >>> # Load from local path
        >>> file = await load_file_async("/path/to/document.pdf")
        >>>
        >>> # Load from URL
        >>> file = await load_file_async("https://example.com/image.png")
        >>>
        >>> # Load with explicit MIME type
        >>> file = await load_file_async("/path/to/file", mime_type="text/plain")
        >>>
        >>> # Load with custom filename
        >>> file = await load_file_async("https://example.com/doc", filename="my_doc.pdf")
    """
    source_str = str(source)

    if _is_url(source_str):
        return await load_file_from_url_async(
            url=source_str,
            mime_type=mime_type,
            filename=filename,
            timeout=timeout,
        )
    else:
        # Local file operations are not async, but we wrap it for consistency
        return load_file_from_path(
            file_path=source_str,
            mime_type=mime_type,
            filename=filename,
        )


__all__ = [
    "load_file",
    "load_file_async",
    "load_file_from_path",
    "load_file_from_url",
    "load_file_from_url_async",
    "FileLoadError",
    "UnsupportedMimeTypeError",
]
