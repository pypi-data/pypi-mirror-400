## SB3 Weight Transfer and Adapter Mapping (Detailed)

### Goals
- Initialize SB3 policies (PPO/SAC) from pretrained sequence models.
- Handle dim mismatches via adapters; log exactly what is transferred vs. randomized.
- Support TorchScript encoder or state_dict-based pretrained checkpoints.

### Inputs
- `pretrained_path`: TorchScript `.ts` or torch `state_dict` `.pth` containing model weights and metadata (`input_dim`, `output_dim`, `conditioning_dim`, `arch`, `cfg`).
- `adapter_mode`: `obs` | `feature` | `none`.
- `env_obs_dim`: observation dimension from env (e.g., Humanoid obs).
- Optional `torchscript_in_dim`: if TorchScript expects a different input dim than env obs.

### Flow
1) Load pretrained:
   - If TorchScript: wrap with `TorchScriptFeatureExtractor(script_path, device)`.
   - If state_dict + arch: build model via registry, load state_dict.
2) Infer source dim:
   - Run dummy input through pretrained; flatten to `(B, F_src)`.
3) Infer target dim:
   - For `obs` mode: target is env obs dim.
   - For `feature` mode: target is SB3 policy first Linear in features extractor; use `infer_linear_adapter_from_models` if needed.
4) Build adapters:
   - If `F_src != F_tgt`: create `LinearAdapter(F_src, F_tgt, hidden_dims=adapter_hidden)`; attach as:
     - `obs` mode: `AdapterObsWrapper` that maps env obs → adapter → policy.
     - `feature` mode: adapter after pretrained encoder inside SB3 `BaseFeaturesExtractor`.
5) Weight copy:
   - If pretrained is an MLP and policy net shares layer sizes, copy matching layers (by index/shape).
   - Otherwise, only adapter + pretrained encoder are used; policy remains randomly initialized.
   - Log: which layers copied, which randomized, adapter dims.
6) Checkpointing:
   - SB3 `model.save(zip_path)` as primary.
   - Bundle fallback: `{"policy_state_dict": model.policy.state_dict(), "adapter_state_dict": adapter.state_dict(), "pre_ts_adapter_state_dict": pre_ts_adapter.state_dict(), "torchscript_path": path, "adapter_mode": adapter_mode, "obs_dim": env_obs_dim}`.

### Edge cases
- TorchScript save failures: fallback to state_dict bundle (already in trainer).
- Action space scale: use env `action_space.high` to normalize deltas in BC datasets.
- Sequence models with `(B, T, F)`: require flatten or take last timestep for feature extraction; document choice (default: last timestep or pooled mean; expose `--feature-pool last|mean`).

### Logging/metrics
- Emit adapter source/target dims.
- Emit layer copy report (list of `(layer_name, copied: bool)`).
- If shapes mismatch, warn but continue with adapter-only path.

### Tests
- Dummy pretrained MLP (input=obs dim) → PPO policy: verify first linear weights copied exactly.
- Pretrained output dim != obs dim: ensure adapter built with correct shapes and policy trains.
- TorchScript vs. state_dict loading parity: same outputs for identical inputs.
