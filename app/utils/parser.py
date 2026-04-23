import json
import re


def _extract_content(result):
    content = result.get("response")
    if not content:
        candidates = result.get("candidates", [])
        parts = (((candidates[0] if candidates else {}).get("content") or {}).get("parts") or [])
        if parts:
            content = parts[0].get("text", "")
    if not content:
        raise Exception("Gemini response tidak memiliki text")
    return re.sub(r"```json\n|\n```", "", content)


def parse_llm_response(result):
    try:
        content = _extract_content(result)
        parsed = json.loads(content)
        return parsed.get("motivations", [])
    except Exception as e:
        raise Exception(f"Invalid JSON from LLM: {str(e)}")


def parse_recommendations_response(result):
    try:
        content = _extract_content(result)
        parsed = json.loads(content)
        return parsed.get("recommendations", [])
    except Exception as e:
        raise Exception(f"Invalid JSON from LLM: {str(e)}")
