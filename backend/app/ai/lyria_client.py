"""Google Lyria 3.5 music generation via the official Gemini API.

Uses client.models.generate_content as documented at:
https://ai.google.dev/gemini-api/docs/generate-content/music-generation

Model ID: lyria-3.5
"""

from __future__ import annotations

import logging
from typing import Optional, Tuple

from backend.app.utils.config import GEMINI_API_KEY, LYRIA_MODEL

logger = logging.getLogger(__name__)


class LyriaUnavailableError(RuntimeError):
    def __init__(self, message: str, code: str = "unavailable"):
        super().__init__(message)
        self.code = code


def _friendly_error(exc: Exception) -> LyriaUnavailableError:
    raw = str(exc)
    lower = raw.lower()
    if any(tok in lower for tok in ("api key", "401", "unauthenticated", "invalid api key", "permission_denied")):
        return LyriaUnavailableError(
            "Google API key is missing or invalid. Add a valid GEMINI_API_KEY in the project .env file.",
            code="missing_or_invalid_key",
        )
    if any(tok in lower for tok in ("quota", "429", "resource exhausted", "rate limit", "billing")):
        return LyriaUnavailableError(
            "Lyria music generation is temporarily unavailable because of quota, rate limits, or billing restrictions on this Google account.",
            code="quota",
        )
    if any(tok in lower for tok in ("not found", "404", "is not found", "unknown model")):
        return LyriaUnavailableError(
            "Lyria 3.5 is not available for this API key or account. The local LSTM MIDI generator still works. Enable Lyria access in Google AI Studio if your account supports it.",
            code="unavailable",
        )
    if any(tok in lower for tok in ("403", "blocked", "safety", "prohibited")):
        return LyriaUnavailableError(
            "The music request was blocked by safety filters or account permissions. Try a more generic original-style description without artist names.",
            code="blocked",
        )
    return LyriaUnavailableError(
        "Lyria music generation failed. The local LSTM MIDI generator is still available. Details: network or API error.",
        code="api_error",
    )


def generate_lyria_song(prompt: str) -> Tuple[bytes, str, str]:
    """Call Lyria 3.5 and return (audio_bytes, mime_type, lyrics_or_structure_text)."""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        raise LyriaUnavailableError(
            "GEMINI_API_KEY is not configured. Add it to .env to use the AI Song Generator (Lyria 3.5).",
            code="missing_or_invalid_key",
        )

    try:
        from google import genai
        from google.genai import types
    except Exception as exc:
        raise LyriaUnavailableError(
            "The google-genai SDK is not installed. Run pip install -r requirements.txt.",
            code="sdk_missing",
        ) from exc

    client = genai.Client(api_key=GEMINI_API_KEY)
    response = None
    last_error: Optional[Exception] = None

    # Official generateContent path; config flags vary slightly across SDK versions.
    configs = []
    try:
        configs.append(
            types.GenerateContentConfig(
                response_modalities=["AUDIO", "TEXT"],
            )
        )
    except Exception:
        pass
    configs.append(None)

    for config in configs:
        try:
            kwargs = {"model": LYRIA_MODEL, "contents": prompt}
            if config is not None:
                kwargs["config"] = config
            response = client.models.generate_content(**kwargs)
            break
        except TypeError as exc:
            last_error = exc
            continue
        except Exception as exc:
            last_error = exc
            # If modalities config is rejected, try the next variant.
            if config is not None:
                continue
            raise _friendly_error(exc) from exc

    if response is None:
        raise _friendly_error(last_error or RuntimeError("Lyria returned no response"))

    audio_bytes: Optional[bytes] = None
    mime_type = "audio/mpeg"
    text_parts = []

    parts = []
    try:
        parts = list(response.parts or [])
    except Exception:
        parts = []
    if not parts:
        try:
            candidates = getattr(response, "candidates", None) or []
            if candidates and getattr(candidates[0], "content", None):
                parts = list(candidates[0].content.parts or [])
        except Exception:
            parts = []

    for part in parts:
        text = getattr(part, "text", None)
        if text:
            text_parts.append(text)
            continue
        inline = getattr(part, "inline_data", None) or getattr(part, "inlineData", None)
        if inline is None:
            continue
        data = getattr(inline, "data", None)
        if data is None:
            continue
        if isinstance(data, str):
            import base64

            audio_bytes = base64.b64decode(data)
        else:
            audio_bytes = bytes(data)
        mime_type = getattr(inline, "mime_type", None) or getattr(inline, "mimeType", None) or mime_type

    if audio_bytes is None:
        # Interactions convenience fallback if this SDK version exposes it on generate_content responses.
        generated_audio = getattr(response, "output_audio", None)
        if generated_audio is not None:
            data = getattr(generated_audio, "data", None)
            if isinstance(data, str):
                import base64

                audio_bytes = base64.b64decode(data)
            elif data:
                audio_bytes = bytes(data)
            mime_type = getattr(generated_audio, "mime_type", None) or mime_type
        lyrics_conv = getattr(response, "output_text", None)
        if lyrics_conv:
            text_parts.append(lyrics_conv)

    if not audio_bytes:
        logger.warning("Lyria response contained no audio bytes")
        raise LyriaUnavailableError(
            "Lyria did not return audio for this request. The account may lack Lyria access, or the prompt was filtered. Local LSTM MIDI generation still works.",
            code="no_audio",
        )

    lyrics = "\n\n".join(t.strip() for t in text_parts if t and t.strip())
    if mime_type in {"audio/wav", "audio/x-wav", "audio/wave"}:
        mime_type = "audio/wav"
    elif mime_type in {"audio/mp3", "audio/mpeg", "audio/mpg"}:
        mime_type = "audio/mpeg"
    return audio_bytes, mime_type, lyrics
