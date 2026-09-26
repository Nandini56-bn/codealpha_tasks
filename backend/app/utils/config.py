import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
BACKEND_DIR = BASE_DIR / "backend"
DATA_DIR = BACKEND_DIR / "data"
RAW_MIDI_DIR = DATA_DIR / "raw_midi"
PROCESSED_DIR = DATA_DIR / "processed"
MODEL_DIR = BACKEND_DIR / "model_checkpoints"
GENERATED_DIR = BACKEND_DIR / "generated"

# Load environment variables from root .env if present
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Server Configuration
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# Gemini API Configuration (server-side only; never expose to the frontend)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_DIRECTOR_MODEL = os.getenv("GEMINI_DIRECTOR_MODEL", "gemini-flash-latest").strip()
LYRIA_MODEL = os.getenv("LYRIA_MODEL", "lyria-3.5").strip()
HISTORY_DB_PATH = PROCESSED_DIR / "history.db"

# Ensure critical directories exist
for directory in [RAW_MIDI_DIR, PROCESSED_DIR, MODEL_DIR, GENERATED_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
