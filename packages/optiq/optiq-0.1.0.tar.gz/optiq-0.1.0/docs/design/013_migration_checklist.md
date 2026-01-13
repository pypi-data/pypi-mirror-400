## Migration Checklist (Execution Plan)

### Data layer
- [ ] Implement `optiq.data` (FrameSequence, LabeledSequence, parquet/hdf5 IO) — initial code added.
- [ ] Wire node extractor outputs into `FrameSequence` convert path; keep JS untouched.
- [ ] Update examples to use `load_sequence` instead of raw JSON where feasible.
- [ ] Add dataset builders to training flows (next-step, autoregressive, BC).

### Models
- [ ] Add registry (`optiq.models.build/list/load_checkpoint`).
- [ ] Implement Transformer/MLP/UNet1D with standard forward signature.
- [ ] Provide config templates under `configs/`.
- [ ] Add TorchScript export helper for RL bootstrap.

### RL bootstrap (SB3)
- [ ] Create `optiq.rl.bootstrap` helpers per `008_rl_bootstrap_sb3.md`.
- [ ] Refactor `examples/humanoid_imitation/train_mujoco.py` to use helpers.
- [ ] Tests: adapter inference, weight transfer, TorchScript + state_dict load.

### Visualization
- [ ] Move Plotly/MoviePy helpers into `optiq.vis` per `011_viz_standardization.md`.
- [ ] Add CLI hooks `optiq viz plotly` and `optiq viz video`.
- [ ] Sanity tests (HTML exists, tiny video render when moviepy available).

### CLI
- [ ] Replace `src/optiq/cli.py` with grouped commands (`data`, `train`, `viz`) per `012_cli_commands_detailed.md`.
- [ ] Ensure extras guardrails (friendly missing-extra errors).
- [ ] CLI smoke tests.

### Packaging
- [x] Split extras in `pyproject.toml` ([ml], [rl], [viz], [web], [infra], [all]/[dev]).
- [ ] Confirm package discovery and console script entry work (install -e ., run `optiq --help`).
- [ ] Update README with install matrix and extras.

### De-Isaac (completed tasks)
- [x] Delete Isaac utilities and imports.
- [x] Remove Isaac pipeline scripts/configs.
- [x] Prune Isaac from Dockerfile.

### Tests/QA
- [ ] Add minimal unit tests for data loaders, datasets, models registry (CPU).
- [ ] Add CLI smoke tests.
- [ ] Add SB3 bootstrap unit covering adapter inference and state_dict bundle.

### Documentation
- [ ] Update README to reflect Mujoco-only, new CLI, extras.
- [ ] Add usage examples for data convert/label, model train, RL bootstrap, viz. 
