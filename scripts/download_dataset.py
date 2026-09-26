"""
Dataset Downloader & Extractor for AI Music Studio
--------------------------------------------------
Extracts verified public-domain classical compositions (J.S. Bach Chorales)
from music21.corpus and saves them as raw MIDI files in backend/data/raw_midi/.

Dataset Metadata:
- Source: music21.corpus (J.S. Bach Chorales collection)
- License: Public Domain (CC0)
- Usage: Training LSTM music generation model locally
"""

import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from music21 import corpus, midi
from backend.app.utils.config import RAW_MIDI_DIR

def prepare_public_domain_dataset(max_files: int = 50):
    """
    Parses public domain Bach chorales from music21 built-in corpus
    and exports clean MIDI files into raw_midi directory.
    """
    print(f"[*] Starting dataset extraction into: {RAW_MIDI_DIR}")
    RAW_MIDI_DIR.mkdir(parents=True, exist_ok=True)
    
    # Fetch Bach Chorales from music21.corpus
    bach_works = corpus.getComposer('bach')
    print(f"[*] Found {len(bach_works)} Bach compositions in music21 corpus.")
    
    exported_count = 0
    for work_path in bach_works:
        if exported_count >= max_files:
            break
        
        # Only process chorales or simple keyboard pieces (.xml, .mxl, .krn)
        str_path = str(work_path).lower()
        if not any(ext in str_path for ext in ['.xml', '.mxl', '.krn', '.mid']):
            continue
            
        try:
            parsed_score = corpus.parse(work_path)
            file_name = f"bach_{exported_count + 1:03d}.mid"
            output_file_path = RAW_MIDI_DIR / file_name
            
            # Write to MIDI file using music21.midi.translate
            mf = midi.translate.music21ObjectToMidiFile(parsed_score)
            mf.open(str(output_file_path), 'wb')
            mf.write()
            mf.close()
            
            exported_count += 1
            if exported_count % 10 == 0:
                print(f"  [+] Exported {exported_count}/{max_files} MIDI files...")
        except Exception as e:
            # Skip invalid or complex files silently
            continue
            
    print(f"[SUCCESS] Successfully exported {exported_count} public-domain MIDI files to {RAW_MIDI_DIR}")
    return exported_count

if __name__ == "__main__":
    prepare_public_domain_dataset(max_files=50)
