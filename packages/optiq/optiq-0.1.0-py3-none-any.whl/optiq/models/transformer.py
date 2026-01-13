from __future__ import annotations

from typing import Optional

import torch
from torch import nn


class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, max_len: int = 5000):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float()
            * (-torch.log(torch.tensor(10000.0)) / d_model)
        )
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        self.register_buffer("pe", pe)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, T, D)
        return x + self.pe[:, : x.size(1)]


class TransformerModel(nn.Module):
    """
    Lightweight Transformer encoder for next-state prediction.

    Accepts prev_state shape (B, T, F) or (B, F). Optional conditioning is
    concatenated channel-wise before projection.

    Standard forward signature:
        forward(prev_state, condition=None, context=None) -> next_state

    Args:
        input_dim: Dimension of input features per timestep.
        model_dim: Internal model dimension.
        num_layers: Number of transformer encoder layers.
        num_heads: Number of attention heads.
        dropout: Dropout probability.
        output_dim: Output dimension (defaults to input_dim).
        conditioning_dim: Expected dimension of conditioning vector (for validation).
        ff_mult: Feedforward dimension multiplier (ff_dim = model_dim * ff_mult).
        max_seq_len: Maximum sequence length for positional encoding.
        causal: If True, apply causal (autoregressive) attention mask.
        horizon: Number of future steps to predict (affects output interpretation).
    """

    def __init__(
        self,
        input_dim: int,
        model_dim: int = 256,
        num_layers: int = 4,
        num_heads: int = 4,
        dropout: float = 0.1,
        output_dim: Optional[int] = None,
        conditioning_dim: Optional[int] = None,
        ff_mult: int = 4,
        max_seq_len: int = 5000,
        causal: bool = False,
        horizon: int = 1,
    ):
        super().__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim or input_dim
        self.conditioning_dim = conditioning_dim
        self.causal = causal
        self.horizon = horizon
        self.max_seq_len = max_seq_len

        # Input projection (with optional conditioning)
        proj_in_dim = input_dim + (conditioning_dim or 0)
        self.input_proj = nn.Linear(proj_in_dim, model_dim)

        # Transformer encoder
        ff_dim = model_dim * ff_mult
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=model_dim,
            nhead=num_heads,
            dim_feedforward=ff_dim,
            dropout=dropout,
            batch_first=True,
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        # Positional encoding
        self.pos = PositionalEncoding(model_dim, max_len=max_seq_len)

        # Output head
        self.head = nn.Linear(model_dim, self.output_dim)

    def _generate_causal_mask(self, seq_len: int, device: torch.device) -> torch.Tensor:
        """Generate a causal (upper triangular) attention mask."""
        mask = torch.triu(torch.ones(seq_len, seq_len, device=device), diagonal=1)
        mask = mask.masked_fill(mask == 1, float("-inf"))
        return mask

    def forward(
        self,
        prev_state: torch.Tensor,
        condition: Optional[torch.Tensor] = None,
        context: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Forward pass.

        Args:
            prev_state: Input state tensor of shape (B, F) or (B, T, F).
            condition: Optional conditioning tensor of shape (B, C) or (B, T, C).
            context: Optional additional context (reserved for future use).

        Returns:
            next_state: Predicted next state of shape (B, output_dim).
        """
        x = prev_state
        if x.dim() == 2:
            x = x.unsqueeze(1)  # (B, 1, F)

        batch_size, seq_len, _ = x.shape

        # Handle conditioning
        if condition is not None:
            if condition.dim() == 2:
                cond = condition.unsqueeze(1).expand(-1, seq_len, -1)
            elif condition.dim() == 3:
                cond = condition
            else:
                cond = condition.view(condition.size(0), 1, -1).expand(-1, seq_len, -1)
            x = torch.cat([x, cond], dim=-1)

        # Project to model dimension
        x = self.input_proj(x)
        x = self.pos(x)

        # Apply causal mask if needed
        mask = None
        if self.causal and seq_len > 1:
            mask = self._generate_causal_mask(seq_len, x.device)

        # Encode
        enc = self.encoder(x, mask=mask)

        # Output from last timestep
        last = enc[:, -1, :]
        return self.head(last)
