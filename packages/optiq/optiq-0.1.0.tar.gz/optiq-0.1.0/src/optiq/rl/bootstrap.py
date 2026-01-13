"""
SB3 Bootstrapping and Weight Initialization.

Provides utilities to load pretrained models (TorchScript or state_dict) and
integrate them into Stable Baselines3 policies via feature extractors or
observation wrappers.

Key APIs:
    - load_pretrained: Load TorchScript or state_dict pretrained model
    - build_adapters: Build pre/post adapters for dimension matching
    - make_policy: Create PPO/SAC policy with optional pretrained features
    - make_obs_wrapper: Create observation wrapper for obs-mode adaptation
    - transfer_weights: Copy matching weights from pretrained to SB3 policy
    - save_bundle: Save model + adapters as state_dict bundle
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import torch
from torch import nn

try:
    from stable_baselines3 import PPO, SAC, A2C, TD3
    from stable_baselines3.common.torch_layers import BaseFeaturesExtractor

    HAS_SB3 = True
except ImportError:
    HAS_SB3 = False
    BaseFeaturesExtractor = object  # type: ignore

from .adapter import TorchScriptFeatureExtractor, build_linear_adapter, LinearAdapter


# ---------------------------------------------------------------------------
# Data classes for bootstrap artifacts
# ---------------------------------------------------------------------------


@dataclass
class PretrainedSpec:
    """Specification for a loaded pretrained model."""

    module: nn.Module  # The pretrained model (TorchScript or nn.Module)
    in_dim: int  # Expected input dimension
    out_dim: int  # Output feature dimension
    is_torchscript: bool = False  # Whether the module is TorchScript
    source_path: Optional[str] = None  # Original path for metadata


@dataclass
class AdapterSpec:
    """Specification for adapters bridging pretrained model to environment."""

    pre_adapter: Optional[nn.Module]  # Maps env obs -> pretrained input
    adapter: Optional[nn.Module]  # Maps pretrained output -> target dim
    features_extractor_class: Optional[Callable]  # SB3 feature extractor class


@dataclass
class BootstrapArtifacts:
    """Complete bootstrap artifacts for RL integration."""

    pretrained: PretrainedSpec
    adapter_spec: AdapterSpec
    metadata: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Loading pretrained models
# ---------------------------------------------------------------------------


def load_pretrained(
    path: str,
    torchscript_in_dim: Optional[int] = None,
    adapter_hidden: Optional[List[int]] = None,
    device: str = "cpu",
    model_class: Optional[Callable[..., nn.Module]] = None,
    model_kwargs: Optional[Dict[str, Any]] = None,
) -> PretrainedSpec:
    """
    Load a pretrained model from TorchScript (.ts, .pt) or state_dict (.pth).

    For TorchScript files, the model is loaded directly.
    For state_dict files, you must provide model_class and model_kwargs to
    reconstruct the model architecture.

    Args:
        path: Path to pretrained model file.
        torchscript_in_dim: Input dimension for TorchScript models.
        adapter_hidden: Hidden dimensions for potential adapters (not used here).
        device: Device to load model to.
        model_class: Class to instantiate for state_dict loading.
        model_kwargs: Kwargs for model_class instantiation.

    Returns:
        PretrainedSpec with loaded module and inferred dimensions.
    """
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"Pretrained model not found: {path}")

    suffix = path_obj.suffix.lower()

    # Try TorchScript first
    is_torchscript = False
    ts_error = None
    if suffix in {".ts", ".pt"}:
        try:
            script_module = torch.jit.load(path, map_location=device)
            is_torchscript = True

            # Infer dimensions with dummy forward pass
            in_dim = torchscript_in_dim
            if in_dim is None:
                raise ValueError("torchscript_in_dim required for TorchScript models")

            with torch.no_grad():
                dummy = torch.zeros(1, in_dim, device=device)
                out = script_module(dummy)
                out_dim = out.shape[-1]

            module = TorchScriptFeatureExtractor(path, device=device)
            return PretrainedSpec(
                module=module,
                in_dim=in_dim,
                out_dim=out_dim,
                is_torchscript=True,
                source_path=path,
            )
        except ValueError:
            # Re-raise ValueError (e.g., missing torchscript_in_dim)
            raise
        except Exception as e:
            # Not a valid TorchScript, try state_dict
            ts_error = e

    # Load as state_dict
    if suffix == ".pth" or not is_torchscript:
        state = torch.load(path, map_location=device, weights_only=False)

        # Check if it's a bundle with metadata
        if isinstance(state, dict) and "policy_state_dict" in state:
            # This is a save_bundle format
            return _load_from_bundle(state, device, model_class, model_kwargs)

        # Plain state_dict
        if model_class is None:
            raise ValueError("model_class required for state_dict loading")
        model_kwargs = model_kwargs or {}
        model = model_class(**model_kwargs)
        model.load_state_dict(state)
        model = model.to(device)
        model.eval()

        # Infer dimensions
        in_dim = model_kwargs.get("input_dim", torchscript_in_dim)
        if in_dim is None:
            # Try to infer from first linear layer
            for m in model.modules():
                if isinstance(m, nn.Linear):
                    in_dim = m.in_features
                    break
        if in_dim is None:
            raise ValueError(
                "Could not infer input dimension; provide torchscript_in_dim"
            )

        with torch.no_grad():
            dummy = torch.zeros(1, in_dim, device=device)
            try:
                out = model(dummy)
                out_dim = out.shape[-1]
            except Exception:
                out_dim = in_dim  # Fallback

        return PretrainedSpec(
            module=model,
            in_dim=in_dim,
            out_dim=out_dim,
            is_torchscript=False,
            source_path=path,
        )

    raise ValueError(f"Could not load pretrained model from {path}")


def _load_from_bundle(
    state: Dict[str, Any],
    device: str,
    model_class: Optional[Callable] = None,
    model_kwargs: Optional[Dict] = None,
) -> PretrainedSpec:
    """Load pretrained spec from a save_bundle format."""
    obs_dim = state.get("obs_dim", 0)

    # If there's a torchscript path, try to load it
    ts_path = state.get("torchscript_path")
    if ts_path and os.path.exists(ts_path):
        return load_pretrained(ts_path, torchscript_in_dim=obs_dim, device=device)

    # Otherwise create a dummy module that returns obs as-is
    class IdentityModule(nn.Module):
        def forward(self, x: torch.Tensor) -> torch.Tensor:
            return x

    return PretrainedSpec(
        module=IdentityModule(),
        in_dim=obs_dim,
        out_dim=obs_dim,
        is_torchscript=False,
        source_path=None,
    )


# ---------------------------------------------------------------------------
# Building adapters
# ---------------------------------------------------------------------------


def build_adapters(
    env_obs_dim: int,
    pretrained: PretrainedSpec,
    adapter_mode: str,
    adapter_hidden: Optional[List[int]] = None,
) -> AdapterSpec:
    """
    Build pre-adapter (obs -> pretrained input) and adapter (output -> target)
    when dimensions don't match.

    Args:
        env_obs_dim: Environment observation dimension.
        pretrained: Loaded pretrained model specification.
        adapter_mode: "obs" for observation wrapper, "feature" for feature extractor.
        adapter_hidden: Hidden layer dimensions for adapters.

    Returns:
        AdapterSpec with pre_adapter, adapter, and optional features_extractor_class.
    """
    if adapter_hidden is None:
        adapter_hidden = []

    pre_adapter: Optional[nn.Module] = None
    adapter: Optional[nn.Module] = None

    # Pre-adapter: env obs -> pretrained input
    if pretrained.in_dim != env_obs_dim:
        pre_adapter = build_linear_adapter(
            env_obs_dim, pretrained.in_dim, hidden_dims=adapter_hidden
        )

    # Post-adapter: pretrained output -> target dim (for obs mode)
    if adapter_mode == "obs" and pretrained.out_dim != env_obs_dim:
        adapter = build_linear_adapter(
            pretrained.out_dim, env_obs_dim, hidden_dims=adapter_hidden
        )

    features_extractor_class: Optional[Callable] = None

    if adapter_mode == "feature":
        # Create a feature extractor class that wraps the pretrained module
        pretrained_module = pretrained.module
        _pre_adapter = pre_adapter
        _adapter = adapter

        class PretrainedFeatureExtractor(BaseFeaturesExtractor):
            def __init__(self, observation_space, features_dim: int = 256):
                super().__init__(observation_space, features_dim)
                self.pretrained = pretrained_module
                self.pre_adapter = _pre_adapter
                self.adapter = _adapter

                # Infer actual features dim
                with torch.no_grad():
                    dummy = torch.zeros(1, *observation_space.shape)
                    out = self._forward_impl(dummy)
                    self._features_dim = out.shape[-1]

            def _forward_impl(self, obs: torch.Tensor) -> torch.Tensor:
                out = obs
                if self.pre_adapter:
                    out = self.pre_adapter(out)
                if hasattr(self.pretrained, "eval"):
                    self.pretrained.eval()
                with torch.no_grad():
                    out = self.pretrained(out)
                if self.adapter:
                    out = self.adapter(out)
                return out

            def forward(self, obs: torch.Tensor) -> torch.Tensor:
                return self._forward_impl(obs)

        features_extractor_class = PretrainedFeatureExtractor

    return AdapterSpec(
        pre_adapter=pre_adapter,
        adapter=adapter,
        features_extractor_class=features_extractor_class,
    )


def create_bootstrap_artifacts(
    path: str,
    env_obs_dim: int,
    adapter_mode: str = "feature",
    torchscript_in_dim: Optional[int] = None,
    adapter_hidden: Optional[List[int]] = None,
    device: str = "cpu",
    model_class: Optional[Callable] = None,
    model_kwargs: Optional[Dict] = None,
) -> BootstrapArtifacts:
    """
    Complete bootstrap loading: load pretrained, build adapters, return artifacts.

    This is the main entry point for loading a pretrained model for RL integration.

    Args:
        path: Path to pretrained model.
        env_obs_dim: Environment observation dimension.
        adapter_mode: "obs" or "feature".
        torchscript_in_dim: Input dim for TorchScript models.
        adapter_hidden: Hidden dimensions for adapters.
        device: Device to load to.
        model_class: Class for state_dict loading.
        model_kwargs: Kwargs for model_class.

    Returns:
        BootstrapArtifacts containing pretrained spec, adapter spec, and metadata.
    """
    pretrained = load_pretrained(
        path,
        torchscript_in_dim=torchscript_in_dim or env_obs_dim,
        adapter_hidden=adapter_hidden,
        device=device,
        model_class=model_class,
        model_kwargs=model_kwargs,
    )

    adapter_spec = build_adapters(
        env_obs_dim=env_obs_dim,
        pretrained=pretrained,
        adapter_mode=adapter_mode,
        adapter_hidden=adapter_hidden,
    )

    metadata = {
        "source_path": path,
        "adapter_mode": adapter_mode,
        "env_obs_dim": env_obs_dim,
        "pretrained_in_dim": pretrained.in_dim,
        "pretrained_out_dim": pretrained.out_dim,
        "is_torchscript": pretrained.is_torchscript,
    }

    return BootstrapArtifacts(
        pretrained=pretrained,
        adapter_spec=adapter_spec,
        metadata=metadata,
    )


# ---------------------------------------------------------------------------
# Policy creation
# ---------------------------------------------------------------------------


def make_policy(
    algo: str,
    env,
    adapter_mode: str = "none",
    adapter_spec: Optional[AdapterSpec] = None,
    policy_kwargs: Optional[Dict[str, Any]] = None,
    **algo_kwargs,
):
    """
    Create PPO, SAC, A2C, or TD3 policy with optional pretrained feature extractor.

    Args:
        algo: Algorithm name ("ppo", "sac", "a2c", "td3").
        env: Gymnasium environment (or VecEnv).
        adapter_mode: "feature" to use pretrained as feature extractor.
        adapter_spec: AdapterSpec with features_extractor_class.
        policy_kwargs: Additional policy kwargs.
        **algo_kwargs: Algorithm-specific kwargs.

    Returns:
        SB3 model instance.
    """
    if not HAS_SB3:
        raise ImportError("stable-baselines3 required for make_policy")

    policy_kwargs = dict(policy_kwargs or {})

    if (
        adapter_mode == "feature"
        and adapter_spec
        and adapter_spec.features_extractor_class
    ):
        policy_kwargs["features_extractor_class"] = (
            adapter_spec.features_extractor_class
        )

    algo_map = {
        "ppo": PPO,
        "sac": SAC,
        "a2c": A2C,
        "td3": TD3,
    }

    algo_lower = algo.lower()
    if algo_lower not in algo_map:
        raise ValueError(
            f"Unsupported algo '{algo}'. Available: {list(algo_map.keys())}"
        )

    model = algo_map[algo_lower](
        "MlpPolicy", env, policy_kwargs=policy_kwargs, **algo_kwargs
    )
    return model


def make_obs_wrapper(
    pretrained: PretrainedSpec,
    adapter_spec: AdapterSpec,
    target_obs_dim: int,
):
    """
    Create an observation wrapper class for obs-mode adaptation.

    Returns a Gymnasium ObservationWrapper subclass that can be passed to
    make_vec_env as wrapper_class.
    """
    import gymnasium as gym

    _pretrained = pretrained
    _adapter_spec = adapter_spec
    _target_dim = target_obs_dim

    class AdapterObsWrapper(gym.ObservationWrapper):
        def __init__(self, env):
            super().__init__(env)
            self.pre_adapter = _adapter_spec.pre_adapter
            self.pretrained = _pretrained.module
            self.adapter = _adapter_spec.adapter
            self.observation_space = gym.spaces.Box(
                low=-float("inf"),
                high=float("inf"),
                shape=(_target_dim,),
                dtype=float,
            )

        def observation(self, observation):
            with torch.no_grad():
                obs_t = torch.as_tensor(observation, dtype=torch.float32)
                if obs_t.dim() == 1:
                    obs_t = obs_t.unsqueeze(0)

                out = obs_t
                if self.pre_adapter:
                    out = self.pre_adapter(out)
                out = self.pretrained(out)
                if self.adapter:
                    out = self.adapter(out)

                out_np = out.cpu().numpy()

            if observation.ndim == 1:
                out_np = out_np.squeeze(0)
            return out_np

    return AdapterObsWrapper


# ---------------------------------------------------------------------------
# Weight transfer
# ---------------------------------------------------------------------------


def transfer_weights(
    source: nn.Module,
    target: nn.Module,
    strict: bool = False,
    log_transfers: bool = True,
) -> Dict[str, str]:
    """
    Transfer matching weights from source to target model.

    Copies weights where both key name and shape match. Logs what was
    transferred and what was skipped.

    Args:
        source: Source model to copy weights from.
        target: Target model to copy weights to.
        strict: If True, raise error on any mismatch.
        log_transfers: If True, print transfer summary.

    Returns:
        Dict mapping parameter names to their transfer status.
    """
    source_state = source.state_dict()
    target_state = target.state_dict()

    transfer_log: Dict[str, str] = {}

    for key in target_state:
        if key in source_state:
            if source_state[key].shape == target_state[key].shape:
                target_state[key] = source_state[key].clone()
                transfer_log[key] = "transferred"
            else:
                msg = f"shape mismatch: {source_state[key].shape} vs {target_state[key].shape}"
                transfer_log[key] = msg
                if strict:
                    raise ValueError(f"Weight transfer failed for {key}: {msg}")
        else:
            transfer_log[key] = "not found in source"
            if strict:
                raise ValueError(f"Weight transfer failed: {key} not found in source")

    target.load_state_dict(target_state)

    if log_transfers:
        transferred = sum(1 for v in transfer_log.values() if v == "transferred")
        total = len(transfer_log)
        print(f"Weight transfer: {transferred}/{total} parameters transferred")
        skipped = [(k, v) for k, v in transfer_log.items() if v != "transferred"]
        if skipped:
            print(f"  Skipped: {len(skipped)} parameters")
            for k, v in skipped[:5]:
                print(f"    - {k}: {v}")
            if len(skipped) > 5:
                print(f"    ... and {len(skipped) - 5} more")

    return transfer_log


def transfer_weights_to_policy(
    pretrained: nn.Module,
    policy: nn.Module,
    target_layers: Optional[List[str]] = None,
    log_transfers: bool = True,
) -> Dict[str, str]:
    """
    Transfer weights from pretrained model to SB3 policy.

    Attempts to match pretrained layers to policy feature extractor or MLP layers.

    Args:
        pretrained: Pretrained source model.
        policy: SB3 policy model.
        target_layers: Specific layer names to target (optional).
        log_transfers: Whether to log transfer summary.

    Returns:
        Transfer log dict.
    """
    # Get the feature extractor or mlp_extractor from policy
    if hasattr(policy, "features_extractor"):
        target = policy.features_extractor
    elif hasattr(policy, "mlp_extractor"):
        target = policy.mlp_extractor
    else:
        # Try direct transfer to policy
        target = policy

    return transfer_weights(
        pretrained, target, strict=False, log_transfers=log_transfers
    )


# ---------------------------------------------------------------------------
# Save/load bundles
# ---------------------------------------------------------------------------


def save_bundle(
    model,
    adapter: Optional[nn.Module] = None,
    pre_adapter: Optional[nn.Module] = None,
    path: str = "policy_bundle.pth",
    torchscript_path: Optional[str] = None,
    adapter_mode: str = "none",
    obs_dim: Optional[int] = None,
    extra_metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Save SB3 model + adapters as a state_dict bundle for fallback loading.

    This is useful when the full SB3 .zip save fails due to TorchScript
    components or custom modules.

    Args:
        model: SB3 model (PPO, SAC, etc.).
        adapter: Post-encoder adapter module.
        pre_adapter: Pre-encoder adapter module.
        path: Output path for the bundle.
        torchscript_path: Original TorchScript path for metadata.
        adapter_mode: Adapter mode used ("obs", "feature", "none").
        obs_dim: Environment observation dimension.
        extra_metadata: Additional metadata to include.

    Returns:
        Path to saved bundle.
    """
    payload = {
        "policy_state_dict": model.policy.state_dict(),
        "adapter_state_dict": adapter.state_dict() if adapter else None,
        "pre_adapter_state_dict": pre_adapter.state_dict() if pre_adapter else None,
        "torchscript_path": torchscript_path,
        "adapter_mode": adapter_mode,
        "obs_dim": obs_dim,
        "metadata": extra_metadata or {},
    }

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    torch.save(payload, path)
    return path


