"""Gemini-powered music director: multilingual intent parsing, chat, and lyrics.

Gemini is NOT the audio generator. It turns natural language into MusicSpec / lyrics.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional, Tuple

from backend.app.ai.music_spec import MusicSpec, apply_mass_and_genre_expansion, default_structure
from backend.app.utils.config import GEMINI_API_KEY, GEMINI_DIRECTOR_MODEL


DIRECTOR_SYSTEM = """You are the AI Music Director for AI Music Festival.
The user may write in English, Telugu, Hinglish, or mixed languages.
You understand informal South Indian English/Telugu requests such as "naku oka mass music kavali".
You are NOT a music synthesizer. You convert requests into a structured MusicSpec JSON.

Return ONLY valid JSON with this schema:
{
  "assistant_reply": "short helpful reply in the user's language mix",
  "user_intent": "generate_music | generate_lyrics | chat | interpret",
  "genre": "string",
  "mood": "string",
  "language": "string",
  "tempo_bpm": 120 or null,
  "instruments": ["drums", "bass"],
  "vocals": true,
  "lyrics_required": false,
  "duration": "about 45 seconds",
  "structure": ["Intro", "Verse", "Chorus"],
  "energy": "low|medium|high",
  "style_description": "detailed original-style production description",
  "vocal_style": "string or null",
  "lyrics_topic": "string or null"
}

