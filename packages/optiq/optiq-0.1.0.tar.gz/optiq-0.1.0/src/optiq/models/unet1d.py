from __future__ import annotations

from typing import List, Optional

import torch
from torch import nn


class ConvBlock(nn.Module):
    """Basic convolutional block with optional residual connection."""

    def __init__(
        self,
        in_ch: int,
        out_ch: int,
        kernel_size: int = 3,
        dropout: float = 0.0,
        residual: bool = False,
    ):
        super().__init__()
        padding = kernel_size // 2
        self.residual = residual

        self.net = nn.Sequential(
            nn.Conv1d(in_ch, out_ch, kernel_size=kernel_size, padding=padding),
            nn.GroupNorm(min(8, out_ch), out_ch),
            nn.SiLU(),
            nn.Conv1d(out_ch, out_ch, kernel_size=kernel_size, padding=padding),
            nn.GroupNorm(min(8, out_ch), out_ch),
            nn.SiLU(),
            nn.Dropout(dropout) if dropout > 0 else nn.Identity(),
        )

        self.skip_proj = None
        if residual:
            if in_ch != out_ch:
                self.skip_proj = nn.Conv1d(in_ch, out_ch, kernel_size=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.net(x)
        if self.residual:
            if self.skip_proj is not None:
                out = out + self.skip_proj(x)
            else:
                out = out + x
        return out


class SelfAttention1D(nn.Module):
    """Simple self-attention for 1D sequences."""

    def __init__(self, channels: int, num_heads: int = 4):
        super().__init__()
        self.norm = nn.GroupNorm(min(8, channels), channels)
        self.attn = nn.MultiheadAttention(channels, num_heads, batch_first=True)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, C, T)
        b, c, t = x.shape
        h = self.norm(x)
        h = h.permute(0, 2, 1)  # (B, T, C)
        h, _ = self.attn(h, h, h)
        h = h.permute(0, 2, 1)  # (B, C, T)
        return x + h


class NoiseSchedule:
    """Simple linear noise schedule for diffusion models."""

    def __init__(
        self, num_steps: int = 1000, beta_start: float = 1e-4, beta_end: float = 0.02
    ):
        self.num_steps = num_steps
        self.betas = torch.linspace(beta_start, beta_end, num_steps)
        self.alphas = 1.0 - self.betas
        self.alpha_cumprod = torch.cumprod(self.alphas, dim=0)

    def get_timestep_embedding(self, t: torch.Tensor, dim: int) -> torch.Tensor:
        """Sinusoidal timestep embedding."""
        half_dim = dim // 2
        emb = torch.log(torch.tensor(10000.0)) / (half_dim - 1)
        emb = torch.exp(
            torch.arange(half_dim, device=t.device, dtype=torch.float32) * -emb
        )
        emb = t[:, None].float() * emb[None, :]
        emb = torch.cat([torch.sin(emb), torch.cos(emb)], dim=-1)
        if dim % 2 == 1:
            emb = torch.cat([emb, torch.zeros_like(emb[:, :1])], dim=-1)
        return emb


