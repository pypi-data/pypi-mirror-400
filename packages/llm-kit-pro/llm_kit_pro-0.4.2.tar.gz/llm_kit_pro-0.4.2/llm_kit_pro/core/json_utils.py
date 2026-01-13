from typing import Any, Dict, List, Union

import json_repair


class JSONExtractionError(ValueError):
    """Raised when JSON cannot be extracted from the provided text."""

    pass


def extract_json(text: str) -> Union[Dict[str, Any], List[Any]]:
    """
    Extracts and repairs JSON from a given text string.

    Uses a combination of stack-based extraction and json_repair to find
    and fix common JSON issues in LLM outputs.
    """
    text = text.strip()
    last_error = None

    try:
        decoded = json_repair.repair_json(text, return_objects=True)
        if isinstance(decoded, (dict, list)):
            return _format_result(decoded)
    except Exception:
        pass

    start_indices = [i for i, char in enumerate(text) if char in "{["]

    if not start_indices:
        raise JSONExtractionError("No JSON-like opening brackets found.")

    for start in start_indices:
        opener = text[start]
        closer = "}" if opener == "{" else "]"

        depth = 0
        end = -1

        for i in range(start, len(text)):
            char = text[i]
            if char == opener:
                depth += 1
            elif char == closer:
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break

        candidates = []

        if end != -1:
            candidates.append(text[start:end])

        candidates.append(text[start:])

        for candidate in candidates:
            try:
                decoded = json_repair.repair_json(candidate, return_objects=True)
                if isinstance(decoded, (dict, list)) and decoded:
                    return _format_result(decoded)
            except Exception as e:
                last_error = e
                continue

    raise JSONExtractionError(f"No valid JSON object found. Last error: {last_error}")


def _format_result(decoded: Any) -> Dict[str, Any]:
    """Helper to ensure we always return a Dict, wrapping lists if necessary."""
    if isinstance(decoded, list):
        return {"data": decoded}
    return decoded
