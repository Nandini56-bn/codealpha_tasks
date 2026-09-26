import torch
import torch.nn as nn

class MusicLSTM(nn.Module):
    """
    PyTorch LSTM Model for Recurrent Music Sequence Generation.
    Takes integer note tokens, converts to dense embeddings, passes through a 2-layer LSTM,
    and outputs logit distributions over the musical note vocabulary.
    """
    def __init__(self, vocab_size: int, embedding_dim: int = 128, hidden_dim: int = 256, num_layers: int = 2, dropout: float = 0.3):
        super(MusicLSTM, self).__init__()
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.lstm = nn.LSTM(
            input_size=embedding_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0
        )
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_dim, vocab_size)
        
    def forward(self, x, hidden=None):
        # x shape: (batch_size, sequence_length)
        embeds = self.embedding(x) # (batch_size, sequence_length, embedding_dim)
        lstm_out, hidden = self.lstm(embeds, hidden) # lstm_out shape: (batch_size, sequence_length, hidden_dim)
        
        # We predict the next token based on the final LSTM time-step
        last_out = lstm_out[:, -1, :] # (batch_size, hidden_dim)
        out = self.dropout(last_out)
        logits = self.fc(out) # (batch_size, vocab_size)
        
        return logits, hidden
