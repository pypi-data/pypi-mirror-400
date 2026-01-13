## SB3 Bootstrapping and Weight Initialization

**Status: IMPLEMENTED** (see `src/optiq/rl/bootstrap.py`)

### Implemented SB3 Bootstrap Flow

1. **Load pretrained model** (TorchScript or state_dict) from disk
2. **Infer feature dimensions**; if mismatch with env obs dim, build `LinearAdapter`
3. **Choose adapter mode**:
   - `obs`: wrap env observation with adapter/pretrained encoder → policy sees adapted obs
   - `feature`: use pretrained encoder as `BaseFeaturesExtractor` inside SB3 policy
4. **Initialize PPO/SAC policy weights** (optional):
   - If compatible shapes, copy matching layers from pretrained model
   - Fall back to random init for unmatched layers; log what was transferred
5. **Save checkpoints**:
   - Primary: SB3 `.zip`
   - Fallback: `state_dict` bundle containing policy + adapters + metadata

### Implemented APIs

#### Data Classes

```python
from optiq.rl import PretrainedSpec, AdapterSpec, BootstrapArtifacts

# PretrainedSpec: loaded model info
pretrained = PretrainedSpec(
    module=encoder,        # nn.Module or TorchScript
    in_dim=455,            # Input dimension
    out_dim=128,           # Output feature dimension
    is_torchscript=True,   # Whether TorchScript
    source_path="enc.ts",  # Original file path
)

# AdapterSpec: adapter modules
adapter_spec = AdapterSpec(
    pre_adapter=pre_adapter,           # Maps env obs -> encoder input
    adapter=post_adapter,              # Maps encoder output -> target
    features_extractor_class=FEClass,  # SB3 feature extractor class
)

# BootstrapArtifacts: complete bundle
artifacts = BootstrapArtifacts(
    pretrained=pretrained,
    adapter_spec=adapter_spec,
    metadata={"adapter_mode": "feature", ...},
)
```

#### Loading Functions

```python
from optiq.rl import load_pretrained, create_bootstrap_artifacts

# Load TorchScript encoder
pretrained = load_pretrained(
    path="encoder.ts",
    torchscript_in_dim=455,
    device="cpu",
)

# Load state_dict (requires model class)
pretrained = load_pretrained(
    path="encoder.pth",
    torchscript_in_dim=455,
    model_class=MyEncoder,
    model_kwargs={"input_dim": 455, "hidden_dim": 128},
)

# Complete bootstrap in one call
artifacts = create_bootstrap_artifacts(
    path="encoder.ts",
    env_obs_dim=455,
    adapter_mode="feature",
    torchscript_in_dim=455,
    adapter_hidden=[256],
)
```

#### Adapter Building

```python
from optiq.rl import build_adapters, build_linear_adapter

# Build adapters for dimension matching
adapter_spec = build_adapters(
    env_obs_dim=455,
    pretrained=pretrained,
    adapter_mode="feature",  # or "obs"
    adapter_hidden=[256, 128],
)

# Build a simple linear adapter
adapter = build_linear_adapter(
    in_dim=128,
    out_dim=455,
    hidden_dims=[256],
    dropout=0.1,
)
```

#### Policy Creation

```python
from optiq.rl import make_policy, make_obs_wrapper

# Create SB3 policy with feature extractor
model = make_policy(
    algo="ppo",
    env=env,
    adapter_mode="feature",
    adapter_spec=adapter_spec,
    verbose=1,
    learning_rate=3e-4,
)

# Create observation wrapper for obs-mode
wrapper_class = make_obs_wrapper(
    pretrained=pretrained,
    adapter_spec=adapter_spec,
    target_obs_dim=455,
)
env = make_vec_env(env_id, wrapper_class=wrapper_class)
```

#### Weight Transfer

```python
from optiq.rl import transfer_weights, transfer_weights_to_policy

# Transfer matching weights between models
log = transfer_weights(
    source=pretrained_model,
    target=policy_model,
    strict=False,      # Don't error on mismatches
    log_transfers=True,
)

# Transfer to SB3 policy
log = transfer_weights_to_policy(
    pretrained=encoder,
    policy=model.policy,
    log_transfers=True,
)
```

#### Save/Load Bundles

```python
from optiq.rl import save_bundle, load_bundle

# Save policy + adapters as state_dict bundle
save_bundle(
    model=model,
    adapter=adapter_spec.adapter,
    pre_adapter=adapter_spec.pre_adapter,
    path="policy_bundle.pth",
    torchscript_path="encoder.ts",
    adapter_mode="feature",
    obs_dim=455,
)

# Load bundle
bundle = load_bundle("policy_bundle.pth")
# Optionally restore to models
bundle = load_bundle("policy_bundle.pth", model=model, adapter=adapter)
```

### CLI Integration

The `optiq train rl` command uses these bootstrap helpers:

```bash
# Train with pretrained encoder
optiq train rl \
  --env Humanoid-v5 \
  --algo ppo \
  --pretrained encoder.ts \
  --adapter-mode feature \
  --total-steps 300000 \
  --out policy.zip
```

### Tests

Comprehensive tests in `tests/unit/rl/test_bootstrap.py` (25 tests):
- TorchScript loading (3 tests)
- State dict loading (3 tests)
- Adapter building (3 tests)
- Bootstrap artifacts (2 tests)
- Linear adapter (4 tests)
- Weight transfer (4 tests)
- Save/load bundles (3 tests)
- Integration workflows (3 tests)

### Migration Notes

- Legacy `examples/humanoid_imitation/train_mujoco.py` continues to work
- The `optiq.rl` module now exports all bootstrap functions via `__init__.py`
- `PretrainedSpec` replaces the old simpler dataclass structure
- `create_bootstrap_artifacts()` provides a single entry point for common workflows
