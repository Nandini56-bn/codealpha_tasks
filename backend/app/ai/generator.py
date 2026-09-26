import os
import sys
import json
import pickle
import random
from pathlib import Path
from typing import List, Dict, Any

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

import torch
import torch.nn.functional as F
import numpy as np

from backend.app.utils.config import PROCESSED_DIR, MODEL_DIR
from backend.app.ai.model import MusicLSTM
from backend.app.music.midi_utils import sequence_to_midi_file

def sample_with_temperature(logits: torch.Tensor, temperature: float = 1.0) -> int:
    """
    Applies temperature scaling to output logits and samples a token index
    from the resulting probability distribution using categorical multinomial sampling.
    """
    if temperature <= 0.0:
        return torch.argmax(logits, dim=-1).item()
        
    scaled_logits = logits / temperature
    probs = F.softmax(scaled_logits, dim=-1)
    sampled_idx = torch.multinomial(probs, num_samples=1).item()
    return sampled_idx

def generate_ai_music(generate_length: int = 64, temperature: float = 1.0, output_filename: str = None) -> Dict[str, Any]:
    """
    Generates a new AI music composition using the trained PyTorch LSTM model.
    """
    vocab_file = PROCESSED_DIR / "vocab.json"
    dataset_file = PROCESSED_DIR / "dataset.pkl"
    checkpoint_path = MODEL_DIR / "lstm_music_model.pth"
    
    if not checkpoint_path.exists():
        raise FileNotFoundError("Trained model checkpoint lstm_music_model.pth not found. Please train model first.")
        
    with open(vocab_file, "r") as f:
        vocab_data = json.load(f)
        
    note_to_int = vocab_data["note_to_int"]
    int_to_note = {int(k): v for k, v in vocab_data["int_to_note"].items()}
    vocab_size = vocab_data["vocab_size"]
    sequence_length = vocab_data.get("sequence_length", 32)
    
    # Load model state
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    model = MusicLSTM(
        vocab_size=vocab_size,
        embedding_dim=checkpoint.get("embedding_dim", 128),
        hidden_dim=checkpoint.get("hidden_dim", 256),
        num_layers=checkpoint.get("num_layers", 2),
        dropout=checkpoint.get("dropout", 0.3)
    )
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    
    # Load seed sequence pattern from training dataset
    if dataset_file.exists():
        with open(dataset_file, "rb") as f:
            dataset_data = pickle.load(f)
        X_data = dataset_data["X"]
        seed_idx = random.randint(0, len(X_data) - 1)
        pattern = list(X_data[seed_idx])
    else:
        pattern = [random.randint(0, vocab_size - 1) for _ in range(sequence_length)]
        
    prediction_output = []
    
    # Generate new sequence step-by-step
    with torch.no_grad():
        for _ in range(generate_length):
            input_tensor = torch.tensor([pattern[-sequence_length:]], dtype=torch.long) # shape: (1, seq_len)
            logits, _ = model(input_tensor) # shape: (1, vocab_size)
            
            idx_next = sample_with_temperature(logits[0], temperature=temperature)
            note_str = int_to_note[idx_next]
            
            prediction_output.append(note_str)
            pattern.append(idx_next)
            
    if not output_filename:
        output_filename = f"ai_composition_{random.randint(1000, 9999)}.mid"
        
    output_path = sequence_to_midi_file(prediction_output, output_filename=output_filename, quarter_length=0.5)
    
    # Estimate duration in seconds (each step = 0.5 quarter notes ~ 0.5 seconds at 120 BPM)
    estimated_duration_sec = round(generate_length * 0.5, 1)
    
    return {
        "status": "success",
        "filename": output_filename,
        "filepath": str(output_path),
        "note_count": len(prediction_output),
        "estimated_duration_seconds": estimated_duration_sec,
        "temperature": temperature,
        "generated_notes": prediction_output[:10] # First 10 preview notes
    }

if __name__ == "__main__":
    result = generate_ai_music(generate_length=64, temperature=1.0, output_filename="test_output.mid")
    print(f"[SUCCESS] Generated composition saved: {result['filepath']} ({result['note_count']} notes)")
