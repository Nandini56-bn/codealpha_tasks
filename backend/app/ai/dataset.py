import os
import sys
import json
import pickle
from pathlib import Path
from typing import List, Tuple, Dict, Any
import numpy as np

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from music21 import converter, instrument, note, chord
from backend.app.utils.config import RAW_MIDI_DIR, PROCESSED_DIR

REST_TOKEN = "REST"

def parse_midi_file(file_path: Path) -> List[str]:
    """
    Parses a single MIDI file using music21 and extracts a list of note/chord/rest tokens.
    Handles music21 v10+ compatibility (flatten() vs flat vs recurse).
    """
    notes_sequence = []
    try:
        midi_obj = converter.parse(file_path)
        
        if hasattr(midi_obj, 'flatten'):
            notes_to_parse = midi_obj.flatten().notesAndRests
        elif hasattr(midi_obj, 'flat'):
            notes_to_parse = midi_obj.flat.notesAndRests
        else:
            notes_to_parse = midi_obj.recurse()
            
        for element in notes_to_parse:
            if isinstance(element, note.Note):
                notes_sequence.append(str(element.pitch))
            elif isinstance(element, chord.Chord):
                notes_sequence.append('.'.join(str(n) for n in element.normalOrder))
            elif isinstance(element, note.Rest):
                notes_sequence.append(REST_TOKEN)
                
    except Exception as e:
        print(f"[!] Warning: Error parsing {file_path.name}: {e}")
        
    return notes_sequence

def load_and_preprocess_genre_dataset(genre: str = "classical", sequence_length: int = 32) -> Tuple[np.ndarray, np.ndarray, Dict[str, int], Dict[int, str], int]:
    """
    Loads raw MIDI files for a specific genre subfolder, extracts note sequences,
    builds vocabulary dictionaries, and creates sliding-window training sequences (X, y).
    """
    genre = genre.lower()
    genre_dir = RAW_MIDI_DIR / genre
    if not genre_dir.exists():
        genre_dir = RAW_MIDI_DIR # Fallback
        
    midi_files = list(genre_dir.glob("*.mid")) + list(genre_dir.glob("*.midi"))
    print(f"[*] Processing {len(midi_files)} MIDI files for genre '{genre}' from {genre_dir}...")
    
    all_notes = []
    for file_path in midi_files:
        parsed_notes = parse_midi_file(file_path)
        if len(parsed_notes) > sequence_length:
            all_notes.extend(parsed_notes)
            
    if not all_notes:
        raise ValueError(f"No valid note sequences found for genre '{genre}'. Please extract dataset first.")
        
    unique_pitches = sorted(list(set(all_notes)))
    vocab_size = len(unique_pitches)
    note_to_int = {note_name: number for number, note_name in enumerate(unique_pitches)}
    int_to_note = {number: note_name for number, note_name in enumerate(unique_pitches)}
    
    print(f"[*] Genre '{genre}' - Total notes: {len(all_notes)} | Vocab size: {vocab_size}")
    
    input_sequences = []
    output_targets = []
    
    for i in range(0, len(all_notes) - sequence_length):
        seq_in = all_notes[i : i + sequence_length]
        seq_out = all_notes[i + sequence_length]
        input_sequences.append([note_to_int[char] for char in seq_in])
        output_targets.append(note_to_int[seq_out])
        
    X = np.array(input_sequences, dtype=np.int32)
    y = np.array(output_targets, dtype=np.int32)
    
    # Save processed vocabulary and dataset pickle for genre
    target_processed_dir = PROCESSED_DIR / genre
    target_processed_dir.mkdir(parents=True, exist_ok=True)
    
    vocab_file = target_processed_dir / "vocab.json"
    with open(vocab_file, "w") as f:
        json.dump({
            "genre": genre,
            "note_to_int": note_to_int,
            "int_to_note": {str(k): v for k, v in int_to_note.items()},
            "vocab_size": vocab_size,
            "sequence_length": sequence_length
        }, f, indent=2)
        
    dataset_file = target_processed_dir / "dataset.pkl"
    with open(dataset_file, "wb") as f:
        pickle.dump({"X": X, "y": y}, f)
        
    print(f"[SUCCESS] Genre '{genre}' dataset saved to {target_processed_dir}")
    return X, y, note_to_int, int_to_note, vocab_size

if __name__ == "__main__":
    for g in ["classical", "jazz", "ragtime"]:
        try:
            load_and_preprocess_genre_dataset(genre=g, sequence_length=32)
        except Exception as e:
            print(f"[!] Error processing {g}: {e}")
