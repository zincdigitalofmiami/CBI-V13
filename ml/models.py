"""
Neural model scaffolding for short‑term horizon forecasts.

Alignment with Modeling Plan:
- Short‑term (1–7d): sequence model using last 5–10 days of prices + high‑freq exogenous features
  (FX, palm, weather updates) when available.
- Medium/long‑term handled in baseline/structural pipelines; this module focuses on ST.

Safe to import: if torch is not installed in your environment, keep this module unused.
"""
try:
    import torch
    import torch.nn as nn
except Exception:  # pragma: no cover — allow environments without torch
    torch = None  # type: ignore
    nn = None  # type: ignore


class LSTMRegressor(nn.Module if nn is not None else object):
    def __init__(self, input_dim: int, hidden_dim: int = 32, num_layers: int = 1, dropout: float = 0.1):
        if nn is None:
            raise ImportError("PyTorch is not installed; install torch to use LSTMRegressor.")
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


def build_model(input_dim: int):
    if nn is None:
        raise ImportError("PyTorch is not installed; install torch to build the model.")
    return LSTMRegressor(input_dim)
