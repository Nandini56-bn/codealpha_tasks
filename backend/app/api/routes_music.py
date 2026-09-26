import json
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel, Field

from backend.app.ai.errors import user_facing_error
from backend.app.ai.gemini_director import gemini_configured, generate_lyrics, interpret_request
from backend.app.ai.generator import generate_ai_music
from backend.app.ai.history_db import add_generation, list_generations
from backend.app.ai.jobs import create_job, get_job, run_in_background, update_job
from backend.app.ai.lyria_client import LyriaUnavailableError, generate_lyria_song
from backend.app.ai.music_spec import MusicSpec, apply_mass_and_genre_expansion, build_lyria_prompt, spec_to_public_dict
from backend.app.utils.config import GENERATED_DIR, GEMINI_DIRECTOR_MODEL, LYRIA_MODEL, PROCESSED_DIR

router = APIRouter(prefix="/api/music", tags=["Music Generation"])

HISTORY_FILE = PROCESSED_DIR / "history.json"


class MusicGenerateRequest(BaseModel):
    generate_length: int = Field(default=64, ge=16, le=256, description="Number of note steps to generate")
    creativity: float = Field(default=1.0, ge=0.1, le=2.0, description="Temperature scaling factor for model sampling")
    genre: str = Field(default="Classical Bach", description="Style representation")
    instrument: str = Field(default="Piano", description="Primary active instrument")
    user_request: Optional[str] = None


class InterpretRequest(BaseModel):
    message: str = Field(..., min_length=1)
    hint: Optional[Dict[str, Any]] = None


class LyricsRequest(BaseModel):
    message: str = Field(..., min_length=1)
    spec: Optional[Dict[str, Any]] = None
    previous_lyrics: Optional[str] = None


class AIGenerateRequest(BaseModel):
    message: str = Field(default="", description="Natural language request")
    spec: Optional[Dict[str, Any]] = None
    lyrics: Optional[str] = None
    generate_lyrics: bool = False


def _load_json_history() -> List[dict]:
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def _save_json_history(entry: dict) -> None:
    history = _load_json_history()
    history.insert(0, entry)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history[:50], f, indent=2)


def _extension_for_mime(mime_type: str) -> str:
    if mime_type in {"audio/wav", "audio/x-wav", "audio/wave"}:
        return ".wav"
    return ".mp3"


def _media_type_for_filename(filename: str) -> str:
    lower = filename.lower()
    if lower.endswith(".mid") or lower.endswith(".midi"):
        return "audio/midi"
    if lower.endswith(".wav"):
        return "audio/wav"
    if lower.endswith(".txt"):
        return "text/plain"
    return "audio/mpeg"


@router.get("/capabilities")
async def capabilities_endpoint():
    return {
        "lstm": {
            "available": True,
            "label": "Local LSTM MIDI Generator – CodeAlpha Task 3",
            "output": "midi",
            "style": "Classical Bach piano sequences from the trained local checkpoint",
        },
        "gemini_director": {
            "available": gemini_configured(),
            "model": GEMINI_DIRECTOR_MODEL,
            "role": "Intent parser / lyrics writer. Not the audio generator.",
        },
        "lyria": {
            "available": gemini_configured(),
            "model": LYRIA_MODEL,
            "label": "AI Song Generator",
            "output": "audio",
            "note": "Availability also depends on account access and quota. Missing access is reported honestly.",
        },
        "api_key_configured": gemini_configured(),
    }


