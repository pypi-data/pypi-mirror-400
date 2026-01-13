# Tutorials

## 1. Data pipeline: FBX → Parquet → dataset

1) Extract or convert animation:
```bash
# Using the Node extractor (kept in scripts/) to generate ground_truth.json
node scripts/extract_fbx_anim.js examples/humanoid_imitation/Walking.fbx examples/humanoid_imitation/data/ground_truth.json --fps=30
```
Then convert that JSON to Parquet:
```bash
optiq data convert --in examples/humanoid_imitation/data/ground_truth.json --out examples/humanoid_imitation/data/ground_truth.parquet --compute-velocities
```
2) Label (optional):
```bash
optiq data label --in examples/humanoid_imitation/data/ground_truth.parquet --out examples/humanoid_imitation/data/ground_truth_labeled.parquet --label movement=walk
```
3) Load in Python:
```python
from optiq.data import load_sequence, build_imitation_dataset
seq = load_sequence("examples/humanoid_imitation/data/ground_truth_labeled.parquet")
ds = build_imitation_dataset(seq, mode="next", horizon=1)
```

## 2. Train a model (CLI)

Train a model using the registry with a YAML/JSON config:

```bash
# Create a config file (configs/transformer.yaml)
cat > configs/transformer.yaml << 'EOF'
input_dim: 455
output_dim: 455
model_dim: 128
num_layers: 2
num_heads: 4
epochs: 100
batch_size: 32
lr: 0.001
EOF

# Train using the CLI
optiq --seed 42 train model \
  --config configs/model_transformer.yaml \
  --arch transformer \
  --out models/motion_transformer.pt
```

Or use config overrides:
```bash
optiq train model \
  --config configs/transformer.yaml \
  --arch mlp \
  --out models/motion_mlp.pt \
  --epochs 50 \
  --override hidden_dim=256
```

### Train a model (Python)

```python
from optiq.models import build, available
import torch

# See available models
print(available().keys())  # {'mlp', 'transformer', 'unet1d'}

# Basic transformer
model = build("transformer", input_dim=455, model_dim=128, num_layers=2, num_heads=4)
x = torch.randn(1, 10, 455)  # (batch, seq_len, features)
out = model(x)
print(out.shape)  # (1, 455)
```

### Advanced Model Configuration

All models follow a standardized forward signature: `forward(prev_state, condition=None, context=None) -> next_state`

```python
from optiq.models import build
import torch

# Transformer with causal mask and conditioning
model = build("transformer",
    input_dim=455,
    model_dim=256,
    num_layers=4,
    num_heads=8,
    causal=True,              # Enable causal (autoregressive) masking
    conditioning_dim=10,      # Size of conditioning vector
    ff_mult=4,                # Feedforward dimension multiplier
    max_seq_len=1000,         # Maximum sequence length
)

x = torch.randn(4, 20, 455)   # (batch, seq_len, features)
cond = torch.randn(4, 10)     # (batch, conditioning_dim)
out = model(x, condition=cond)

# MLP with multi-timestep horizon
model = build("mlp",
    input_dim=455,
    hidden_dims=[512, 256, 128],
    horizon=5,                # Flatten last 5 timesteps as input
    conditioning_dim=10,
)

# UNet1D with attention and diffusion noise scheduling
model = build("unet1d",
    input_dim=455,
    base_channels=64,
    num_res_blocks=2,
    num_levels=3,
    attention_layers=[1, 2],  # Add attention at these levels
    noise_schedule="linear",  # Enable diffusion-style conditioning
    time_emb_dim=128,
)

# For diffusion, pass timestep as context
x = torch.randn(4, 32, 455)
timestep = torch.randint(0, 1000, (4,))
out = model(x, context=timestep)
```

## 3. RL Training (CLI)

Train an RL policy with optional pretrained encoder:

```bash
# Basic PPO training on Humanoid
optiq train rl \
  --env Humanoid-v5 \
  --algo ppo \
  --total-steps 100000 \
  --out policies/humanoid_ppo.zip \
  --n-envs 4

# With pretrained encoder (feature mode)
optiq train rl \
  --env Humanoid-v5 \
  --algo ppo \
  --pretrained models/fbx_encoder.ts \
  --adapter-mode feature \
  --total-steps 300000 \
  --out policies/humanoid_ppo_pretrained.zip \
  --record-video

# With config file for hyperparameters
optiq --seed 42 --device cuda train rl \
  --env Humanoid-v5 \
  --algo sac \
  --config configs/rl_hyperparams.yaml \
  --total-steps 500000 \
  --out policies/humanoid_sac.zip
```

