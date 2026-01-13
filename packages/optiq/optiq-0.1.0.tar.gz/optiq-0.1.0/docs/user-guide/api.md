# API Reference

This page provides a comprehensive reference for the optiq Python API.

## Core Modules

### Data Processing

#### `optiq.data`

```python
from optiq.data import load_sequence, build_imitation_dataset, build_bc_dataset
```

**Functions:**
- `load_sequence(path: str) -> MotionSequence`: Load motion data from file
- `build_imitation_dataset(sequence, mode="next", horizon=1) -> Dataset`: Create imitation learning dataset
- `build_bc_dataset(sequence, labels) -> Dataset`: Create behavior cloning dataset

**Classes:**
- `MotionSequence`: Container for motion capture data
- `MotionDataset`: PyTorch dataset for motion data

### Model Building

#### `optiq.models`

```python
from optiq.models import build, available, load_checkpoint, export_torchscript
```

**Functions:**
- `build(arch: str, **kwargs) -> nn.Module`: Build model by architecture name
- `available() -> List[str]`: List available model architectures
- `load_checkpoint(path: str) -> Tuple[nn.Module, dict]`: Load trained model and metadata
- `export_torchscript(model, example_input, path: str)`: Export model to TorchScript

**Available Architectures:**
- `"mlp"`: Multi-layer perceptron for motion prediction
- `"transformer"`: Transformer-based sequence model
- `"unet1d"`: U-Net architecture for motion generation

### Training

#### `optiq.training`

```python
from optiq.training import Trainer, Config
```

**Classes:**
- `Trainer`: High-level training interface
- `Config`: Training configuration container

**Key Methods:**
- `Trainer.fit(model, dataset, config)`: Train a model
- `Trainer.evaluate(model, dataset)`: Evaluate model performance
- `Config.from_yaml(path)`: Load configuration from YAML

### RL Integration

#### `optiq.rl`

```python
from optiq.rl import bootstrap_policy, create_adapter, load_pretrained
```

**Functions:**
- `bootstrap_policy(env, pretrained_model, **kwargs)`: Create RL policy with pretrained encoder
- `create_adapter(obs_dim, encoder, mode="feature")`: Create observation adapter
- `load_pretrained(path, **kwargs)`: Load pretrained model for RL

### Visualization

#### `optiq.viz`

```python
from optiq.viz import plot_motion, create_animation, comparative_plot
```

**Functions:**
- `plot_motion(sequence, **kwargs)`: Create interactive motion plot
- `create_animation(sequence, **kwargs)`: Generate motion animation
- `comparative_plot(pred, target, **kwargs)`: Compare predictions vs ground truth

## Model Architectures

### MLP Architecture

```python
model = optiq.models.build(
    "mlp",
    input_dim=465,      # Input feature dimension
    hidden_dims=[256, 128],  # Hidden layer sizes
    output_dim=465,     # Output feature dimension
    horizon=1,          # Prediction horizon
    dropout=0.1         # Dropout probability
)
```

**Parameters:**
- `input_dim`: Input feature dimension
- `hidden_dims`: List of hidden layer sizes
- `output_dim`: Output feature dimension
- `horizon`: Number of timesteps to predict
- `dropout`: Dropout probability
- `activation`: Activation function ('relu', 'gelu', etc.)

### Transformer Architecture

```python
model = optiq.models.build(
    "transformer",
    input_dim=465,
    model_dim=256,      # Internal model dimension
    num_layers=6,       # Number of transformer layers
    num_heads=8,        # Number of attention heads
    causal=True,        # Causal attention mask
    conditioning_dim=10 # Optional conditioning input
)
```

**Parameters:**
- `input_dim`: Input feature dimension
- `model_dim`: Internal model dimension
- `num_layers`: Number of transformer blocks
- `num_heads`: Number of attention heads
- `causal`: Use causal attention for autoregressive modeling
- `conditioning_dim`: Dimension of conditioning input
- `dropout`: Dropout probability

### U-Net 1D Architecture

```python
model = optiq.models.build(
    "unet1d",
    input_dim=465,
    base_channels=64,   # Base number of channels
    num_res_blocks=3,   # Residual blocks per level
    attention_layers=[1, 2],  # Layers with attention
    noise_schedule="linear"   # For diffusion models
)
```

