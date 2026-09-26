from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.app.ai.errors import user_facing_error
from backend.app.ai.gemini_director import chat_about_music, gemini_configured, interpret_request
from backend.app.ai.music_spec import build_lyria_prompt, spec_to_public_dict

router = APIRouter(prefix="/api/chat", tags=["AI Music Assistant"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User question or natural-language music request")
    interpret: bool = Field(default=True, description="Also parse a MusicSpec when the message looks like a generation request")


@router.post("")
async def chat_endpoint(request: ChatRequest):
    """
    Gemini chatbot: mixed-language conversation + MusicSpec parsing.
    Gemini does not synthesize audio. Lyria / LSTM do that on dedicated endpoints.
    """
    if not gemini_configured():
        return {
            "status": "error",
            "reply": "Google Gemini API Key is not configured in backend .env file. Please add your GEMINI_API_KEY in the backend .env file to enable live AI Assistant responses.",
            "api_key_missing": True,
        }

    try:
        spec = None
        intent = "chat"
        reply = ""
        if request.interpret:
            spec, reply, intent = interpret_request(request.message)
        if intent == "chat" or not spec:
            reply = chat_about_music(request.message)
            return {
                "status": "success",
                "reply": reply,
                "api_key_missing": False,
                "user_intent": "chat",
                "music_spec": None,
            }
        return {
            "status": "success",
            "reply": reply,
            "api_key_missing": False,
            "user_intent": intent,
            "music_spec": spec_to_public_dict(spec),
            "lyria_prompt": build_lyria_prompt(spec),
        }
    except Exception as e:
        try:
            reply = chat_about_music(request.message)
            return {
                "status": "success",
                "reply": reply,
                "api_key_missing": False,
                "user_intent": "chat",
                "music_spec": None,
            }
        except Exception:
            return {
                "status": "error",
                "reply": user_facing_error(e),
                "api_key_missing": False,
            }
