from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.app.utils.config import GENERATED_DIR, BASE_DIR, DEBUG
from backend.app.api.routes_music import router as music_router
from backend.app.api.routes_chat import router as chat_router
from backend.app.ai.history_db import init_db

FRONTEND_DIR = BASE_DIR / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="AI Music Festival API",
    description="Local LSTM MIDI generation plus Gemini director and Lyria 3.5 song generation",
    version="2.0.0",
    debug=DEBUG,
    lifespan=lifespan,
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers & Endpoints
app.include_router(music_router)
app.include_router(chat_router)

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "AI Music Studio"}

# Mount static file server for generated MIDI downloads
app.mount("/static/generated", StaticFiles(directory=str(GENERATED_DIR)), name="generated_static")

# Mount static file server for full frontend web UI (MUST BE MOUNTED LAST)
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend_static")
