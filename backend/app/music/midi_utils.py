import os
from pathlib import Path
from typing import List, Dict, Any
from music21 import stream, note, chord, midi, instrument

from backend.app.utils.config import GENERATED_DIR

REST_TOKEN = "REST"

def sequence_to_midi_file(prediction_output: List[str], output_filename: str = "ai_composition.mid", quarter_length: float = 0.5) -> Path:
    """
    Converts a sequence of note/chord/rest string tokens into a standard MIDI file using music21.
    """
    output_notes = []
    
    # Set default piano instrument for clean classical/polyphonic output
    output_notes.append(instrument.Piano())
    
    for pattern in prediction_output:
        if pattern == REST_TOKEN:
            new_rest = note.Rest()
            new_rest.quarterLength = quarter_length
            new_rest.storedInstrument = instrument.Piano()
            output_notes.append(new_rest)
            
        elif ('.' in pattern) or pattern.isdigit(): # Pattern is a chord
            try:
                notes_in_chord = [int(n) for n in pattern.split('.')]
                new_chord = chord.Chord(notes_in_chord)
                new_chord.quarterLength = quarter_length
                new_chord.storedInstrument = instrument.Piano()
                output_notes.append(new_chord)
            except Exception:
                # Fallback to single rest if chord string parsing fails
                r = note.Rest()
                r.quarterLength = quarter_length
                output_notes.append(r)
                
        else: # Pattern is a single note (e.g. 'C4', 'E-4', 'G#5')
            try:
                new_note = note.Note(pattern)
                new_note.quarterLength = quarter_length
                new_note.storedInstrument = instrument.Piano()
                output_notes.append(new_note)
            except Exception:
                r = note.Rest()
                r.quarterLength = quarter_length
                output_notes.append(r)
                
    midi_stream = stream.Stream(output_notes)
    
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    output_path = GENERATED_DIR / output_filename
    
    # Write stream to MIDI file
    mf = midi.translate.music21ObjectToMidiFile(midi_stream)
    mf.open(str(output_path), 'wb')
    mf.write()
    mf.close()
    
    return output_path