Rules:
- "mass" / "mass music" means energetic Indian commercial-style production with powerful percussion, heavy drums, dhol/toms where appropriate, strong bass, synth layers, cinematic intro, energetic chorus, dance-oriented rhythm. Never name or imitate a specific artist or copyrighted song.
- Map DJ/EDM/classical/cinematic/lo-fi/jazz/rock/hip-hop/pop/folk/ambient/Indian classical/orchestral naturally.
- If the user asks only a question about the LSTM/MIDI app, set user_intent to "chat".
- If they ask to generate lyrics only, user_intent is "generate_lyrics".
- If they ask to make/generate music/song/beat, user_intent is "generate_music".
- Never copy copyrighted lyrics. Original writing only.
- tempo_bpm must be an integer between 40 and 220 or null.
"""

LYRICS_SYSTEM = """You write original song lyrics for AI music generation.
Never copy or imitate existing copyrighted songs or famous hooks.
Support English, Telugu, and mixed-language requests.
Use this structure with tags:
[Intro]
[Verse]
[Pre-Chorus]
[Chorus]
[Verse]
[Bridge]
[Final Chorus]
[Outro]
Return only the lyrics, no commentary.
"""


def gemini_configured() -> bool:
    return bool(GEMINI_API_KEY) and GEMINI_API_KEY != "your_gemini_api_key_here"


def _extract_json_object(text: str) -> Dict[str, Any]:
    if not text:
        raise ValueError("Empty model response")
    cleaned = text.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
    if fence:
        cleaned = fence.group(1)
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("Model did not return JSON")
    return json.loads(cleaned[start : end + 1])


def _client():
    from google import genai

    return genai.Client(api_key=GEMINI_API_KEY)


def _generate_text(system_instruction: str, user_text: str, temperature: float = 0.4, max_tokens: int = 1200) -> str:
    from google import genai

    client = _client()
    want_json = "Return ONLY valid JSON" in system_instruction
    candidate_models = [GEMINI_DIRECTOR_MODEL, "gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-flash-latest", "gemini-flash-lite-latest", "gemini-3.1-flash-lite"]
    last_error = None

    for model_name in candidate_models:
        try:
            cfg_kwargs = {
                "system_instruction": system_instruction,
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
            if want_json:
                cfg_kwargs["response_mime_type"] = "application/json"
            response = client.models.generate_content(
                model=model_name,
                contents=user_text,
                config=genai.types.GenerateContentConfig(**cfg_kwargs),
            )
            text = getattr(response, "text", None)
            if text:
                return text
        except Exception as e:
            last_error = e
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=f"{system_instruction}\n\nUser:\n{user_text}",
                    config=genai.types.GenerateContentConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens,
                    ),
                )
                text = getattr(response, "text", None)
                if text:
                    return text
            except Exception as e2:
                last_error = e2
                continue

    if last_error:
        raise last_error
    raise RuntimeError("Gemini returned an empty response.")


def interpret_request(user_message: str, hint_spec: Optional[Dict[str, Any]] = None) -> Tuple[MusicSpec, str, str]:
    """Return (spec, assistant_reply, user_intent)."""
    hint = ""
    if hint_spec:
        hint = f"\nOptional UI field hints (override only if the user request disagrees):\n{json.dumps(hint_spec)}"
    raw = _generate_text(DIRECTOR_SYSTEM, user_message + hint, temperature=0.3, max_tokens=1400)
    data = _extract_json_object(raw)
    intent = str(data.get("user_intent") or "generate_music").strip().lower()
    reply = str(data.get("assistant_reply") or "I understood your music request.")
    spec = MusicSpec(
        genre=data.get("genre") or "pop",
        mood=data.get("mood") or "energetic",
        language=data.get("language") or "English",
        tempo_bpm=data.get("tempo_bpm"),
        instruments=data.get("instruments") or [],
        vocals=data.get("vocals", True),
        lyrics_required=data.get("lyrics_required", False),
        duration=data.get("duration") or "about 45 seconds",
        structure=data.get("structure") or [],
        energy=data.get("energy") or "medium",
        style_description=data.get("style_description") or "",
        vocal_style=data.get("vocal_style"),
        lyrics_topic=data.get("lyrics_topic"),
        user_intent=intent,
        original_request=user_message,
    )
    if not spec.structure:
        spec.structure = default_structure(spec.vocals or spec.lyrics_required)
    spec = apply_mass_and_genre_expansion(spec)
    return spec, reply, intent


def generate_lyrics(user_message: str, spec: Optional[MusicSpec] = None, previous_lyrics: Optional[str] = None) -> str:
    payload = {
        "request": user_message,
        "music_spec": spec.model_dump() if spec else None,
        "regenerate_from": previous_lyrics,
        "instruction": "Write original lyrics. Do not copy copyrighted songs.",
    }
    text = _generate_text(LYRICS_SYSTEM, json.dumps(payload, ensure_ascii=False), temperature=0.9, max_tokens=2000)
    # Lyrics mode may accidentally wrap JSON; unwrap if needed.
    stripped = text.strip()
    if stripped.startswith("{") and "lyrics" in stripped.lower():
        try:
            obj = _extract_json_object(stripped)
            for key in ("lyrics", "text", "content"):
                if isinstance(obj.get(key), str) and obj[key].strip():
                    return obj[key].strip()
        except Exception:
            pass
    if stripped.startswith("```"):
        stripped = re.sub(r"^```[a-zA-Z]*\n?", "", stripped)
        stripped = re.sub(r"\n?```$", "", stripped)
    return stripped.strip()


def chat_about_music(user_message: str) -> str:
    from google import genai

    client = _client()
    system_instruction = (
        "You are the AI Music Festival assistant. Help with natural-language music requests "
        "(English/Telugu/mixed), the local PyTorch LSTM MIDI generator, Lyria AI song generation, "
        "lyrics workflow, and concert-stage playback. Be concise. Do not invent audio that was not generated."
    )
    candidate_models = [GEMINI_DIRECTOR_MODEL, "gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-flash-latest", "gemini-flash-lite-latest", "gemini-3.1-flash-lite"]
    for model_name in candidate_models:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=user_message,
                config=genai.types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                    max_output_tokens=700,
                ),
            )
            if response and getattr(response, "text", None):
                return response.text.strip()
        except Exception:
            continue
    return "I am your AI Music Festival Assistant! Tell me what style of music you want to generate."