@router.post("/generate")
async def generate_music_endpoint(request: MusicGenerateRequest):
    """
    Triggers local PyTorch LSTM model generation and returns metadata with MIDI download path.
    """
    try:
        job_id = str(uuid.uuid4())[:8]
        filename = f"composition_{job_id}.mid"

        result = generate_ai_music(
            generate_length=request.generate_length,
            temperature=request.creativity,
            output_filename=filename,
        )

        history_entry = {
            "id": job_id,
            "filename": filename,
            "composition_name": f"Bach AI Study #{job_id}",
            "genre": request.genre,
            "instrument": request.instrument,
            "note_count": result["note_count"],
            "duration_seconds": result["estimated_duration_seconds"],
            "creativity": request.creativity,
            "download_url": f"/api/music/download/{filename}",
            "static_url": f"/static/generated/{filename}",
            "preview_notes": result["generated_notes"],
            "mode": "lstm",
            "model": "local-pytorch-lstm",
            "output_type": "midi",
            "user_request": request.user_request or "Local LSTM MIDI generation",
        }

        _save_json_history(history_entry)
        add_generation(
            item_id=job_id,
            mode="lstm",
            genre=request.genre,
            model="local-pytorch-lstm",
            filename=filename,
            lyrics=None,
            user_request=history_entry["user_request"],
            metadata=history_entry,
        )
        return history_entry

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Music generation failed: {user_facing_error(e)}")


@router.post("/interpret")
async def interpret_endpoint(request: InterpretRequest):
    if not gemini_configured():
        return {
            "status": "error",
            "api_key_missing": True,
            "message": "GEMINI_API_KEY is not configured. The director cannot parse mixed-language requests until you add a key to .env. Local LSTM MIDI generation still works.",
        }
    try:
        spec, reply, intent = interpret_request(request.message, request.hint)
        return {
            "status": "success",
            "assistant_reply": reply,
            "user_intent": intent,
            "music_spec": spec_to_public_dict(spec),
            "lyria_prompt": build_lyria_prompt(spec),
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail=user_facing_error(e))


@router.post("/lyrics")
async def lyrics_endpoint(request: LyricsRequest):
    if not gemini_configured():
        return {
            "status": "error",
            "api_key_missing": True,
            "message": "GEMINI_API_KEY is not configured. Lyrics generation requires Gemini. Local LSTM MIDI generation still works.",
        }
    try:
        spec = None
        if request.spec:
            spec = apply_mass_and_genre_expansion(MusicSpec(**request.spec, original_request=request.message))
        lyrics = generate_lyrics(request.message, spec=spec, previous_lyrics=request.previous_lyrics)
        file_id = uuid.uuid4().hex[:10]
        filename = f"lyrics_{file_id}.txt"
        path = GENERATED_DIR / filename
        path.write_text(lyrics, encoding="utf-8")
        return {
            "status": "success",
            "lyrics": lyrics,
            "filename": filename,
            "download_url": f"/api/music/download/{filename}",
            "music_spec": spec_to_public_dict(spec) if spec else None,
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail=user_facing_error(e))


def _run_lyria_job(job_id: str, message: str, spec_dict: Optional[Dict[str, Any]], lyrics: Optional[str], want_lyrics: bool) -> None:
    spec = MusicSpec(**(spec_dict or {}), original_request=message or (spec_dict or {}).get("original_request") or "")
    spec = apply_mass_and_genre_expansion(spec)
    used_lyrics = lyrics
    if want_lyrics and not used_lyrics:
        if not gemini_configured():
            raise LyriaUnavailableError(
                "GEMINI_API_KEY is required to generate lyrics before Lyria synthesis.",
                code="missing_or_invalid_key",
            )
        update_job(job_id, message="Writing original lyrics with Gemini...")
        used_lyrics = generate_lyrics(message or spec.style_description, spec=spec)

    prompt = build_lyria_prompt(spec, lyrics=used_lyrics)
    update_job(job_id, message="Calling Lyria 3.5 (this can take a while)...")
    audio_bytes, mime_type, returned_text = generate_lyria_song(prompt)
    ext = _extension_for_mime(mime_type)
    filename = f"song_{job_id}{ext}"
    path = GENERATED_DIR / filename
    path.write_bytes(audio_bytes)

    final_lyrics = used_lyrics or returned_text or ""
    lyrics_filename = None
    if final_lyrics.strip():
        lyrics_filename = f"lyrics_{job_id}.txt"
        (GENERATED_DIR / lyrics_filename).write_text(final_lyrics, encoding="utf-8")

    result = {
        "id": job_id,
        "mode": "lyria",
        "output_type": "audio",
        "model": LYRIA_MODEL,
        "genre": spec.genre,
        "filename": filename,
        "composition_name": f"AI Song #{job_id}",
        "download_url": f"/api/music/download/{filename}",
        "static_url": f"/static/generated/{filename}",
        "mime_type": mime_type,
        "lyrics": final_lyrics,
        "lyrics_download_url": f"/api/music/download/{lyrics_filename}" if lyrics_filename else None,
        "music_spec": spec_to_public_dict(spec),
        "user_request": message,
        "prompt_used": prompt,
    }
    add_generation(
        item_id=job_id,
        mode="lyria",
        genre=spec.genre,
        model=LYRIA_MODEL,
        filename=filename,
        lyrics=final_lyrics,
        user_request=message,
        metadata=result,
    )
    update_job(job_id, status="succeeded", message="Song ready", result=result, error=None)


