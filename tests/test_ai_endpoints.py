from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.utils.config import GENERATED_DIR
from backend.app.ai.history_db import add_generation, list_generations

client = TestClient(app)


def test_capabilities_endpoint():
    response = client.get("/api/music/capabilities")
    assert response.status_code == 200
    data = response.json()
    assert data["lstm"]["available"] is True
    assert "midi" in data["lstm"]["output"]
    assert "lyria" in data
    assert "api_key_configured" in data


def test_interpret_without_key_is_honest():
    response = client.post("/api/music/interpret", json={"message": "naku oka mass music kavali"})
    assert response.status_code in (200, 502)
    if response.status_code == 200:
        data = response.json()
        if data.get("api_key_missing"):
            assert data["status"] == "error"
            assert "GEMINI_API_KEY" in data["message"]
            assert "LSTM" in data["message"]
        else:
            assert data["status"] == "success"
            assert "music_spec" in data


def test_generate_ai_without_key_does_not_fake_lstm():
    response = client.post(
        "/api/music/generate-ai",
        json={"message": "make me a DJ beat with energetic drums"},
    )
    assert response.status_code in (200, 502)
    if response.status_code == 200:
        data = response.json()
        if data.get("api_key_missing"):
            assert data["status"] == "error"
            assert "Lyria" in data["message"]
            assert "not faked" in data["message"].lower() or "LSTM" in data["message"]
        else:
            assert data.get("job_id")
            assert data.get("output_type") == "audio"


def test_lyrics_without_key_is_honest():
    response = client.post("/api/music/lyrics", json={"message": "Telugu lyrics generate cheyyi"})
    assert response.status_code in (200, 502)
    if response.status_code == 200:
        data = response.json()
        if data.get("api_key_missing"):
            assert data["status"] == "error"
        else:
            assert data.get("lyrics")


def test_job_status_unknown():
    response = client.get("/api/music/status/does-not-exist")
    assert response.status_code == 404


def test_download_missing_file():
    response = client.get("/api/music/download/missing_file.mp3")
    assert response.status_code == 404
    assert "audio" in response.json()["detail"].lower() or "not found" in response.json()["detail"].lower()


def test_download_generated_audio_and_lyrics_files():
    audio_name = "test_audio_fixture.mp3"
    lyrics_name = "test_lyrics_fixture.txt"
    (GENERATED_DIR / audio_name).write_bytes(b"ID3fakeaudio")
    (GENERATED_DIR / lyrics_name).write_text("[Verse]\noriginal line\n", encoding="utf-8")

    audio_res = client.get(f"/api/music/download/{audio_name}")
    assert audio_res.status_code == 200
    assert audio_res.headers["content-type"].startswith("audio/")
    assert audio_res.content == b"ID3fakeaudio"

    lyrics_res = client.get(f"/api/music/download/{lyrics_name}")
    assert lyrics_res.status_code == 200
    assert "original line" in lyrics_res.text


def test_history_sqlite_roundtrip():
    add_generation(
        item_id="histtest01",
        mode="lyria",
        genre="edm",
        model="lyria-3.5",
        filename="song_histtest01.mp3",
        lyrics="[Chorus]\nGo",
        user_request="Create DJ Beat",
        metadata={"download_url": "/api/music/download/song_histtest01.mp3"},
    )
    items = list_generations(10)
    assert any(i["id"] == "histtest01" for i in items)

    response = client.get("/api/music/history")
    assert response.status_code == 200
    history = response.json()["history"]
    assert isinstance(history, list)
    assert any(item.get("id") == "histtest01" or item.get("filename") == "song_histtest01.mp3" for item in history)


def test_invalid_generate_ai_payload():
    response = client.post("/api/music/generate-ai", json={"message": "", "spec": None})
    # Missing key returns 200 honest error; with key, empty payload is 400
    assert response.status_code in (200, 400)