def load_bundle(
    path: str,
    model=None,
    adapter: Optional[nn.Module] = None,
    pre_adapter: Optional[nn.Module] = None,
    device: str = "cpu",
) -> Dict[str, Any]:
    """
    Load a policy bundle and optionally restore state to provided models.

    Args:
        path: Path to bundle file.
        model: SB3 model to restore policy state to (optional).
        adapter: Adapter module to restore state to (optional).
        pre_adapter: Pre-adapter module to restore state to (optional).
        device: Device to load tensors to.

    Returns:
        Bundle dict with all saved data.
    """
    bundle = torch.load(path, map_location=device, weights_only=False)

    if model is not None and bundle.get("policy_state_dict"):
        model.policy.load_state_dict(bundle["policy_state_dict"])

    if adapter is not None and bundle.get("adapter_state_dict"):
        adapter.load_state_dict(bundle["adapter_state_dict"])

    if pre_adapter is not None and bundle.get("pre_adapter_state_dict"):
        pre_adapter.load_state_dict(bundle["pre_adapter_state_dict"])

    return bundle


# ---------------------------------------------------------------------------
# Legacy compatibility aliases
# ---------------------------------------------------------------------------


# Keep old function name for backwards compatibility
def load_pretrained_torchscript(
    torchscript_path: str,
    torchscript_in_dim: int,
    adapter_hidden: Optional[List[int]] = None,
    device: str = "cpu",
) -> PretrainedSpec:
    """Legacy alias for load_pretrained with TorchScript files."""
    return load_pretrained(
        path=torchscript_path,
        torchscript_in_dim=torchscript_in_dim,
        adapter_hidden=adapter_hidden,
        device=device,
    )
