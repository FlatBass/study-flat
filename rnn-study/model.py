import torch
import torch.nn as nn


class SpamRNN(nn.Module):
    def __init__(self, vocab_size, embed_dim=32, hidden_size=32):
        super().__init__()

        self.embedding = nn.Embedding(
            vocab_size,
            embed_dim,
            padding_idx=0
        )

        self.rnn = nn.RNN(
            embed_dim,
            hidden_size,
            batch_first=True
        )

        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        x = self.embedding(x)

        output, hidden = self.rnn(x)

        last = hidden[-1]
        score = self.fc(last)

        return torch.sigmoid(score).squeeze(-1)