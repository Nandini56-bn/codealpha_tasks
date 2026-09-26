import sys
import json
import urllib.request
from pathlib import Path
from music21 import converter

BASE_URL = "http://127.0.0.1:8000"

def test_frontend_index_html():
    print("[1/5] Testing Frontend UI Landing Page (http://127.0.0.1:8000/)...")
    req = urllib.request.Request(f"{BASE_URL}/")
    with urllib.request.urlopen(req) as response:
        assert response.status == 200
        html = response.read().decode('utf-8')
        
        # Verify essential UI IDs and script tags
        required_elements = [
          "generate-btn", "player-card", "musicians-row", "visualizer-canvas",
          "chat-input", "Tone.js", "@tonejs/midi", "audio_engine.js", "band_animator.js"
        ]
        for elem in required_elements:
            assert elem in html, f"Missing UI component: {elem}"
            
    print("  [SUCCESS] Frontend index.html served cleanly with all required elements and CDN scripts.")

def test_api_music_generation():
    print("[2/5] Testing AI Music Generation Endpoint (POST /api/music/generate)...")
    payload = json.dumps({
        "generate_length": 64,
        "creativity": 1.2,
        "genre": "Classical Bach",
        "instrument": "Piano"
    }).encode('utf-8')
    
    req = urllib.request.Request(
        f"{BASE_URL}/api/music/generate",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    
    with urllib.request.urlopen(req) as response:
        assert response.status == 200
        data = json.loads(response.read().decode('utf-8'))
        
        assert "filename" in data
        assert "download_url" in data
        assert data["note_count"] == 64
        assert data["creativity"] == 1.2
        print(f"  [SUCCESS] Model generated composition '{data['composition_name']}' ({data['note_count']} notes, duration: {data['duration_seconds']}s).")
        return data

def test_midi_download_and_parsing(gen_data):
    print("[3/5] Testing Generated MIDI Download & music21 Structure...")
    download_url = f"{BASE_URL}{gen_data['download_url']}"
    
    with urllib.request.urlopen(download_url) as response:
        assert response.status == 200
        midi_binary = response.read()
        assert len(midi_binary) > 0
        
        # Save temporary file and verify music21 parser
        temp_midi_path = Path("temp_e2e_verify.mid")
        temp_midi_path.write_bytes(midi_binary)
        
        score = converter.parse(temp_midi_path)
        assert score is not None
        
        if temp_midi_path.exists():
            temp_midi_path.unlink()
            
    print(f"  [SUCCESS] MIDI binary downloaded ({len(midi_binary)} bytes) and successfully parsed by music21.")

def test_chat_endpoint():
    print("[4/5] Testing Gemini AI Chatbot Endpoint (POST /api/chat)...")
    payload = json.dumps({"message": "What is an LSTM neural network?"}).encode('utf-8')
    req = urllib.request.Request(
        f"{BASE_URL}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    
    with urllib.request.urlopen(req) as response:
        assert response.status == 200
        data = json.loads(response.read().decode('utf-8'))
        assert "status" in data
        assert "reply" in data
        print(f"  [SUCCESS] Chatbot endpoint returned status '{data['status']}' with reply message.")

def test_static_asset_serving():
    print("[5/5] Testing Static Frontend Assets Serving...")
    asset_urls = [
        f"{BASE_URL}/css/styles.css",
        f"{BASE_URL}/css/band.css",
        f"{BASE_URL}/css/visualizer.css",
        f"{BASE_URL}/js/app.js",
        f"{BASE_URL}/js/audio_engine.js",
        f"{BASE_URL}/js/band_animator.js",
        f"{BASE_URL}/js/visualizer.js",
        f"{BASE_URL}/js/chat.js"
    ]
    
    for url in asset_urls:
        with urllib.request.urlopen(url) as response:
            assert response.status == 200
            content = response.read()
            assert len(content) > 0
            
    print("  [SUCCESS] All CSS and JS frontend assets served with HTTP 200 OK.")

if __name__ == "__main__":
    print("==================================================")
    print("  AI MUSIC STUDIO END-TO-END VERIFICATION SUITE")
    print("==================================================")
    test_frontend_index_html()
    gen_data = test_api_music_generation()
    test_midi_download_and_parsing(gen_data)
    test_chat_endpoint()
    test_static_asset_serving()
    print("==================================================")
    print("  [ALL VERIFICATION CHECKS PASSED SUCCESSFULLY]  ")
    print("==================================================")
