# AI Music Festival – Virtual Cartoon Band

![CodeAlpha Internship](https://img.shields.io/badge/CodeAlpha-AI--Internship--Task3-6366f1)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-orange)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-emerald)

Full-stack **CodeAlpha Artificial Intelligence Internship Task 3** app: a locally trained **PyTorch LSTM MIDI generator** plus an optional **Google Gemini director** and **Lyria 3.5** song generator.

There are two honest generation modes. They are not interchangeable.

| Mode | Label in UI | What it actually produces |
| :--- | :--- | :--- |
| Local LSTM | **Local LSTM MIDI Generator – CodeAlpha Task 3** | New **MIDI** piano sequences in the trained Bach style |
| Foundation audio | **AI Song Generator** | Mixed **stereo audio** from official model `lyria-3.5` |

Gemini is **not** the music synthesizer. It parses mixed-language requests into a MusicSpec and can write original lyrics. Lyria generates audio. If Lyria is unavailable, the app says so; it does **not** silently play LSTM MIDI and call it mass/EDM.

---

## Architecture

```
User request (English / Telugu / mixed)
        ↓
Gemini Music Director  →  MusicSpec JSON  →  optional original lyrics
        ↓
Lyria 3.5 (generateContent)  →  MP3/WAV + lyrics/structure text
        ↓
Player + AnalyserNode visualizer + cartoon concert stage

Parallel path (always offline):
POST /api/music/generate  →  PyTorch LSTM  →  .mid  →  Tone.js playback
```

Official Lyria docs used:

- https://ai.google.dev/gemini-api/docs/generate-content/music-generation
- https://ai.google.dev/gemini-api/docs/models/lyria-3.5
- https://ai.google.dev/gemini-api/docs/lyria-prompt-guide

SDK call: `google.genai.Client(...).models.generate_content(model="lyria-3.5", contents=prompt, ...)`.

---

## Features that are implemented

* Local LSTM MIDI generation, download, Tone.js playback, note-event band animation
* Gemini mixed-language chatbot and MusicSpec parsing (`/api/chat`, `/api/music/interpret`)
* Original lyrics generate / edit / regenerate / `.txt` download
* Lyria 3.5 job-based audio generation (`/api/music/generate-ai` + `/api/music/status/{job_id}`)
* HTML5 audio player with seek, volume, replay, audio download
* AnalyserNode spectrum visualizer for generated audio (labeled separately from the MIDI visualizer)
* SQLite generation history with replay
* Concert stage (original fictional musicians), performance mode, spotlights, LED wall
* Honest errors for missing key, quota, missing files, invalid jobs

Not claimed:

* Isolated instrument stems (Lyria returns a mixed song)
* A local multi-genre LSTM (jazz/ragtime leftovers are not live models)
* Artist or copyrighted-song imitation

---

## Setup

```bash
pip install -r requirements.txt
Copy-Item .env.example .env   # Windows PowerShell
```

Edit `.env` (server-side only; never sent to the browser):

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_DIRECTOR_MODEL=gemini-flash-latest
LYRIA_MODEL=lyria-3.5
```

Get a key at https://aistudio.google.com/. Lyria access and quota depend on the Google account. Without a key, LSTM MIDI still works.

---

## Run

```bash
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000/**

---

## Tests

```bash
python -m pytest
```

---

## API

| Method | Path | Role |
| :--- | :--- | :--- |
| GET | `/api/health` | Health |
| GET | `/api/music/capabilities` | Which backends are configured |
| POST | `/api/music/generate` | Local LSTM MIDI |
| POST | `/api/music/interpret` | Gemini → MusicSpec |
| POST | `/api/music/lyrics` | Original lyrics |
| POST | `/api/music/generate-ai` | Queue Lyria 3.5 job |
| GET | `/api/music/status/{job_id}` | Job status |
| GET | `/api/music/download/{file}` | MIDI, audio, or lyrics |
| GET | `/api/music/history` | SQLite + legacy JSON history |
| POST | `/api/chat` | Gemini assistant + MusicSpec |

`GEMINI_API_KEY` is read only in Python from `.env`.

---

## Limitations

* LSTM output is Bach-style piano MIDI, not modern mass/DJ audio.
* Duration/BPM/genre for Lyria are **prompt controls**, matching the official API (no separate undocumented duration field).
* Full-length Lyria songs can take a long time and may be blocked by quota, billing, or account access.
* Visual band members represent selected/detected instruments; they are not separate generated tracks.

See [`dataset_provenance.md`](dataset_provenance.md) for training-data honesty.
