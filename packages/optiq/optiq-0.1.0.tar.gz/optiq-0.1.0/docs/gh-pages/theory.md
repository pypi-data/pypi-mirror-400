# Theory Notes

## Data representation
- Frames stored as `(T, F)` where `F = bones * (3 pos + 4 quat [+ optional vel])`.
- Metadata captures fps, bone order, coordinate space, and label namespaces.
- Parquet/HDF5 chosen for columnar compression and schema metadata; JSON kept for backward compatibility.

## Conditioning and labels
- Frame-level labels `(T, L)` attach as dense arrays; sequence labels stored in metadata.
- Models accept `(prev_state, condition)`; conditions concatenate across feature dim for MLP/Transformer/UNet1D.

## Model suite
- `mlp`: baselines for small datasets or single-step prediction.
- `transformer`: encoder-style with positional encoding; outputs next-state head from last token.
- `unet1d`: temporal conv with skip connections for smooth trajectories and diffusion-style training.

## Adapters and RL bootstrapping
- TorchScript encoder → SB3 via two modes:
  - `obs`: wrap env obs with TorchScript + adapters to match observation dim.
  - `feature`: use TorchScript as SB3 features_extractor.
- Auto-build adapters when TorchScript input/output dims differ from env obs dim.

## Visualization
- Plotly 3D skeletons with optional tube rendering; supports edge lists for different rigs.
- Video rendering uses env `render_mode="rgb_array"` and MoviePy; optional metrics overlay via MLflow/Grafana (infra extras).