**Parameters:**
- `input_dim`: Input feature dimension
- `base_channels`: Base number of convolutional channels
- `num_res_blocks`: Residual blocks per resolution level
- `attention_layers`: Which layers get attention blocks
- `noise_schedule`: Noise schedule for diffusion ('linear', 'cosine')

## Data Structures

### MotionSequence

Container for motion capture data with temporal indexing.

```python
class MotionSequence:
    @property
    def data(self) -> np.ndarray: ...        # Shape: (frames, joints * 3)
    @property
    def joint_count(self) -> int: ...        # Number of joints
    @property
    def fps(self) -> float: ...              # Frames per second
    @property
    def duration(self) -> float: ...         # Total duration in seconds

    def __len__(self) -> int: ...            # Number of frames
    def __getitem__(self, idx) -> np.ndarray: ...  # Get frame by index
```

### MotionDataset

PyTorch dataset for motion sequences.

```python
class MotionDataset(Dataset):
    def __init__(self, sequences: List[MotionSequence], **kwargs): ...

    def __len__(self) -> int: ...
    def __getitem__(self, idx) -> Dict[str, torch.Tensor]: ...
```

## Configuration

### Training Configuration

YAML configuration for training:

```yaml
# Model
model:
  arch: transformer
  input_dim: 465
  model_dim: 256
  num_layers: 6

# Data
data:
  batch_size: 32
  seq_len: 128
  num_workers: 4

# Training
training:
  epochs: 100
  lr: 1e-4
  grad_clip: 1.0
  checkpoint_freq: 10

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

YAML configuration for RL training:

```yaml
# Environment
env: Humanoid-v5
normalize_obs: true
normalize_reward: true

# Algorithm
algo: ppo
learning_rate: 3e-4
batch_size: 2048

# Policy
policy_kwargs:
  net_arch: [256, 256]

# Pretraining
pretrained_encoder: models/encoder.pt
adapter_mode: feature
```

## Error Handling

optiq provides specific exception types:

```python
from optiq.exceptions import (
    DataError,          # Invalid data format
    ConfigError,        # Configuration issues
    TrainingError,      # Training failures
    ModelError         # Model-related errors
)
```

**Example:**
```python
try:
    model = optiq.models.build("invalid_arch")
except optiq.exceptions.ConfigError as e:
    print(f"Configuration error: {e}")
```

## Utilities

### Device Management

```python
from optiq.utils import get_device, set_seed

# Automatic device selection
device = get_device()  # 'cuda', 'mps', or 'cpu'

# Reproducible training
set_seed(42)
```

### Logging

```python
import optiq.utils.logging as log

# Configure logging
log.setup_logging(level="INFO", file="training.log")

# Log training progress
logger = log.get_logger(__name__)
logger.info("Starting training...")
```

## Advanced Usage

### Custom Models

Implement custom architectures:

```python
from optiq.models.base import MotionModel

class CustomModel(MotionModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Custom initialization

    def forward(self, x, **kwargs):
        # Custom forward pass
        return output
```

### Custom Datasets

Create custom data loaders:

```python
from optiq.data import MotionDataset

class CustomDataset(MotionDataset):
    def __init__(self, data_path, **kwargs):
        # Custom data loading logic
        super().__init__(sequences, **kwargs)
```

## Performance Tips

### GPU Training
```python
# Enable CUDA optimizations
torch.backends.cudnn.benchmark = True
torch.backends.cuda.matmul.allow_tf32 = True

# Use mixed precision
from torch.cuda.amp import autocast, GradScaler
scaler = GradScaler()
```

### Memory Optimization
```python
# Use gradient checkpointing for large models
model.gradient_checkpointing_enable()

# Data loading optimizations
dataloader = DataLoader(dataset, num_workers=4, pin_memory=True)
```

### Profiling
```python
from torch.profiler import profile, record_function

with profile() as prof:
    with record_function("model_forward"):
        output = model(input)

print(prof.key_averages().table())
```

---

For more examples, see the [examples section](../examples/index.md). For questions, visit our [GitHub Discussions](https://github.com/tedtroxell/optiq/discussions).