### RL Bootstrap (Python API)

For programmatic control over RL bootstrapping:

```python
from optiq.rl import (
    load_pretrained,
    build_adapters,
    create_bootstrap_artifacts,
    make_policy,
    save_bundle,
    transfer_weights,
)
import gymnasium as gym
from stable_baselines3.common.env_util import make_vec_env

# Load pretrained encoder (TorchScript or state_dict)
pretrained = load_pretrained(
    path="encoder.ts",
    torchscript_in_dim=455,
    device="cpu",
)

# Build adapters for dimension matching
adapter_spec = build_adapters(
    env_obs_dim=455,           # Env observation dimension
    pretrained=pretrained,
    adapter_mode="feature",    # Use as feature extractor
    adapter_hidden=[256],      # Hidden dims for adapters
)

# Create SB3 policy with feature extractor
env = make_vec_env("Humanoid-v5", n_envs=4)
model = make_policy(
    algo="ppo",
    env=env,
    adapter_mode="feature",
    adapter_spec=adapter_spec,
    learning_rate=3e-4,
)

# Train
model.learn(total_timesteps=100000)

# Save with fallback bundle
model.save("policy.zip")
save_bundle(
    model=model,
    adapter=adapter_spec.adapter,
    pre_adapter=adapter_spec.pre_adapter,
    path="policy_bundle.pth",
    torchscript_path="encoder.ts",
    adapter_mode="feature",
)
```

Or use the convenience function for complete setup:

```python
from optiq.rl import create_bootstrap_artifacts

# One-call setup
artifacts = create_bootstrap_artifacts(
    path="encoder.ts",
    env_obs_dim=455,
    adapter_mode="feature",
    torchscript_in_dim=455,
)

# Access components
pretrained = artifacts.pretrained
adapter_spec = artifacts.adapter_spec
metadata = artifacts.metadata
```

### RL bootstrap (legacy script)

```bash
uv run python examples/humanoid_imitation/run.py --fbx Walking.fbx --ppo-bootstrap --ppo-steps 50000
```

## 4. Visualize with Plotly

```bash
# From prediction JSON
optiq viz plotly \
  --pred examples/humanoid_imitation/data/ground_truth.json \
  --gt examples/humanoid_imitation/data/ground_truth.json \
  --out anim.html \
  --tubes

# From Parquet dataset
optiq viz plotly \
  --dataset examples/humanoid_imitation/data/ground_truth.parquet \
  --out anim.html \
  --title "Motion Visualization"
```

The Plotly output overlays prediction and ground truth skeletons and shows a loss curve (avg L2 error) below the animation; the "Loop (x3)" button replays the animation three times.

## 5. Render policy video

```bash
optiq viz video \
  --policy examples/humanoid_imitation/data/mujoco_humanoid_ppo.zip \
  --env Humanoid-v5 \
  --out videos/ppo_rollout.mp4 \
  --steps 2000 \
  --fps 30
```

## 6. Pretrain and export a TorchScript encoder from FBX data

```bash
# Convert the Node-extracted JSON to Parquet (if not already)
optiq data convert \
  --in examples/humanoid_imitation/data/ground_truth.json \
  --out examples/humanoid_imitation/data/ground_truth.parquet \
  --compute-velocities

# Quick autoencoder pretrain + TorchScript export
uv run python - <<'PY'
import json
from pathlib import Path
import torch
from examples.humanoid_imitation.run import TinyAutoencoder, FBXDataSet, _export_torchscript_encoder

data_path = Path("examples/humanoid_imitation/data/ground_truth.parquet")
ds = FBXDataSet(str(data_path))
in_dim = ds[0][0].numel()
model = TinyAutoencoder(input_dim=in_dim)
opt = torch.optim.Adam(model.parameters(), lr=1e-3)
loader = torch.utils.data.DataLoader(ds, batch_size=64, shuffle=True)
model.train()
for _ in range(5):
    for x, _ in loader:
        opt.zero_grad()
        recon = model(x)
        loss = torch.nn.functional.mse_loss(recon, x)
        loss.backward()
        opt.step()
out_ts = Path("examples/humanoid_imitation/data/fbx_encoder.ts")
_export_torchscript_encoder(model, in_dim, out_ts)
print("Exported TorchScript encoder to", out_ts)
PY
```

