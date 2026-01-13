## Training Configs, Losses, and Schedules

### Config files to add
- `configs/model_transformer.yaml`
- `configs/model_mlp.yaml`
- `configs/model_unet1d.yaml`
- `configs/training_defaults.yaml` (shared training hyperparams)

### Suggested fields per model config
- `arch`: `transformer` | `mlp` | `unet1d`
- `input_dim`: int
- `output_dim`: int
- `conditioning_dim`: int (optional)
- `horizon`: int (sequence length for transformer/unet)
- Optimizer: `optimizer: adamw`, `lr`, `weight_decay`, `betas`
- Scheduler: `scheduler: cosine` or `none`; `warmup_steps`
- Regularization: `dropout`, `grad_clip`
- Loss: `loss: mse` (options: `mse`, `l1`, `smooth_l1`); `vel_weight`, `quat_norm_weight`
- Data: `batch_size`, `num_workers`, `shuffle`, `pin_memory`
- Trainer: `max_epochs`, `precision`, `accumulate_grad_batches`
- Logging: `log_every_n_steps`, `val_every_n_steps`, `checkpoint_every_n_steps`

### Loss composition
- Base next-state loss: `L_base = mse(pred, target)`
- Optional velocity loss (if velocities present): `L_vel = mse(vel_pred, vel_target)`; to compute vel_pred, finite diff on predicted frames.
- Quaternion normalization penalty: encourage unit norm for quaternion parts; `L_quat = mse(||q||, 1)`.
- Total: `L = L_base + λ_vel * L_vel + λ_quat * L_quat`

### Data handling in training loop
- For `NextStepDataset`: inputs `(x, y, cond)` where `x` is frame t, `y` is frame t+1.
- For `AutoregressiveDataset`: inputs `(chunk, target, cond_seq)` where shapes `(B, T, F)`; mask padding if any.
- Collate: allow `cond` to be None; models must handle `condition=None`.

### Model-specific notes
- Transformer:
  - Apply causal mask if `causal=True`.
  - Positional encodings up to `max_seq_len`; truncate or error if exceeded.
  - Conditioning: prepend a condition token or add to every timestep via MLP.
- MLP:
  - If horizon > 1, flatten `(B, T, F)` to `(B, T*F)` or pool; config flag `flatten_sequence: true|false`.
- UNet1D:
  - Input reshape `(B, T, F) -> (B, F, T)`.
  - Optional noise schedule; if used, include timestep conditioning.

### Schedules and optimization
- Default: AdamW lr=3e-4, weight_decay=1e-4.
- Cosine annealing with warmup: `warmup_steps=500`, min_lr=1e-5.
- Gradient clipping: `grad_clip=1.0`.
- Mixed precision: allow `precision=16` when CUDA available.

### Checkpointing and exports
- Save best (val loss) and last checkpoints.
- Export TorchScript encoder for MLP/Transformer when `--export-ts` flag is set; use example input matching `input_dim`.
- Store training config alongside checkpoint (`metadata/config.yaml`).

### Evaluation/validation
- Metrics: MSE, MAE on frames; optional velocity MSE.
- Autoregressive rollout sanity: run short rollout and compute drift (norm difference) vs. ground truth over T steps; log to tensorboard/MLflow.

### CLI mapping (future)
- `optiq train model --config configs/model_transformer.yaml --data data/labeled.parquet --out ckpt.pth --export-ts encoder.ts`

