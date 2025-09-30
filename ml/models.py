import torch
import torch.nn as nn


class LSTMRegressor(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 32, num_layers: int = 1, dropout: float = 0.1):
        super().__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers=num_layers, batch_first=True, dropout=dropout if num_layers > 1 else 0.0)
        self.head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
        )

    def forward(self, x):  # x: [B, T, F]
        out, _ = self.lstm(x)
        last = out[:, -1, :]
        y = self.head(last)
        return y.squeeze(-1)


def build_model(input_dim: int) -> nn.Module:
    return LSTMRegressor(input_dim)
