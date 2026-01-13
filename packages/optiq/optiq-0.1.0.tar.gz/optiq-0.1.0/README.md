# optiq: imitation-first motion learning

optiq ingests FBX animations, converts them to Parquet/HDF5 datasets, trains sequence models (Transformer/MLP/UNet1D), and can bootstrap stable-baselines3 RL policies from pretrained encoders. Blender capture helpers remain available, but the primary flow is motion → dataset → model → RL/viz.

## Installation

optiq uses optional dependency groups ("extras") to keep the base install lightweight. Install only what you need:

### Quick Start (uv)

```bash
uv venv .venv
source .venv/bin/activate

# Minimal install (core only: numpy, torch, pydantic, click, scipy, trimesh)
uv pip install -e .

# Development install (everything)
uv pip install -e ".[dev]"
```

### Available Extras

| Extra   | Includes                                         | Use Case                          |
|---------|--------------------------------------------------|-----------------------------------|
| `ml`    | pytorch-lightning, torchmetrics, mlflow, h5py    | Model training & experiment tracking |
| `rl`    | stable-baselines3, gymnasium[mujoco], mujoco     | Reinforcement learning            |
| `viz`   | plotly, moviepy, matplotlib                      | Visualization & video rendering   |
| `web`   | fastapi, uvicorn, django, sqlmodel               | Web apps & APIs                   |
| `infra` | prometheus-client, kombu, redis                  | Monitoring & task queues          |
| `all`   | All of the above                                 | Full installation                 |
| `dev`   | All + pytest, pytest-cov                         | Development & testing             |

### Install Examples

```bash
# Just RL and visualization
pip install -e ".[rl,viz]"

# Web deployment with monitoring
pip install -e ".[web,infra]"

# ML training with visualization
pip install -e ".[ml,viz]"

# Everything
pip install -e ".[all]"
```

### pip (alternative to uv)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## CLI Overview

optiq provides a unified CLI with global options for reproducibility:

```bash
optiq [--seed INT] [--device cpu|cuda|mps|auto] COMMAND
```

### Data Commands

Convert motion files and attach labels:

```bash
# Convert JSON → Parquet with velocity computation
optiq data convert --in ground_truth.json --out seq.parquet --compute-velocities

# Attach sequence and frame labels
optiq data label --in seq.parquet --out seq_labeled.parquet \
  --label movement=walk \
  --frame-labels frame_labels.json \
  --label-names phase
```

### Train Commands

Train models using the registry or RL policies:

```bash
# Train a model (transformer, mlp, or unet1d)
optiq train model --config configs/model.yaml --arch transformer --out ckpt.pt

# Train an RL policy with optional pretrained encoder
optiq train rl --env Humanoid-v5 --algo ppo --total-steps 300000 --out policy.zip

# With pretrained encoder integration
optiq train rl --env Humanoid-v5 --algo ppo \
  --pretrained encoder.ts \
  --adapter-mode feature \
  --total-steps 300000 \
  --out policy.zip \
  --record-video
```

### Visualization Commands

```bash
# Plotly animation from predictions or dataset
optiq viz plotly --pred pred.json --out viz.html --tubes
optiq viz plotly --dataset seq.parquet --out viz.html

# Render policy rollout to video
optiq viz video --policy policy.zip --env Humanoid-v5 --out rollout.mp4
```

## Python API

### Data Pipeline
```python
from optiq.data import load_sequence, build_imitation_dataset, build_bc_dataset

seq = load_sequence("seq.parquet")
ds = build_imitation_dataset(seq, mode="next", horizon=1)
```

### Models
```python
from optiq.models import (
    build,
    available,
    list_models,
    load_checkpoint,
    export_torchscript,
)

# Discover models
print(list_models())  # ['mlp', 'transformer', 'unet1d']

# Transformer with causal mask and conditioning
model = build("transformer",
    input_dim=455,
    model_dim=128,
    num_layers=2,
    num_heads=4,
    causal=True,
    conditioning_dim=10,
)

# MLP with horizon (uses last N timesteps)
model = build("mlp",
    input_dim=455,
    hidden_dims=[256, 128],
    horizon=3,
)

# UNet1D with attention and diffusion support
model = build("unet1d",
    input_dim=455,
    base_channels=64,
    num_res_blocks=2,
    attention_layers=[0, 1],
    noise_schedule="linear",
)

# Standard forward signature for all models
out = model(prev_state, condition=cond_vec, context=timestep)

# Save / load checkpoints with metadata
torch.save({
    "arch": "mlp",
    "config": {"input_dim": 455, "output_dim": 455},
    "model_state_dict": model.state_dict(),
}, "ckpt.pth")
loaded_model, meta = load_checkpoint("ckpt.pth")

# Export TorchScript for RL adapters or serving
export_torchscript(model, example_input=torch.zeros(1, 455), out_path="model_ts.pt")
```

### Model Config Templates
- `configs/model_mlp.yaml`
- `configs/model_transformer.yaml`
- `configs/model_unet1d.yaml`

Each template includes optimizer (AdamW), scheduler (cosine), grad clipping, and dimensions for input/output/conditioning. Use them with `optiq train model --config configs/model_transformer.yaml`.

### RL Bootstrapping
```python
from optiq.rl import (
    load_pretrained,
    build_adapters,
    create_bootstrap_artifacts,
    make_policy,
    save_bundle,
    transfer_weights,
)

# Load pretrained encoder (TorchScript or state_dict)
pretrained = load_pretrained("encoder.ts", torchscript_in_dim=455)

# Build adapters for env observation dim matching
adapters = build_adapters(obs_dim, pretrained, adapter_mode="feature")

# Create SB3 policy with feature extractor
model = make_policy("ppo", env, adapter_mode="feature", adapter_spec=adapters)

# Or use one-call convenience function
artifacts = create_bootstrap_artifacts(
    path="encoder.ts",
    env_obs_dim=455,
    adapter_mode="feature",
)

# Save with fallback bundle for TorchScript compatibility
save_bundle(model, adapter=adapters.adapter, path="policy_bundle.pth")
```

## Quickstart (humanoid)

```bash
# Extract FBX → Parquet + train kinematic prior + optional Mujoco PPO bootstrap
uv run python examples/humanoid_imitation/run.py --fbx Walking.fbx --ppo-bootstrap
```

## Training Configs

Configs under `configs/` point to Parquet by default (convert via `optiq data convert`):
- `train_cnn_next.json`
- `train_unet_diffusion.yaml`
- `train_custom.yaml`

## Development

### Setup

```bash
# Install development dependencies
uv pip install -e .[dev]

# Setup git hooks for automatic formatting
./setup-hooks.sh
```

### Code Formatting

The pre-commit hook automatically formats code with:
- **black**: Code formatting (88 char line length)

To skip formatting for a specific commit:
```bash
git commit --no-verify
```

### Testing

```bash
# Run all tests
uv run pytest tests/

# Run with coverage
uv run pytest tests/ --cov=optiq --cov-report=html
```

## Legacy Blender capture (still available)

- Capture attributes in Blender and export to JSON/CSV/Parquet with `capture_selected_object` / `capture_object`.
- Convert captures to temporal graphs with `capture_to_temporal_graph` and sequence batches with `make_sequence_batches`.
- Example scripts remain under `examples/` for Blender-driven captures.

## License

MIT License © Ted T.
