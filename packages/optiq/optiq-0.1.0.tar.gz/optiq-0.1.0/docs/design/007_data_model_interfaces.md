## Data & Model Interfaces (APIs and Shapes)

**Status: IMPLEMENTED** (see `src/optiq/data/` and `src/optiq/models/`)

### Data Abstractions (Implemented)

#### FrameSequence (`optiq.data.FrameSequence`)
In-memory representation of motion frames with:
- `fps: int` - Frame rate
- `bone_names: List[str]` - List of bone/joint names
- `frames: np.ndarray (T, F)` - Frame data (T timesteps, F features)
- `velocities: Optional[np.ndarray]` - Per-frame velocities
- `labels: Optional[np.ndarray]` - Per-frame labels
- `label_names: Optional[List[str]]` - Label column names
- `seq_labels: Optional[Dict]` - Sequence-level labels
- `metadata: Dict` - Arbitrary metadata
- `splits: Optional[Dict[str, np.ndarray]]` - Train/val/test split masks
- `raw_bones: Optional[Dict]` - Original bone structure

#### Persistence
- `FrameSequence.to_parquet(out_path, compression="snappy")` - Write to Parquet
- `FrameSequence.to_hdf5(out_path, compression="gzip")` - Write to HDF5

#### Loader
- `optiq.data.load_sequence(path) -> FrameSequence` - Load from Parquet/HDF5/JSON

#### Labeling
- `FrameSequence.attach_labels(frame_labels, label_names, seq_labels)` - Attach labels in-place
- `FrameSequence.with_labels(frame_labels, seq_labels, conditions) -> LabeledSequence` - Create labeled sequence

### Dataset Builders (Implemented)

```python
from optiq.data import build_imitation_dataset, build_bc_dataset
from optiq.data.datasets import NextStepDataset, AutoregressiveDataset, BehaviorCloneDataset

# Next-step prediction: (prev_state, next_state, condition_vec)
ds = build_imitation_dataset(path, mode="next", horizon=1)

# Autoregressive chunks: (chunk, target_chunk, condition_vec)
ds = build_imitation_dataset(path, mode="autoregressive", chunk_len=32, stride=1)

# Behavior cloning: (obs, action) for RL environments
ds = build_bc_dataset(path, env_id="Humanoid-v5", retarget_fn=..., action_fn=...)
```

### Model Forward Signature (Implemented)

All models follow standardized signature:
```python
forward(prev_state, condition=None, context=None) -> next_state
```

Shapes:
- `prev_state`: `(B, F)` for single-step; `(B, T, F)` for sequence models
- `condition`: `(B, C)` optional conditioning vector
- `context`: Reserved for diffusion timesteps or additional context
- `next_state`: Same shape as `prev_state` (single-step output `(B, F)`)

### Model Architectures (Implemented)

#### TransformerModel (`optiq.models.TransformerModel`)
```python
model = build("transformer",
    input_dim=14,
    model_dim=256,
    num_layers=4,
    num_heads=4,
    dropout=0.1,
    output_dim=14,
    conditioning_dim=5,    # Optional conditioning input dimension
    ff_mult=4,             # Feedforward multiplier
    max_seq_len=5000,      # Maximum sequence length for positional encoding
    causal=True,           # Enable causal (autoregressive) mask
    horizon=1,             # Prediction horizon
)
```

#### MLPModel (`optiq.models.MLPModel`)
```python
model = build("mlp",
    input_dim=14,
    hidden_dims=[256, 128, 64],  # Or use hidden_dim + num_layers
    output_dim=14,
    dropout=0.1,
    conditioning_dim=5,    # Optional conditioning input dimension
    horizon=3,             # Number of input timesteps to flatten
)
```

#### UNet1D (`optiq.models.UNet1D`)
```python
model = build("unet1d",
    input_dim=14,
    base_channels=64,
    dropout=0.1,
    output_dim=14,
    conditioning_dim=5,    # Optional conditioning input dimension
    num_res_blocks=2,      # Residual blocks per level
    attention_layers=[0, 1],  # Levels with self-attention
    noise_schedule="linear",  # Enable diffusion noise conditioning
    time_emb_dim=128,      # Timestep embedding dimension
    num_levels=2,          # Number of UNet encoder/decoder levels
)
```

### Model Registry

```python
from optiq.models import build, available, register

# Available models
available()  # {'mlp': MLPModel, 'transformer': TransformerModel, 'unet1d': UNet1D}

# Build model from config
model = build("transformer", input_dim=14, model_dim=128, num_layers=2, num_heads=4)

# Register custom model
register("custom", MyCustomModel)
```

### Configuration Knobs Summary

| Parameter | MLP | Transformer | UNet1D |
|-----------|-----|-------------|--------|
| `input_dim` | ✓ | ✓ | ✓ |
| `output_dim` | ✓ | ✓ | ✓ |
| `hidden_dim(s)` | ✓ | - | - |
| `model_dim` | - | ✓ | - |
| `base_channels` | - | - | ✓ |
| `num_layers` | ✓ | ✓ | - |
| `num_levels` | - | - | ✓ |
| `num_heads` | - | ✓ | - |
| `dropout` | ✓ | ✓ | ✓ |
| `conditioning_dim` | ✓ | ✓ | ✓ |
| `horizon` | ✓ | ✓ | - |
| `causal` | - | ✓ | - |
| `ff_mult` | - | ✓ | - |
| `max_seq_len` | - | ✓ | - |
| `num_res_blocks` | - | - | ✓ |
| `attention_layers` | - | - | ✓ |
| `noise_schedule` | - | - | ✓ |

### Tests

Comprehensive tests in `tests/unit/test_data_model_interfaces.py`:
- FrameSequence field validation
- Parquet/HDF5/JSON roundtrips
- Label attachment and splitting
- Dataset builders (NextStep, Autoregressive)
- Model forward signature compliance
- Conditioning support
- Shape compatibility (various batch sizes, sequence lengths)
- Gradient flow verification

### Migration Notes
- Legacy `FBXDataSet` and `HumanoidPoseActionDataset` in `optiq.rl.fbx_dataset` remain for backwards compatibility
- New code should use `build_imitation_dataset()` and `build_bc_dataset()` from `optiq.data`
- All models in registry follow the standardized forward signature
