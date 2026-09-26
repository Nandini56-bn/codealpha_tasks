import os
from pathlib import Path
from backend.app.utils.config import BASE_DIR, RAW_MIDI_DIR, PROCESSED_DIR, MODEL_DIR, GENERATED_DIR

def test_directory_structure():
    """Verify that all core project directories exist."""
    assert BASE_DIR.exists()
    assert RAW_MIDI_DIR.exists()
    assert PROCESSED_DIR.exists()
    assert MODEL_DIR.exists()
    assert GENERATED_DIR.exists()

def test_config_variables():
    """Verify backend configuration parameters."""
    from backend.app.utils.config import HOST, PORT
    assert isinstance(HOST, str)
    assert isinstance(PORT, int)
