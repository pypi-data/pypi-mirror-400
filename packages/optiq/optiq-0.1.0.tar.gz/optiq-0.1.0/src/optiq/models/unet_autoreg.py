"""
Autoregressive UNet for motion prediction.

This model is designed for continuous frame-to-frame motion prediction,
where each output becomes the input for the next prediction. Unlike the
diffusion-oriented UNet1D, this model is optimized for:

1. Single-step prediction: (B, F) -> (B, F)
2. Smooth transitions between frames
3. Long-horizon autoregressive rollout stability
"""

from __future__ import annotations

from typing import List, Optional

import torch
from torch import nn


class ResidualBlock(nn.Module):
    """Residual block with LayerNorm and skip connection."""

    def __init__(self, dim: int, hidden_dim: int, dropout: float = 0.0):
        super().__init__()
        self.net = nn.Sequential(
            nn.LayerNorm(dim),
            nn.Linear(dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout) if dropout > 0 else nn.Identity(),
            nn.Linear(hidden_dim, dim),
            nn.Dropout(dropout) if dropout > 0 else nn.Identity(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.net(x)


class DownBlock(nn.Module):
    """Downsampling block: reduces feature dimension."""

    def __init__(self, in_dim: int, out_dim: int, dropout: float = 0.0):
        super().__init__()
        self.proj = nn.Linear(in_dim, out_dim)
        self.res = ResidualBlock(out_dim, out_dim * 2, dropout)
        self.norm = nn.LayerNorm(out_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.proj(x)
        x = self.res(x)
        return self.norm(x)


class UpBlock(nn.Module):
    """Upsampling block: increases feature dimension with skip connection."""

    def __init__(self, in_dim: int, skip_dim: int, out_dim: int, dropout: float = 0.0):
        super().__init__()
        self.proj = nn.Linear(in_dim + skip_dim, out_dim)
        self.res = ResidualBlock(out_dim, out_dim * 2, dropout)
        self.norm = nn.LayerNorm(out_dim)

    def forward(self, x: torch.Tensor, skip: torch.Tensor) -> torch.Tensor:
        x = torch.cat([x, skip], dim=-1)
        x = self.proj(x)
        x = self.res(x)
        return self.norm(x)


class MiddleBlock(nn.Module):
    """Middle/bottleneck block with multiple residual layers."""

    def __init__(self, dim: int, num_layers: int = 2, dropout: float = 0.0):
        super().__init__()
        self.layers = nn.ModuleList(
            [ResidualBlock(dim, dim * 2, dropout) for _ in range(num_layers)]
        )
        self.norm = nn.LayerNorm(dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        for layer in self.layers:
            x = layer(x)
        return self.norm(x)


class UNetAutoreg(nn.Module):
    """
    Autoregressive UNet for frame-to-frame motion prediction.

    Architecture:
    - Encoder: progressively reduces feature dimension
    - Middle: bottleneck with residual blocks
    - Decoder: progressively increases dimension with skip connections
    - Output: predicts next frame features

    Designed for stable autoregressive rollout where output is fed back as input.

    Standard forward signature:
        forward(prev_state, condition=None, context=None) -> next_state

    Args:
        input_dim: Dimension of input features (e.g., num_bones * 7 for position + quaternion).
        hidden_dims: List of hidden dimensions for encoder levels. Decoder mirrors this.
        bottleneck_dim: Dimension at the bottleneck (smallest representation).
        num_res_blocks: Number of residual blocks in the middle/bottleneck.
        dropout: Dropout probability.
        output_dim: Output dimension (defaults to input_dim for autoregressive use).
        conditioning_dim: Optional conditioning vector dimension.
        residual_output: If True, output is added to input (predicts delta).
    """

    def __init__(
        self,
        input_dim: int,
        hidden_dims: Optional[List[int]] = None,
        bottleneck_dim: int = 64,
        num_res_blocks: int = 3,
        dropout: float = 0.1,
        output_dim: Optional[int] = None,
        conditioning_dim: Optional[int] = None,
        residual_output: bool = True,
    ):
        super().__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim or input_dim
        self.conditioning_dim = conditioning_dim
        self.residual_output = residual_output

        # Default hidden dims: progressively reduce
        if hidden_dims is None:
            hidden_dims = [256, 128]

        self.hidden_dims = hidden_dims

        # Input projection (includes conditioning if present)
        in_features = input_dim + (conditioning_dim or 0)
        self.input_proj = nn.Sequential(
            nn.Linear(in_features, hidden_dims[0]),
            nn.LayerNorm(hidden_dims[0]),
            nn.GELU(),
        )

        # Encoder (downsampling path)
        self.encoder_blocks = nn.ModuleList()
        encoder_dims = hidden_dims + [bottleneck_dim]
        for i in range(len(encoder_dims) - 1):
            in_d = encoder_dims[i]
            out_d = encoder_dims[i + 1]
            self.encoder_blocks.append(DownBlock(in_d, out_d, dropout))

        # Bottleneck
        self.middle = MiddleBlock(bottleneck_dim, num_res_blocks, dropout)

        # Decoder (upsampling path with skip connections)
        # Mirror the encoder: bottleneck -> hidden_dims[1] -> hidden_dims[0]
        self.decoder_blocks = nn.ModuleList()
        decoder_in_dims = [bottleneck_dim] + list(
            reversed(hidden_dims[1:])
        )  # [bottleneck, 128, ...]
        decoder_out_dims = list(reversed(hidden_dims))  # [128, 256, ...]
        skip_dims = list(reversed(hidden_dims))  # Skip connections from encoder

        for i in range(len(decoder_out_dims)):
            in_d = (
                decoder_in_dims[i]
                if i < len(decoder_in_dims)
                else decoder_out_dims[i - 1]
            )
            skip_d = skip_dims[i]
            out_d = decoder_out_dims[i]
            self.decoder_blocks.append(UpBlock(in_d, skip_d, out_d, dropout))

        # Output projection
        final_dim = hidden_dims[0]  # Back to first hidden dim
        self.output_proj = nn.Sequential(
            nn.Linear(final_dim, final_dim * 2),
            nn.GELU(),
            nn.Linear(final_dim * 2, self.output_dim),
        )

        # For residual output, ensure dimensions match
        self.residual_proj = None
        if residual_output and self.output_dim != input_dim:
            self.residual_proj = nn.Linear(input_dim, self.output_dim)

    def forward(
        self,
        prev_state: torch.Tensor,
        condition: Optional[torch.Tensor] = None,
        context: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Forward pass for next-frame prediction.

        Args:
            prev_state: Input state tensor of shape (B, F) or (B, T, F).
                        If 3D, uses the last timestep.
            condition: Optional conditioning tensor of shape (B, C).
            context: Optional additional context (reserved for future use).

        Returns:
            next_state: Predicted next state of shape (B, output_dim).
        """
        x = prev_state

        # Handle sequence input - use last frame
        if x.dim() == 3:
            x = x[:, -1, :]  # (B, F)

        # Store input for residual connection
        input_for_residual = x

        # Concatenate conditioning if present
        if condition is not None:
            if condition.dim() > 2:
                condition = condition.view(condition.size(0), -1)
            if condition.dim() == 1:
                condition = condition.unsqueeze(0)
            x = torch.cat([x, condition], dim=-1)

        # Input projection
        x = self.input_proj(x)

        # Encoder with skip connections
        skips: List[torch.Tensor] = []
        for block in self.encoder_blocks:
            skips.append(x)
            x = block(x)

        # Bottleneck
        x = self.middle(x)

        # Decoder with skip connections (in reverse order)
        for i, block in enumerate(self.decoder_blocks):
            skip_idx = len(skips) - 1 - i
            skip = skips[skip_idx] if skip_idx >= 0 else x
            x = block(x, skip)

        # Output projection
        out = self.output_proj(x)

        # Residual connection: predict delta from input
        if self.residual_output:
            if self.residual_proj is not None:
                input_for_residual = self.residual_proj(input_for_residual)
            out = out + input_for_residual

        return out


# Convenience alias for registry
AutoregressiveUNet = UNetAutoreg
