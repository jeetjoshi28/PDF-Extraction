"""Load include / exclude keyword sets from ``KEYWORDS_JSON`` in ``keywords_embedded.py``."""

import json


def _string_list(raw: list, field_name: str) -> list[str]:
    if not isinstance(raw, list):
        raise ValueError(f'"{field_name}" must be an array of strings.')
    out = []
    for item in raw:
        if not isinstance(item, str):
            raise ValueError(f'Each entry in "{field_name}" must be a string.')
        s = item.strip()
        if s:
            out.append(s)
    return out


def _parse_config(data) -> tuple[list[str], list[str]]:
    if isinstance(data, list):
        return _string_list(data, "keywords"), []

    if isinstance(data, dict):
        if "keywords" not in data:
            raise ValueError(
                "JSON must be a string array, or an object with "
                '"keywords" (array) and optional "exclude_keywords" (array).'
            )
        include = _string_list(data["keywords"], "keywords")
        raw_ex = data.get("exclude_keywords", [])
        if raw_ex is None:
            raw_ex = []
        exclude = _string_list(raw_ex, "exclude_keywords")
        return include, exclude

    raise ValueError(
        "JSON must be a string array, e.g. [\"a\",\"b\"], "
        'or an object with "keywords" and optional "exclude_keywords".'
    )


def load_embedded_keyword_sets() -> tuple[list[str], list[str]]:
    try:
        from keywords_embedded import KEYWORDS_JSON
    except ImportError as e:
        raise ValueError("keywords_embedded.py is missing or has no KEYWORDS_JSON.") from e

    raw = KEYWORDS_JSON.strip()
    if not raw:
        raise ValueError("KEYWORDS_JSON in keywords_embedded.py is empty.")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in keywords_embedded.py: {e}") from e

    include, exclude = _parse_config(data)
    if not include:
        raise ValueError("No keywords after parsing KEYWORDS_JSON.")
    return include, exclude


def load_embedded_keywords() -> list[str]:
    """Include-keywords only (same order as first element of ``load_embedded_keyword_sets``)."""
    include, _ = load_embedded_keyword_sets()
    return include
