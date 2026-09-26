from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_check_endpoint():
    """Test health check route."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "AI Music Studio"}

def test_music_generate_and_download_endpoints():
    """Test full POST /api/music/generate and GET /api/music/download endpoints."""
    payload = {
        "generate_length": 32,
        "creativity": 1.0,
        "genre": "Classical Bach",
        "instrument": "Piano"
    }
    
    response = client.post("/api/music/generate", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "filename" in data
    assert "download_url" in data
    assert data["note_count"] == 32
    
    # Test downloading generated file via REST route
    download_url = data["download_url"]
    dl_response = client.get(download_url)
    assert dl_response.status_code == 200
    assert dl_response.headers["content-type"] in ["audio/midi", "audio/x-midi", "application/x-midi"]
    assert len(dl_response.content) > 0

def test_chat_endpoint_missing_key_response():
    """Test chatbot endpoint handling when API key is missing or default."""
    response = client.post("/api/chat", json={"message": "What is an LSTM?"})
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "reply" in data
