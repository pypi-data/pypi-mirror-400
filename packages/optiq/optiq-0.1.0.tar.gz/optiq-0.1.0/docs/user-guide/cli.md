# CLI Reference

optiq provides a comprehensive command-line interface for all major operations. This guide covers the available commands and their options.

## Global Options

All optiq commands support these global options:

```bash
optiq [GLOBAL OPTIONS] COMMAND [COMMAND OPTIONS]
```

### Global Options

| Option | Description | Default |
|--------|-------------|---------|
| `--seed INT` | Random seed for reproducibility | None |
| `--device STR` | Device to use (cpu/cuda/mps/auto) | auto |
| `--help` | Show help message | - |
| `--version` | Show version information | - |

## Data Commands

### `optiq data convert`

Convert motion data files to optiq format.

```bash
optiq data convert [OPTIONS] --in INPUT --out OUTPUT
```

**Options:**
- `--in PATH` *(required)*: Input file path (FBX, JSON, etc.)
- `--out PATH` *(required)*: Output Parquet file path
- `--compute-velocities`: Compute velocity features from positions
- `--fps FLOAT`: Override FPS if not in source file
- `--normalize`: Normalize joint positions to [-1, 1]
- `--center`: Center motion around origin

**Examples:**
```bash
# Basic FBX conversion
optiq data convert --in walking.fbx --out walking.parquet

# With velocity computation
optiq data convert --in motion.fbx --out motion.parquet --compute-velocities

# Normalize and center
optiq data convert --in raw.fbx --out processed.parquet --normalize --center
```

### `optiq data label`

Add labels and metadata to motion datasets.

```bash
optiq data label [OPTIONS] --in INPUT --out OUTPUT
```

**Options:**
- `--in PATH` *(required)*: Input dataset path
- `--out PATH` *(required)*: Output labeled dataset path
- `--label KEY=VALUE`: Add sequence-level label
- `--frame-labels PATH`: JSON file with frame-level labels
- `--label-names STR`: Comma-separated label column names

**Examples:**
```bash
# Add movement type label
optiq data label --in motion.parquet --out labeled.parquet --label movement=walk

# Add phase labels from file
optiq data label --in motion.parquet --out labeled.parquet \
  --frame-labels phase_labels.json \
  --label-names stance,swing
```

### `optiq data validate`

Validate dataset integrity and format.

```bash
optiq data validate [OPTIONS] PATH
```

**Options:**
- `PATH`: Dataset file to validate
- `--verbose`: Show detailed validation output

## Training Commands

### `optiq train model`

Train motion prediction models.

```bash
optiq train model [OPTIONS] --config CONFIG --out OUTPUT
```

**Options:**
- `--config PATH` *(required)*: YAML configuration file
- `--data PATH`: Training dataset (or specify in config)
- `--out PATH` *(required)*: Output model checkpoint path
- `--arch STR`: Model architecture (mlp/transformer/unet1d)
- `--epochs INT`: Number of training epochs
- `--batch-size INT`: Training batch size
- `--lr FLOAT`: Learning rate
- `--device STR`: Training device
- `--checkpoint-freq INT`: Save checkpoint every N epochs

**Examples:**
```bash
# Train with config file
optiq train model --config configs/model_transformer.yaml --out model.pt

# Override config options
optiq train model --config configs/model.yaml --arch transformer \
  --epochs 100 --batch-size 32 --out custom_model.pt
```

### `optiq train rl`

Train reinforcement learning policies.

```bash
optiq train rl [OPTIONS] --env ENV --out OUTPUT
```

**Options:**
- `--env STR` *(required)*: Gymnasium environment name
- `--algo STR`: RL algorithm (ppo/sac/td3) [default: ppo]
- `--pretrained PATH`: Path to pretrained encoder
- `--adapter-mode STR`: How to use pretrained model (feature/frozen/fine-tune)
- `--total-steps INT`: Total training steps [default: 100000]
- `--out PATH` *(required)*: Output policy path
- `--eval-freq INT`: Evaluate every N steps
- `--save-freq INT`: Save checkpoint every N steps
- `--record-video`: Record training videos

