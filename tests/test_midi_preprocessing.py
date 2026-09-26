import json
from pathlib import Path
import pytest
from backend.app.utils.config import RAW_MIDI_DIR, PROCESSED_DIR
from backend.app.ai.dataset import parse_midi_file, load_and_preprocess_genre_dataset

def test_raw_midi_files_exist():
    """Verify raw MIDI files are extracted in raw_midi directory."""
    midi_files = list(RAW_MIDI_DIR.glob("*.mid")) + list(RAW_MIDI_DIR.glob("*.midi"))
    assert len(midi_files) > 0, "No raw MIDI files found for preprocessing."

def test_parse_single_midi_file():
    """Test parsing a single MIDI file into note tokens."""
    midi_files = list(RAW_MIDI_DIR.glob("*.mid"))
    assert len(midi_files) > 0
    
    first_midi = midi_files[0]
    tokens = parse_midi_file(first_midi)
    
    assert isinstance(tokens, list)
    assert len(tokens) > 0, "Parsed MIDI file returned an empty note sequence."
    assert all(isinstance(t, str) for t in tokens)

def test_load_and_preprocess_dataset():
    """Test full dataset preprocessing pipeline and vocabulary file creation."""
    X, y, note_to_int, int_to_note, vocab_size = load_and_preprocess_genre_dataset(
        genre="classical", sequence_length=16
    )
    
    assert len(X) > 0
    assert len(y) == len(X)
    assert vocab_size > 0
    assert len(note_to_int) == vocab_size
    assert len(int_to_note) == vocab_size
    
    # Check inverse mapping property
    for note_str, idx in note_to_int.items():
        assert int_to_note[idx] == note_str
        
    # Writes genre vocab without overwriting the live LSTM vocab.json
    vocab_file = PROCESSED_DIR / "classical" / "vocab.json"
    assert vocab_file.exists()
    
    with open(vocab_file, "r") as f:
        data = json.load(f)
        assert "note_to_int" in data
        assert "int_to_note" in data
        assert data["vocab_size"] == vocab_size
