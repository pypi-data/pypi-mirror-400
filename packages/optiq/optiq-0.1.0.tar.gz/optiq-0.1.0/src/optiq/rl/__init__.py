"""RL integration module for optiq.

Provides utilities for bootstrapping SB3 policies from pretrained models.
"""

from .adapter import (
    LinearAdapter,
    TorchScriptFeatureExtractor,
    build_linear_adapter,
    infer_linear_adapter_from_models,
)
from .bootstrap import (
    AdapterSpec,
    BootstrapArtifacts,
    PretrainedSpec,
    build_adapters,
    create_bootstrap_artifacts,
    load_bundle,
    load_pretrained,
    make_obs_wrapper,
    make_policy,
    save_bundle,
    transfer_weights,
    transfer_weights_to_policy,
)

__all__ = [
    # Adapter classes
    "LinearAdapter",
    "TorchScriptFeatureExtractor",
    "build_linear_adapter",
    "infer_linear_adapter_from_models",
    # Bootstrap dataclasses
    "PretrainedSpec",
    "AdapterSpec",
    "BootstrapArtifacts",
    # Bootstrap functions
    "load_pretrained",
    "build_adapters",
    "create_bootstrap_artifacts",
    "make_policy",
    "make_obs_wrapper",
    "transfer_weights",
    "transfer_weights_to_policy",
    "save_bundle",
    "load_bundle",
]