@router.post("/generate-ai")
async def generate_ai_song_endpoint(request: AIGenerateRequest):
    if not gemini_configured():
        return {
            "status": "error",
            "api_key_missing": True,
            "error_code": "missing_or_invalid_key",
            "message": "AI Song Generator (Lyria 3.5) needs GEMINI_API_KEY in .env. This is not faked with the local LSTM. Use Local LSTM MIDI Generator for Bach piano MIDI, or add an API key for Lyria.",
        }

    spec_dict = dict(request.spec or {})
    message = request.message.strip()
    if not spec_dict and not message:
        raise HTTPException(status_code=400, detail="Provide a natural-language message or a music spec.")

    if message and not spec_dict:
        try:
            spec, _, _ = interpret_request(message)
            spec_dict = spec_to_public_dict(spec)
        except Exception as e:
            raise HTTPException(status_code=502, detail=user_facing_error(e))

    job_id = create_job("lyria", {"message": message, "spec": spec_dict})
    lyrics = request.lyrics
    want_lyrics = request.generate_lyrics or bool(spec_dict.get("lyrics_required"))

    def worker() -> None:
        _run_lyria_job(job_id, message, spec_dict, lyrics, want_lyrics)

    run_in_background(job_id, worker)
    return {
        "status": "queued",
        "job_id": job_id,
        "status_url": f"/api/music/status/{job_id}",
        "music_spec": spec_dict,
        "model": LYRIA_MODEL,
        "output_type": "audio",
        "message": "Lyria 3.5 generation started. Poll the status URL until it succeeds or fails.",
    }


@router.get("/status/{job_id}")
async def job_status_endpoint(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Generation job not found.")
    return job


@router.get("/download/{filename}")
async def download_midi_endpoint(filename: str):
    """Download generated MIDI, audio, or lyrics files. Never returns a traceback."""
    safe_name = filename.replace("\\", "/").split("/")[-1]
    if not safe_name or ".." in safe_name:
        raise HTTPException(status_code=400, detail="Invalid file name.")
    file_path = GENERATED_DIR / safe_name
    if not file_path.exists() or not file_path.is_file():
        kind = "audio" if safe_name.lower().endswith((".mp3", ".wav")) else "MIDI" if safe_name.lower().endswith((".mid", ".midi")) else "file"
        raise HTTPException(status_code=404, detail=f"Requested {kind} was not found.")

    return FileResponse(
        path=file_path,
        filename=safe_name,
        media_type=_media_type_for_filename(safe_name),
    )


@router.get("/history")
async def get_history_endpoint():
    sqlite_items = list_generations(50)
    if sqlite_items:
        normalized = []
        for item in sqlite_items:
            meta = item.get("metadata") or {}
            merged = {**meta, **{k: v for k, v in item.items() if k != "metadata"}}
            merged["metadata"] = meta
            normalized.append(merged)
        return {"history": normalized}
    return {"history": _load_json_history()}
