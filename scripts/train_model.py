"""
Model Training Script for AI Music Studio
-----------------------------------------
Trains PyTorch LSTM neural network locally on CPU using the preprocessed
classical MIDI dataset. Measures actual laptop execution time and loss convergence.
"""

import sys
import json
import pickle
import time
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

from backend.app.utils.config import PROCESSED_DIR, MODEL_DIR
from backend.app.ai.model import MusicLSTM

def train_music_model(epochs: int = 15, batch_size: int = 64, learning_rate: float = 0.003):
    print("[*] Starting Local PyTorch Model Training...")
    
    # Load vocabulary metadata
    vocab_file = PROCESSED_DIR / "vocab.json"
    dataset_file = PROCESSED_DIR / "dataset.pkl"
    
    if not vocab_file.exists() or not dataset_file.exists():
        raise FileNotFoundError(f"Processed dataset files not found in {PROCESSED_DIR}. Run dataset.py first.")
        
    with open(vocab_file, "r") as f:
        vocab_data = json.load(f)
    vocab_size = vocab_data["vocab_size"]
    
    with open(dataset_file, "rb") as f:
        dataset_data = pickle.load(f)
    X_raw, y_raw = dataset_data["X"], dataset_data["y"]
    
    # Convert numpy arrays to PyTorch Tensors
    X_tensor = torch.tensor(X_raw, dtype=torch.long)
    y_tensor = torch.tensor(y_raw, dtype=torch.long)
    
    dataset = TensorDataset(X_tensor, y_tensor)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    # Instantiate Model, Loss Function & Optimizer
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[*] Training Device: {device}")
    
    model = MusicLSTM(vocab_size=vocab_size, embedding_dim=128, hidden_dim=256, num_layers=2, dropout=0.3).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    checkpoint_path = MODEL_DIR / "lstm_music_model.pth"
    
    start_time = time.time()
    
    model.train()
    for epoch in range(1, epochs + 1):
        epoch_loss = 0.0
        for batch_X, batch_y in loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            
            optimizer.zero_grad()
            logits, _ = model(batch_X)
            loss = criterion(logits, batch_y)
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item() * batch_X.size(0)
            
        avg_loss = epoch_loss / len(dataset)
        print(f"  Epoch [{epoch:02d}/{epochs:02d}] - Loss: {avg_loss:.4f}", flush=True)
        
    total_time = time.time() - start_time
    print(f"[SUCCESS] Training completed in {total_time:.2f} seconds.", flush=True)
    print(f"[*] Saving model checkpoint to: {checkpoint_path}", flush=True)
    
    torch.save({
        "model_state_dict": model.state_dict(),
        "vocab_size": vocab_size,
        "embedding_dim": 128,
        "hidden_dim": 256,
        "num_layers": 2,
        "dropout": 0.3
    }, checkpoint_path)
    
    return checkpoint_path

if __name__ == "__main__":
    train_music_model(epochs=15, batch_size=64, learning_rate=0.003)
