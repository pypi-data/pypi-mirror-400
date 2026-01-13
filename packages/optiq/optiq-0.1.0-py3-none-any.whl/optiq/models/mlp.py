from __future__ import annotations

from typing import Iterable, List, Optional, Union

import torch
from torch import nn


class MLPModel(nn.Module):
    """
    Feedforward predictor for single-step or short-horizon next-state prediction.

    Expects inputs of shape (B, F) or (B, T, F). When a sequence is given,
    it uses the last timestep as input. Optional conditioning is concatenated
    along the feature dimension.

    Standard forward signature:
        forward(prev_state, condition=None, context=None) -> next_state

    Args:
        input_dim: Dimension of input features.
        hidden_dims: List of hidden layer dimensions.
        output_dim: Output dimension (defaults to input_dim).
        dropout: Dropout probability between layers.
        conditioning_dim: Expected dimension of conditioning vector (for validation).
        horizon: Number of timesteps to use from input sequence (last N timesteps).
        hidden_dim: Alternative to hidden_dims - single hidden dimension repeated num_layers times.
        num_layers: Number of hidden layers (used with hidden_dim).
    """

    def __init__(
        self,
        input_dim: int,
        hidden_dims: Optional[Union[Iterable[int], List[int]]] = None,
        output_dim: Optional[int] = None,
        dropout: float = 0.0,
        conditioning_dim: Optional[int] = None,
        horizon: int = 1,
        hidden_dim: Optional[int] = None,
        num_layers: Optional[int] = None,
    ):
        super().__init__()
        self.input_dim = input_dim
        self.conditioning_dim = conditioning_dim
        self.horizon = horizon
        self.output_dim = output_dim or input_dim

        # Build hidden_dims from alternative parameters
        if hidden_dims is None:
            if hidden_dim is not None and num_layers is not None:
                hidden_dims = [hidden_dim] * num_layers
            else:
                hidden_dims = [128, 64]  # Default
        hidden = list(hidden_dims)

        # Calculate actual input dimension (including conditioning and horizon)
        actual_input_dim = input_dim * horizon + (conditioning_dim or 0)
        dims = [actual_input_dim] + hidden + [self.output_dim]

        layers: List[nn.Module] = []
        for i in range(len(dims) - 1):
            layers.append(nn.Linear(dims[i], dims[i + 1]))
            if i < len(dims) - 2:
                layers.append(nn.ReLU())
                if dropout > 0:
                    layers.append(nn.Dropout(dropout))
        self.net = nn.Sequential(*layers)

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
            condition: Optional conditioning tensor of shape (B, C).
            context: Optional additional context (reserved for future use).

        Returns:
            next_state: Predicted next state of shape (B, output_dim).
        """
        x = prev_state

        if x.dim() == 3:
            # Use last `horizon` timesteps
            if self.horizon == 1:
                x = x[:, -1, :]  # (B, F)
            else:
                # Flatten last horizon timesteps
                x = x[:, -self.horizon :, :].reshape(x.size(0), -1)  # (B, horizon * F)
        elif x.dim() == 2 and self.horizon > 1:
            # If horizon > 1 but input is 2D, assume it's already correctly shaped
            pass

        # Handle conditioning
        if condition is not None:
            if condition.dim() > 2:
                condition = condition.view(condition.size(0), -1)
            if condition.dim() == 1:
                condition = condition.unsqueeze(0)
            x = torch.cat([x, condition], dim=-1)

        # context is reserved for future use
        return self.net(x)
