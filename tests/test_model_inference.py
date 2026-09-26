import json
import torch
import pytest
from backend.app.utils.config import MODEL_DIR, PROCESSED_DIR
from backend.app.ai.model import MusicLSTM

def test_model_forward_pass():
    """Verify PyTorch model forward pass returns correct logit dimensions."""
    vocab_size = 50
    batch_size = 4
    seq_len = 32
    
    model = MusicLSTM(vocab_size=vocab_size, embedding_dim=64, hidden_dim=128, num_layers=2)
    dummy_input = torch.randint(0, vocab_size, (batch_size, seq_len))
    
    logits, hidden = model(dummy_input)
    
    assert logits.shape == (batch_size, vocab_size), f"Expected logits shape ({batch_size}, {vocab_size}), got {logits.shape}"
    assert hidden is not None

def test_checkpoint_exists_and_loads():
    """Verify trained model checkpoint file exists and state dict loads cleanly."""
    checkpoint_path = MODEL_DIR / "lstm_music_model.pth"
    vocab_file = PROCESSED_DIR / "vocab.json"
    
    assert checkpoint_path.exists(), "Model checkpoint lstm_music_model.pth does not exist. Run train_model.py first."
    assert vocab_file.exists()
    
    with open(vocab_file, "r") as f:
        vocab_data = json.load(f)
    vocab_size = vocab_data["vocab_size"]
    
    checkpoint = torch.load(checkpoint_path, weights_only=True)
    assert "model_state_dict" in checkpoint
    
    model = MusicLSTM(
        vocab_size=vocab_size,
        embedding_dim=checkpoint.get("embedding_dim", 128),
        hidden_dim=checkpoint.get("hidden_dim", 256),
        num_layers=checkpoint.get("num_layers", 2)
    )
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    
    # Test evaluation forward pass
    sample_seq = torch.randint(0, vocab_size, (1, 32))
    with torch.no_grad():
        logits, _ = model(sample_seq)
        probs = torch.softmax(logits, dim=-1)
        assert probs.shape == (1, vocab_size)
        assert torch.isclose(probs.sum(), torch.tensor(1.0), atol=1e-4)