**Examples:**
```bash
# Basic RL training
optiq train rl --env Humanoid-v5 --out policy.zip

# With pretrained encoder
optiq train rl --env Humanoid-v5 --pretrained encoder.pt \
  --adapter-mode feature --out bootstrapped_policy.zip
```

## Prediction Commands

### `optiq predict`

Generate predictions from trained models.

```bash
optiq predict [OPTIONS] --model MODEL --data DATA --out OUTPUT
```

**Options:**
- `--model PATH` *(required)*: Trained model checkpoint
- `--data PATH` *(required)*: Input dataset or sequence
- `--out PATH` *(required)*: Output predictions file
- `--horizon INT`: Prediction horizon (for autoregressive models)
- `--batch-size INT`: Inference batch size

**Examples:**
```bash
# Predict next states
optiq predict --model trained.pt --data test.parquet --out predictions.json

# Long-horizon prediction
optiq predict --model model.pt --data sequence.parquet --out forecast.json --horizon 100
```

## Visualization Commands

### `optiq viz plotly`

Create interactive motion plots.

```bash
optiq viz plotly [OPTIONS] --out OUTPUT [DATA OPTIONS]
```

**Options:**
- `--out PATH` *(required)*: Output HTML file
- `--dataset PATH`: Dataset to visualize
- `--pred PATH`: Predictions to overlay
- `--ground-truth PATH`: Ground truth for comparison
- `--tubes`: Show uncertainty tubes
- `--joint-names PATH`: JSON file with joint names
- `--fps FLOAT`: Animation frame rate

**Examples:**
```bash
# Visualize dataset
optiq viz plotly --dataset motion.parquet --out visualization.html

# Compare predictions
optiq viz plotly --dataset test.parquet --pred predictions.json --out comparison.html
```

### `optiq viz video`

Generate videos from policies or datasets.

```bash
optiq viz video [OPTIONS] --out OUTPUT
```

**Options:**
- `--policy PATH`: Trained policy for rollout
- `--env STR`: Environment name (with policy)
- `--dataset PATH`: Dataset for animation (alternative to policy)
- `--out PATH` *(required)*: Output video file
- `--duration FLOAT`: Video duration in seconds
- `--fps INT`: Video frame rate
- `--width INT`: Video width
- `--height INT`: Video height

**Examples:**
```bash
# Policy rollout video
optiq viz video --policy policy.zip --env Humanoid-v5 --out rollout.mp4

# Dataset animation
optiq viz video --dataset motion.parquet --out animation.mp4 --fps 30
```

## Configuration Files

### Model Configuration

Example `model_config.yaml`:

```yaml
# Model architecture
arch: transformer
input_dim: 465
output_dim: 465
hidden_dim: 256
num_layers: 6
num_heads: 8

# Training parameters
lr: 1e-4
batch_size: 32
epochs: 100
grad_clip: 1.0

# Data parameters
seq_len: 128
horizon: 1

# Optimizer
optimizer:
  name: adamw
  weight_decay: 1e-4

# Scheduler
scheduler:
  name: cosine
  warmup_steps: 1000
```

### RL Configuration

Example `rl_config.yaml`:

```yaml
# Environment
env: Humanoid-v5
normalize_obs: true
normalize_reward: true

# Algorithm
algo: ppo
learning_rate: 3e-4
batch_size: 2048
n_epochs: 10

# Policy network
policy_kwargs:
  net_arch: [256, 256]

# Pretraining (optional)
pretrained_encoder: path/to/encoder.pt
adapter_mode: feature  # feature/frozen/fine-tune
```

## Error Handling

### Common Exit Codes

- `0`: Success
- `1`: General error
- `2`: Configuration error
- `3`: File not found
- `4`: Invalid data format

### Debugging

Enable verbose logging:

```bash
export OPTIQ_LOG_LEVEL=DEBUG
optiq command --help
```

Check data integrity:

```bash
optiq data validate dataset.parquet --verbose
```

## Next Steps

- [Installation Guide](../installation.md)
- [Quick Start Tutorial](../quickstart.md)
- [API Reference](api.md)
- [Configuration Examples](../examples/index.md)
