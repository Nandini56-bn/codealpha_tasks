"""Structured MusicSpec parsing, genre expansion, and Lyria prompt building."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


SUPPORTED_GENRES = [
    "indian commercial / mass",
    "edm",
    "dj",
    "electronic",
    "classical",
    "cinematic",
    "lo-fi",
    "jazz",
    "rock",
    "hip-hop",
    "pop",
    "folk",
    "ambient",
    "indian classical",
    "orchestral",
]

MASS_TOKENS = (
    "mass",
    "mass music",
    "mass song",
    "mass beat",
    "commercial hit",
    "item song energy",
)


class MusicSpec(BaseModel):
    genre: str = Field(default="pop")
    mood: str = Field(default="energetic")
    language: str = Field(default="English")
    tempo_bpm: Optional[int] = Field(default=None)
    instruments: List[str] = Field(default_factory=list)
    vocals: bool = True
    lyrics_required: bool = False
    duration: str = Field(default="about 45 seconds")
    structure: List[str] = Field(default_factory=list)
    energy: str = Field(default="medium")
    style_description: str = Field(default="")
    vocal_style: Optional[str] = None
    lyrics_topic: Optional[str] = None
    user_intent: str = Field(default="generate_music")
    original_request: str = Field(default="")

    @field_validator("tempo_bpm", mode="before")
    @classmethod
    def _coerce_bpm(cls, value: Any) -> Optional[int]:
        if value is None or value == "":
            return None
        try:
            bpm = int(float(value))
        except (TypeError, ValueError):
            return None
        return max(40, min(220, bpm))

    @field_validator("instruments", "structure", mode="before")
    @classmethod
    def _coerce_list(cls, value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, str):
            parts = [p.strip() for p in value.replace("|", ",").split(",") if p.strip()]
            return parts
        if isinstance(value, list):
            return [str(v).strip() for v in value if str(v).strip()]
        return []

    @field_validator("vocals", "lyrics_required", mode="before")
    @classmethod
    def _coerce_bool(cls, value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        text = str(value).strip().lower()
        return text in {"1", "true", "yes", "y", "on"}


def _contains_mass(text: str) -> bool:
    lowered = (text or "").lower()
    return any(token in lowered for token in MASS_TOKENS)


def apply_mass_and_genre_expansion(spec: MusicSpec) -> MusicSpec:
    """Map informal requests such as 'mass music' into a useful production description.

    Does not name or imitate specific artists or copyrighted songs.
    """
    blob = " ".join(
        [
            spec.genre or "",
            spec.style_description or "",
            spec.original_request or "",
            spec.mood or "",
        ]
    ).lower()

    if _contains_mass(blob) or "indian commercial" in blob:
        spec.genre = "indian commercial / mass"
        extra = (
            "Energetic Indian commercial-style production with powerful percussion, "
            "heavy drums, dhol and toms where appropriate, strong bass, layered synths, "
            "a cinematic intro, an energetic chorus, and a dance-oriented rhythm. "
            "Original composition only. Do not imitate any specific artist, singer, "
            "or copyrighted song."
        )
        if extra.lower() not in (spec.style_description or "").lower():
            spec.style_description = f"{spec.style_description} {extra}".strip()
        if not spec.instruments:
            spec.instruments = ["drums", "dhol", "bass", "synths", "electric guitar"]
        if spec.tempo_bpm is None:
            spec.tempo_bpm = 128
        if spec.energy in {"", "medium"}:
            spec.energy = "high"
        if not spec.mood or spec.mood.lower() in {"neutral", "none"}:
            spec.mood = "heroic, high-energy"

    genre_aliases = {
        "dj": "DJ / club dance beat, DJ mix energy, four-on-the-floor or breakbeat club drums",
        "dj beat": "DJ / club dance beat with punchy kicks and drops",
        "edm": "electronic dance music with synthesized leads, sidechain bass, and club drums",
        "lofi": "lo-fi hip-hop with dusty drums, warm keys, and relaxed groove",
        "lo-fi": "lo-fi hip-hop with dusty drums, warm keys, and relaxed groove",
        "classical": "classical instrumental writing with clear melodic phrasing",
        "indian classical": "Indian classical inspired raga-like melody, tabla or mridangam, tanpura drone; original, not a specific raga recording",
        "cinematic": "cinematic film-score atmosphere with orchestral swells and tension/release",
        "orchestral": "full orchestral arrangement with strings, brass, and percussion",
    }
    key = (spec.genre or "").strip().lower()
    if key in genre_aliases:
        hint = genre_aliases[key]
        if hint.lower() not in (spec.style_description or "").lower():
            spec.style_description = f"{spec.style_description} {hint}".strip()

    return spec


def default_structure(vocals: bool) -> List[str]:
    if vocals:
        return ["Intro", "Verse", "Pre-Chorus", "Chorus", "Verse", "Bridge", "Final Chorus", "Outro"]
    return ["Intro", "Main Theme", "Build", "Drop", "Breakdown", "Final Theme", "Outro"]


def build_lyria_prompt(spec: MusicSpec, lyrics: Optional[str] = None) -> str:
    spec = apply_mass_and_genre_expansion(spec.model_copy(deep=True))
    sections = spec.structure or default_structure(bool(spec.vocals or spec.lyrics_required or lyrics))
    structure_line = " -> ".join(f"[{s.strip()}]" for s in sections if s.strip())
    instruments = ", ".join(spec.instruments) if spec.instruments else "genre-appropriate instrumentation"
    bpm_line = f"Tempo around {spec.tempo_bpm} BPM." if spec.tempo_bpm else "Choose a tempo that fits the mood."
    vocal_line = "Instrumental only. No sung lyrics."
    if spec.vocals or lyrics or spec.lyrics_required:
        vocal_line = "Include vocals."
        if spec.vocal_style:
            vocal_line += f" Vocal style: {spec.vocal_style}."
        if not lyrics:
            vocal_line += " Write original lyrics. Do not copy or imitate existing copyrighted songs."
            if spec.lyrics_topic:
                vocal_line += f" Lyrics topic: {spec.lyrics_topic}."
            if spec.language:
                vocal_line += f" Write the lyrics in {spec.language}."
    elif spec.language:
        vocal_line += f" Musical character may reflect {spec.language} popular music aesthetics without copying songs."

    duration = spec.duration or "about 45 seconds"
    prompt = (
        f"Create an original {duration} song.\n"
        f"Genre: {spec.genre}.\n"
        f"Mood: {spec.mood}. Energy: {spec.energy}.\n"
        f"Language context: {spec.language}.\n"
        f"Instruments to feature in the mix (this is a mixed stereo song, not isolated stems): {instruments}.\n"
        f"{bpm_line}\n"
        f"Song structure: {structure_line}.\n"
        f"{vocal_line}\n"
        f"Style: {spec.style_description or spec.genre}.\n"
        "Original composition only. Do not imitate a specific artist, singer, or copyrighted melody.\n"
    )
    if spec.original_request:
        prompt += f"User request (may be mixed language): {spec.original_request}\n"
    if lyrics and lyrics.strip():
        prompt += "\nUse these approved original lyrics exactly, with section tags:\nLyrics:\n"
        prompt += lyrics.strip() + "\n"
    return prompt.strip()


def spec_to_public_dict(spec: MusicSpec) -> Dict[str, Any]:
    return spec.model_dump()
