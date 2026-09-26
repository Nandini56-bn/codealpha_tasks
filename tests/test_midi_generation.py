import os
from pathlib import Path
import pytest
from music21 import converter
from backend.app.utils.config import GENERATED_DIR
from backend.app.music.midi_utils import sequence_to_midi_file
from backend.app.ai.generator import generate_ai_music

def test_sequence_to_midi_file():
    """Verify converting note tokens into a valid MIDI file."""
    sample_sequence = ['C4', 'E4', 'G4', 'C5', 'REST', '0.4.7', 'A4', 'F4']
    filename = "test_converter.mid"
    
    file_path = sequence_to_midi_file(sample_sequence, output_filename=filename)
    
    assert file_path.exists()
    assert file_path.stat().st_size > 0
    
    # Verify file can be parsed by music21
    parsed_score = converter.parse(file_path)
    assert parsed_score is not None

def test_ai_music_generator_output():
    """Verify full end-to-end model sequence generation and MIDI creation."""
    result = generate_ai_music(generate_length=32, temperature=1.0, output_filename="test_gen_full.mid")
    
    assert result["status"] == "success"
    assert result["note_count"] == 32
    assert "filename" in result
    
    generated_path = Path(result["filepath"])
    assert generated_path.exists()
    assert generated_path.stat().st_size > 0
    
    # Parse generated composition with music21 to confirm valid MIDI structure
    score = converter.parse(generated_path)
    assert score is not None