You can then point the RL training to this encoder:

```bash
optiq train rl \
  --env Humanoid-v5 \
  --algo ppo \
  --pretrained examples/humanoid_imitation/data/fbx_encoder.ts \
  --adapter-mode obs \
  --total-steps 50000 \
  --out policies/humanoid_ppo_pretrained.zip
```

Or use the legacy script for end-to-end (pretrain + export + PPO):

```bash
uv run python examples/humanoid_imitation/bootstrap_from_fbx.py \
  --data examples/humanoid_imitation/data/ground_truth.parquet \
  --ts-out examples/humanoid_imitation/data/fbx_encoder.ts \
  --epochs 5 \
  --ppo-steps 50000 \
  --adapter-mode obs

If you run outside the repo root, prepend:

```bash
PYTHONPATH=$(pwd)
```

## Generate predictions and Plotly comparison

After training a checkpoint (e.g., `models/motion_transformer.pt`), create a prediction JSON and compare with ground truth:

```bash
# Generate predictions
uv run python examples/humanoid_imitation/predict_to_json.py \
  --checkpoint models/motion_transformer.pt \
  --dataset examples/humanoid_imitation/data/ground_truth.parquet \
  --out examples/humanoid_imitation/data/predictions.json

# Visualize comparison (pred vs ground truth)
uv run optiq viz plotly \
  --pred examples/humanoid_imitation/data/predictions.json \
  --gt   examples/humanoid_imitation/data/ground_truth.json \
  --out  examples/humanoid_imitation/data/anim_compare.html \
  --tubes

Notes:
- The prediction script reads `input_dim` from the checkpoint; if the model outputs fewer features than the dataset bones expect, it will truncate to the available bones and warn. For best results, train with a model whose `input_dim` matches the dataset feature dimension (7 * num_bones).

### Training with Lightning (data_path required)

The CLI now runs a PyTorch Lightning loop. Your config must include a `data_path` pointing to your dataset, for example:

```yaml
# configs/model_transformer.yaml
data_path: examples/humanoid_imitation/data/ground_truth_labeled.parquet
epochs: 50
batch_size: 64
lr: 0.0003
```

Then train:

```bash
uv run optiq train model \
  --config configs/model_transformer.yaml \
  --arch transformer \
  --out models/motion_transformer.pt
```

You can also override without editing the file:

```bash
uv run optiq train model \
  --config configs/model_transformer.yaml \
  --arch transformer \
  --out models/motion_transformer.pt \
  --override data_path=examples/humanoid_imitation/data/ground_truth_labeled.parquet \
  --override epochs=50
```

Custom LightningModule (optional):

```yaml
lightning_module: path/to/my_lit_module.py:MyLitModule
```

The custom class should subclass `pl.LightningModule` and can take either `(model, config)` or just `(model)` in its constructor.
```

If running outside the repo root, prepend `PYTHONPATH=$(pwd)` to the first command so the script can import `optiq`. The prediction JSON uses the format expected by `optiq viz plotly`: `{"fps": int, "bones": {bone: [{position: [x,y,z], quaternion: [w,x,y,z]}, ...]}}`.
```

## CLI Reference

### Global Options
- `--seed INT` - Random seed for reproducibility
- `--device TEXT` - Device: cpu, cuda, mps, or auto (default: auto)

### Data Commands
```bash
optiq data convert --in INPUT --out OUTPUT [--format parquet|hdf5] [--compute-velocities] [--compression snappy|gzip]
optiq data label --in INPUT --out OUTPUT --label KEY=VALUE [--frame-labels FILE] [--label-names NAMES]
```

### Train Commands
```bash
optiq train model --config FILE --out OUTPUT [--arch mlp|transformer|unet1d] [--epochs N] [--batch-size N] [--lr FLOAT] [--override KEY=VALUE]
optiq train rl --env ENV_ID --out OUTPUT [--algo ppo|sac|a2c|td3] [--total-steps N] [--pretrained FILE] [--adapter-mode obs|feature] [--n-envs N] [--record-video] [--config FILE]
optiq train legacy --config FILE --output FILE [--data FILE]
```

### Visualization Commands
```bash
optiq viz plotly --out OUTPUT [--pred FILE] [--dataset FILE] [--gt FILE] [--edges FILE] [--tubes|--no-tubes] [--title TEXT]
optiq viz video --policy FILE --env ENV_ID --out OUTPUT [--steps N] [--fps N]
```
