## Packaging, Visualization, and Infrastructure

### Packaging / extras
- Single package `optiq` with extras:
  - `[ml]`: training, models (Transformer/MLP/UNet), data loaders, PyTorch deps.
  - `[rl]`: stable-baselines3, Mujoco gymnasium extras, adapter wrappers.
  - `[viz]`: Plotly/MoviePy visualization utilities.
  - `[web]`: Django web UI components (existing `web/`).
  - `[infra]`: monitoring/MLflow/Grafana/Prometheus hooks.
- Remove Isaac/Isaac-Lab dependencies; drop `optiq.rl.isaac_utils` and any imports.
- Keep `scripts/` for non-framework utilities (downloads, conversions), but **do not touch** FBX node extractor or Mixamo downloader.

### Visualization (keep, standardize)
- Plotly skeletal animation helper (to be wrapped as reusable API):  
```
1:158:src/optiq/vis/plotly_anim_runner.py
BONE_EDGES = [...]
def load_anim(path: str):
    ...
def frame_traces(...):
    ...
```
- MoviePy post-train video flow in Mujoco trainer (should remain, but callable as library utility):  
```
400:458:examples/humanoid_imitation/train_mujoco.py
if args.post_train_video:
    try:
        import moviepy
    except Exception:
        print("MoviePy not installed; skipping post-training video.")
    else:
        ...
        class AdapterObsWrapper(gym.ObservationWrapper):
            ...
```
- Actions:
  - Move reusable Plotly/MoviePy routines into `optiq.vis` with clear function signatures.
  - Provide CLI hooks: `optiq viz plotly --dataset ...`, `optiq viz video --policy ...`.

### Infrastructure
- Preserve MLflow hooks in Mujoco trainer; make them optional via extras `[infra]`.
- Keep Grafana/Prometheus configs, but ensure service references no longer depend on Isaac.
- Provide logging/metrics interfaces under `optiq.infra` for reuse across training pipelines.

### Removal/cleanup
- Delete Isaac-specific modules and imports; ensure Mujoco-only codepaths remain.
- Update README/usage to point to new extras and commands.

### Deliverables for refactor
- `setup.cfg/pyproject.toml` updated with extras.
- `optiq.cli` exposes commands for data convert/label, model train, RL bootstrap, visualization.
- Tests for viz helpers (sanity shape checks) and packaging metadata. 
