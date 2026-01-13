"""
Adapters and factories to bridge pretrained representations into RL policies.

Supports:
- Linear adapters (projection / small MLP).
- TorchScript-loaded feature extractors and observation wrappers.
- Shape inference helpers between two models.
"""

from __future__ import annotations

from typing import Iterable, List, Optional, Sequence, Tuple

import torch
from torch import nn


class LinearAdapter(nn.Module):
    """
    A small MLP that maps an input feature dimension to a target dimension.

    Typical use: wrap a pretrained torso output to match the observation size
    expected by a downstream policy. Hidden layers are optional; by default,
    this is a single linear projection.
    """

    def __init__(
        self,
        in_dim: int,
        out_dim: int,
        hidden_dims: Optional[Iterable[int]] = None,
        activation: Optional[nn.Module] = None,
        dropout: float = 0.0,
    ) -> None:
        super().__init__()
        hidden: List[int] = list(hidden_dims or [])
        act = activation or nn.ReLU()

        layers: List[nn.Module] = []
        dims = [in_dim] + hidden + [out_dim]
        for i in range(len(dims) - 1):
            layers.append(nn.Linear(dims[i], dims[i + 1]))
            if i < len(dims) - 2:  # hide final activation/dropout on output layer
                layers.append(act)
                if dropout > 0:
                    layers.append(nn.Dropout(dropout))

        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def build_linear_adapter(
    in_dim: int,
    out_dim: int,
    hidden_dims: Optional[Iterable[int]] = None,
    activation: Optional[nn.Module] = None,
    dropout: float = 0.0,
) -> LinearAdapter:
    """
    Convenience constructor for a LinearAdapter.

    Example:
        adapter = build_linear_adapter(pretrain_dim, env_obs_dim, hidden_dims=[256])
        adapted_obs = adapter(pretrained_features)
    """
    return LinearAdapter(
        in_dim=in_dim,
        out_dim=out_dim,
        hidden_dims=hidden_dims,
        activation=activation,
        dropout=dropout,
    )


class TorchScriptFeatureExtractor(nn.Module):
    """
    Wrap a TorchScript module as a feature extractor.

    Expects the scripted module to accept a tensor input and return a tensor
    (B, F). Optionally chains a LinearAdapter to match a downstream feature size.
    """

    def __init__(
        self,
        script_path: str,
        device: str = "cpu",
        adapter: Optional[nn.Module] = None,
    ) -> None:
        super().__init__()
        self.script = torch.jit.load(script_path, map_location=device)
        self.adapter = adapter

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.script(x)
        if self.adapter:
            out = self.adapter(out)
        return out


def infer_linear_adapter_from_models(
    pretrain_model: nn.Module,
    policy_model: nn.Module,
    pretrain_input_shape: Sequence[int],
    adapter_hidden: Optional[Sequence[int]] = None,
) -> Tuple[LinearAdapter, int, int]:
    """
    Infer a LinearAdapter that maps from pretrain_model output dim to the first
    Linear layer input dim in policy_model.
    """
    with torch.no_grad():
        dummy = torch.zeros(*pretrain_input_shape)
        pre_out = pretrain_model(dummy)
        if pre_out.dim() > 2:
            pre_out = pre_out.view(pre_out.size(0), -1)
        src_dim = pre_out.shape[1]

    tgt_dim = None
    for m in policy_model.modules():
        if isinstance(m, nn.Linear):
            tgt_dim = m.in_features
            break
    if tgt_dim is None:
        raise ValueError(
            "Could not infer target dim from policy model (no Linear found)."
        )

    adapter = build_linear_adapter(src_dim, tgt_dim, hidden_dims=adapter_hidden)
    return adapter, src_dim, tgt_dim
