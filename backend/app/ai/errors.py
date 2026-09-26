"""Human-readable API error mapping for Gemini/Lyria."""

from __future__ import annotations


def user_facing_error(exc: Exception) -> str:
    code = getattr(exc, "code", None)
    text = str(exc)
    if code == "missing_or_invalid_key":
        return text
    lower = text.lower()
    if "traceback" in lower:
        return "An unexpected server error happened. Please try again."
    if len(text) > 400:
        return text[:400] + "…"
    return text
