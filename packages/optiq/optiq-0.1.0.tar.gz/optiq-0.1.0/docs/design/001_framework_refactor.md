## Framework Refactor Overview (optiq → imitation-first)

### Goals
- Transform `optiq` into an imitation-learning framework that ingests one or more FBX files, produces labeled datasets (HDF5/Parquet), trains sequence models (Transformer/MLP/UNet) to predict next state conditioned on user-defined labels, and bootstraps RL policies (stable-baselines3) from pretrained weights.
- Standardize on Mujoco + stable-baselines3; remove all Isaac/Isaac-Lab code and references.
- Preserve and standardize visualization (Plotly/MoviePy) and infra scaffolding; make verticals installable via extras: `[ml]`, `[rl]`, `[web]`, `[infra]`, `[viz]`.
- Maintain the scripts folder for one-off utilities (e.g., dataset downloads); do **not** modify the FBX node extractor or Mixamo downloader scripts.

### Non-goals
- Backward compatibility with legacy script CLIs is not required (breaking changes acceptable).
- No Isaac/Isaac-Lab support going forward; delete or isolate those modules.

### Status of Isaac references
- Isaac Gym/Isaac-Lab imports have been removed from the humanoid runner; `examples/humanoid_imitation/run.py` now targets the Mujoco PPO flow in `train_mujoco.py`.
- Legacy `optiq.rl.isaac_utils` no longer exists; all RL helpers are Mujoco/stable-baselines3 only.
- Any future RL adapters should assume Gymnasium Mujoco spaces and SB3 policies (no Isaac config generation).

### Migration plan (high level)
1) Data layer: Replace JSON-only assumptions with HDF5/Parquet datasets that store frames, metadata (fps, bones, objects), and user-defined condition labels; keep JSON import for compatibility during transition.
2) Models: Provide registry-based architectures (Transformer, MLP, UNet) plus adapters for feature/observation remapping; expose configs in `optiq` package.
3) RL: Build SB3 policy bootstrapping that initializes weights from pretrained sequence models (load from disk); keep adapter flow for observation/features.
4) Visualization: Standardize Plotly/MoviePy pipelines into reusable functions/classes under `optiq.vis`.
5) Packaging: Single `optiq` package with extras `[ml]`, `[rl]`, `[web]`, `[infra]`, `[viz]`; prune Isaac deps; keep scripts folder for non-framework utilities.

### Constraints
- Do not edit `scripts/extract_fbx_anim.js`, Mixamo downloader, or other node extractors.
- Use HDF5 or Parquet for new dataset outputs (compression-friendly).
- Keep functionality (even if APIs change) for data processing, training, visualization, infra.

### Open items / questions to resolve in subsequent docs
- Exact dataset schema (per-frame tables vs. sequence group) and metadata layout in HDF5/Parquet.
- API surface for labeling conditions (CLI vs. Python API).
- Default checkpoint formats for pretrained → RL bootstrapping (Torch `state_dict` vs. TorchScript). 
