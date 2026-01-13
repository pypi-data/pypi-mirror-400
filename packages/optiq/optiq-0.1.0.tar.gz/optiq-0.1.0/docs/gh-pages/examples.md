# Examples

## Data Conversion

```bash
# Convert FBX-extracted JSON to Parquet
optiq data convert \
  --in examples/humanoid_imitation/data/ground_truth.json \
  --out examples/humanoid_imitation/data/ground_truth.parquet \
  --compute-velocities

# Add labels
optiq data label \
  --in examples/humanoid_imitation/data/ground_truth.parquet \
  --out examples/humanoid_imitation/data/ground_truth_labeled.parquet \
  --label movement=walk \
  --label style=natural
```

## Model Training

```bash
# Train a transformer model
optiq --seed 42 train model \
  --config configs/transformer.yaml \
  --arch transformer \
  --out models/motion_transformer.pt \
  --epochs 100

# Train with config overrides
optiq train model \
  --config configs/model.yaml \
  --arch mlp \
  --out models/motion_mlp.pt \
  --override hidden_dims=[256,128]
```

## RL Training

```bash
# Basic PPO training
optiq train rl \
  --env Humanoid-v5 \
  --algo ppo \
  --total-steps 300000 \
  --out policies/humanoid_ppo.zip \
  --n-envs 4

# With pretrained encoder
optiq train rl \
  --env Humanoid-v5 \
  --algo ppo \
  --pretrained models/fbx_encoder.ts \
  --adapter-mode feature \
  --total-steps 300000 \
  --out policies/humanoid_pretrained.zip \
  --record-video
```

## Plotly Animation

```bash
# From prediction JSON
optiq viz plotly \
  --pred examples/humanoid_imitation/data/ground_truth.json \
  --out anim.html \
  --tubes

# With ground truth comparison
optiq viz plotly \
  --pred examples/humanoid_imitation/data/pred.json \
  --gt examples/humanoid_imitation/data/ground_truth.json \
  --out comparison.html \
  --tubes

# From Parquet dataset
optiq viz plotly \
  --dataset examples/humanoid_imitation/data/ground_truth.parquet \
  --out anim.html \
  --title "Walking Animation"
```

## Policy Video Rendering

```bash
optiq viz video \
  --policy examples/humanoid_imitation/data/mujoco_humanoid_ppo.zip \
  --env Humanoid-v5 \
  --out videos/ppo_rollout.mp4 \
  --steps 2000 \
  --fps 30
```

## Python: Load Dataset and Model

```python
from optiq.data import load_sequence, build_imitation_dataset
from optiq.models import build
import torch

seq = load_sequence("extracted_jogging/jogging_anim.parquet")
ds = build_imitation_dataset(seq, mode="next", horizon=1)
x, y, cond = ds[0]
model = build("mlp", input_dim=x.numel(), hidden_dims=[128, 64])
out = model(x.unsqueeze(0))
print(out.shape)
```

## Behavior Cloning Dataset

```python
from optiq.data.datasets import build_bc_dataset
ds = build_bc_dataset("extracted_jogging/jogging_anim.parquet", env_id="Humanoid-v5")
obs, act = ds[0]
print(obs.shape, act.shape)
```

## Humanoid Pipeline (Legacy Script)

```bash
uv run python examples/humanoid_imitation/run.py \
  --fbx Walking.fbx \
  --ppo-bootstrap \
  --ppo-steps 50000 \
  --ae-epochs 5
```

## End-to-End Bootstrap from FBX

```bash
# Pretrain encoder + export TorchScript + train PPO
uv run python examples/humanoid_imitation/bootstrap_from_fbx.py \
  --data examples/humanoid_imitation/data/ground_truth.parquet \
  --ts-out models/fbx_encoder.ts \
  --epochs 5 \
  --ppo-steps 50000 \
  --adapter-mode feature
```