class UNet1D(nn.Module):
    """
    Temporal 1D UNet for motion prediction with optional diffusion support.

    Accepts (B, T, F) and predicts the next-state vector (B, F) from the final
    timestep output.

    Standard forward signature:
        forward(prev_state, condition=None, context=None) -> next_state

    Args:
        input_dim: Dimension of input features per timestep.
        base_channels: Base number of channels (doubled at each level).
        dropout: Dropout probability.
        output_dim: Output dimension (defaults to input_dim).
        conditioning_dim: Expected dimension of conditioning vector.
        num_res_blocks: Number of residual blocks per level.
        attention_layers: List of level indices where attention is applied.
        noise_schedule: If "linear", enables diffusion-style noise conditioning.
        time_emb_dim: Dimension of timestep embedding for diffusion.
        num_levels: Number of UNet levels (encoder/decoder stages).
    """

    def __init__(
        self,
        input_dim: int,
        base_channels: int = 64,
        dropout: float = 0.0,
        output_dim: Optional[int] = None,
        conditioning_dim: Optional[int] = None,
        num_res_blocks: int = 2,
        attention_layers: Optional[List[int]] = None,
        noise_schedule: Optional[str] = None,
        time_emb_dim: int = 128,
        num_levels: int = 2,
        kernel_size: int = 3,
    ):
        super().__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim or input_dim
        self.conditioning_dim = conditioning_dim
        self.num_res_blocks = num_res_blocks
        self.attention_layers = attention_layers or []
        self.num_levels = num_levels
        self.kernel_size = kernel_size

        # Noise schedule for diffusion
        self.noise_schedule_obj = None
        self.time_emb_dim = None
        if noise_schedule == "linear":
            self.noise_schedule_obj = NoiseSchedule()
            self.time_emb_dim = time_emb_dim
            self.time_mlp = nn.Sequential(
                nn.Linear(time_emb_dim, time_emb_dim * 4),
                nn.SiLU(),
                nn.Linear(time_emb_dim * 4, time_emb_dim),
            )
        else:
            self.time_mlp = None

        # Input dimension with conditioning
        in_ch = input_dim + (conditioning_dim or 0)

        # Input projection to base_channels
        padding = kernel_size // 2
        self.input_conv = nn.Conv1d(
            in_ch, base_channels, kernel_size=kernel_size, padding=padding
        )

        # Encoder
        self.encoder_blocks: nn.ModuleList = nn.ModuleList()
        self.downsamples: nn.ModuleList = nn.ModuleList()
        ch = base_channels

        for level in range(num_levels):
            out_ch = base_channels * (2**level)
            level_blocks: nn.ModuleList = nn.ModuleList()

            for block_idx in range(num_res_blocks):
                level_blocks.append(
                    ConvBlock(
                        ch,
                        out_ch,
                        kernel_size=kernel_size,
                        dropout=dropout,
                        residual=True,
                    )
                )
                ch = out_ch
                if level in self.attention_layers:
                    level_blocks.append(SelfAttention1D(ch))

            self.encoder_blocks.append(level_blocks)
            if level < num_levels - 1:
                self.downsamples.append(nn.Conv1d(ch, ch, kernel_size=2, stride=2))

        # Middle
        self.mid_block1 = ConvBlock(
            ch, ch, kernel_size=kernel_size, dropout=dropout, residual=True
        )
        self.mid_attn = SelfAttention1D(ch) if self.attention_layers else nn.Identity()
        self.mid_block2 = ConvBlock(
            ch, ch, kernel_size=kernel_size, dropout=dropout, residual=True
        )

        # Decoder
        self.decoder_blocks: nn.ModuleList = nn.ModuleList()
        self.upsamples: nn.ModuleList = nn.ModuleList()
        self.skip_projs: nn.ModuleList = nn.ModuleList()

        for level in reversed(range(num_levels)):
            out_ch = base_channels * (2**level)

            # Skip connection projection (from encoder level)
            skip_in_ch = base_channels * (2**level)
            self.skip_projs.append(nn.Conv1d(skip_in_ch, ch, kernel_size=1))

            level_blocks: nn.ModuleList = nn.ModuleList()
            for block_idx in range(num_res_blocks):
                level_blocks.append(
                    ConvBlock(
                        ch,
                        out_ch,
                        kernel_size=kernel_size,
                        dropout=dropout,
                        residual=True,
                    )
                )
                ch = out_ch
                if level in self.attention_layers:
                    level_blocks.append(SelfAttention1D(ch))

            self.decoder_blocks.append(level_blocks)

            if level > 0:
                self.upsamples.append(
                    nn.ConvTranspose1d(ch, ch, kernel_size=2, stride=2)
                )

        # Output
        self.out_conv = nn.Conv1d(ch, input_dim, kernel_size=1)
        self.head = nn.Linear(input_dim, self.output_dim)

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
            context: Optional timestep for diffusion (int tensor of shape (B,)).

        Returns:
            next_state: Predicted next state of shape (B, output_dim).
        """
        x = prev_state
        if x.dim() == 2:
            x = x.unsqueeze(1)  # (B, 1, F)

        # Handle conditioning
        if condition is not None:
            if condition.dim() == 2:
                condition = condition.unsqueeze(1).expand(-1, x.size(1), -1)
            elif condition.dim() == 3:
                pass
            else:
                condition = condition.view(condition.size(0), 1, -1).expand(
                    -1, x.size(1), -1
                )
            x = torch.cat([x, condition], dim=-1)

        # B, T, F -> B, F, T
        x = x.permute(0, 2, 1)

        # Time embedding for diffusion (currently not applied in blocks for simplicity)
        time_emb = None
        if self.time_mlp is not None and context is not None:
            t_emb = self.noise_schedule_obj.get_timestep_embedding(
                context, self.time_emb_dim
            )
            time_emb = self.time_mlp(t_emb.to(x.device))

        # Input projection
        x = self.input_conv(x)

        # Encoder with skip connections
        skips: List[torch.Tensor] = []
        for level, blocks in enumerate(self.encoder_blocks):
            for block in blocks:
                x = block(x)
            skips.append(x)
            if level < len(self.downsamples) and x.size(-1) >= 2:
                x = self.downsamples[level](x)

        # Middle
        x = self.mid_block1(x)
        x = self.mid_attn(x)
        x = self.mid_block2(x)

        # Add time embedding if available
        if time_emb is not None:
            # Simple additive embedding at bottleneck
            x = x + time_emb[:, :, None].expand(-1, -1, x.size(-1))[:, : x.size(1), :]

        # Decoder with skip connections
        for level, (blocks, skip_proj) in enumerate(
            zip(self.decoder_blocks, self.skip_projs)
        ):
            if level < len(self.upsamples):
                x = self.upsamples[level](x)

            # Add skip connection
            skip_idx = len(skips) - 1 - level
            if skip_idx >= 0:
                skip = skips[skip_idx]
                # Handle size mismatch
                if x.shape[-1] != skip.shape[-1]:
                    x = torch.nn.functional.interpolate(
                        x, size=skip.shape[-1], mode="nearest"
                    )
                x = x + skip_proj(skip)

            for block in blocks:
                x = block(x)

        # Output
        out_seq = self.out_conv(x)  # (B, F, T)
        last = out_seq[:, :, -1]  # (B, F)
        return self.head(last)
