from __future__ import annotations

from typing import Callable, Dict, List, Tuple, Union

import torch
from torch import nn

from .mlp import MLPModel
from .transformer import TransformerModel
from .unet1d import UNet1D
from .unet_autoreg import UNetAutoreg

_REGISTRY: Dict[str, Callable[..., nn.Module]] = {
    "mlp": MLPModel,
    "transformer": TransformerModel,
    "unet1d": UNet1D,
    "unet_autoreg": UNetAutoreg,
}


def register(name: str, builder: Callable[..., nn.Module]) -> None:
    if name in _REGISTRY:
        raise ValueError(f"Model '{name}' already registered.")
    _REGISTRY[name] = builder


def build(name: str, **cfg) -> nn.Module:
    if name not in _REGISTRY:
        raise ValueError(f"Unknown model '{name}'. Available: {list(_REGISTRY.keys())}")
    return _REGISTRY[name](**cfg)


def available() -> Dict[str, Callable[..., nn.Module]]:
    return dict(_REGISTRY)


def list_models() -> List[str]:
    """Return a sorted list of registered model names."""
    return sorted(_REGISTRY.keys())


def load_checkpoint(
    path: Union[str, torch.PathLike],
    map_location: Union[str, torch.device, None] = "cpu",
) -> Tuple[nn.Module, Dict]:
    """
    Load a checkpoint saved via torch.save with metadata or a TorchScript module.

    Expected state_dict format:
        {
            "arch": "mlp" | "transformer" | "unet1d" | "unet_autoreg",
            "config": {...},  # kwargs used to build the model
            "model_state_dict": ...,
            # optional metadata fields:
            # "input_dim", "output_dim", "conditioning_dim", ...
        }

    TorchScript:
        - If the file is a TorchScript artifact, returns the scripted module and
          metadata {"arch": "torchscript"}.
    """
    try:
        obj = torch.load(path, map_location=map_location)
    except (RuntimeError, ValueError):
        # Possibly a TorchScript artifact
        scripted = torch.jit.load(path, map_location=map_location)
        return scripted, {"arch": "torchscript", "config": {}, "format": "torchscript"}

    if not isinstance(obj, dict) or "arch" not in obj:
        raise ValueError(
            "Checkpoint missing required metadata 'arch'. "
            "Expected a dict with keys ['arch', 'config', 'model_state_dict']."
        )

    arch = obj["arch"]
    if arch not in _REGISTRY:
        raise ValueError(f"Unknown architecture '{arch}' in checkpoint.")

    cfg = obj.get("config", {}) or {}
    # Drop training-only or duplicate keys that are not model ctor args
    drop_keys = {
        "arch",
        "optimizer",
        "scheduler",
        "grad_clip",
        "epochs",
        "batch_size",
        "lr",
        "data_path",
        "loss",
        "dry_run",
        # Dataset/training augmentation keys
        "noise_std",
        "input_noise_std",
        "min_horizon",
        "max_horizon",
        "num_rollout_steps",
        "rollout_len",
        "rollout_stride",
        "dataset_type",
        "random_start",
        "num_samples",
        "dataset_size",
        # Lightning module keys
        "lightning_module",
        "initial_teacher_ratio",
        "final_teacher_ratio",
        "teacher_decay_steps",
        "horizon",
        "velocity_weight",
        # Loss configuration
        "loss_type",
        "num_bones",
        "features_per_bone",
        # Gradient control
        "gradient_steps",
    }
    clean_cfg = {k: v for k, v in cfg.items() if k not in drop_keys}

    model = build(arch, **clean_cfg)
    state = obj.get("model_state_dict", obj.get("state_dict"))
    if state is None:
        raise ValueError("Checkpoint missing 'model_state_dict' or 'state_dict'.")
    model.load_state_dict(state)
    metadata = {
        "arch": arch,
        "config": cfg,
        "input_dim": obj.get("input_dim"),
        "output_dim": obj.get("output_dim"),
        "conditioning_dim": obj.get("conditioning_dim"),
        "format": "state_dict",
    }
    return model, metadata


def export_torchscript(
    model: nn.Module,
    example_input: torch.Tensor,
    out_path: Union[str, torch.PathLike],
    strict: bool = False,
    check_trace: bool = False,
) -> str:
    """
    Export a model to TorchScript using trace.

    Args:
        model: The nn.Module to export.
        example_input: Tensor example matching model forward signature
                       (passed as prev_state). Conditioning/context should be
                       pre-bound or handled inside the model.
        out_path: Output file path for the TorchScript artifact.
        strict: Whether to use strict tracing; defaults to False for flexibility.
        check_trace: Whether to run trace checking; defaults to False to avoid
                     spurious failures on nondeterministic modules (e.g., dropout).
    """
    model.eval()
    scripted = torch.jit.trace(
        model, example_input, strict=strict, check_trace=check_trace
    )
    scripted.save(str(out_path))
    return str(out_path)
