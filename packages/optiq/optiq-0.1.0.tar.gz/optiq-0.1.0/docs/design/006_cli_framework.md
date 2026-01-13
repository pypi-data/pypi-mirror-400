## CLI and Module Surface for the Framework

**Status: IMPLEMENTED** (see `src/optiq/cli.py`)

### CLI Command Structure

```
optiq [--seed INT] [--device cpu|cuda|mps|auto] COMMAND

Commands:
  data   - Data conversion and labeling utilities
  train  - Training commands for models and RL policies
  viz    - Visualization helpers (Plotly, video)
```

### Implemented Commands

#### Data Commands
- `optiq data convert --in foo.json --out data/seq.parquet --format parquet --compute-velocities`
- `optiq data label --in data/seq.parquet --out labeled.parquet --label movement=kick --label phase=windup`

#### Train Commands
- `optiq train model --config configs/model.yaml --arch transformer --out ckpt.pt [--epochs N] [--override key=value]`
- `optiq train rl --env Humanoid-v5 --algo ppo --total-steps 3e5 --out policy.zip [--pretrained encoder.pt] [--record-video]`
- `optiq train legacy --config config.yaml --output results.json` (inverse dynamics / physics pipeline)

#### Visualization Commands
- `optiq viz plotly --pred pred.json --out viz.html [--gt gt.json] [--dataset seq.parquet] [--tubes]`
- `optiq viz video --policy sb3.zip --env Humanoid-v5 --out video.mp4 [--steps 1000] [--fps 30]`

### Module layout backing the CLI
- `optiq.data`: FBX ingestion, FrameSequence, dataset writers/readers (HDF5/Parquet), labeling utilities.
- `optiq.models`: registry + architectures (transformer/mlp/unet1d), config loaders.
- `optiq.rl`: SB3 bootstrap helpers, adapters, behavior cloning dataset builders.
- `optiq.vis`: plotly/moviepy utilities packaged as functions callable from CLI.
- `optiq.cli`: Click front-end delegating to the above modules; exposed via `console_scripts` entry `optiq`.

### Behavior (implemented)
- Global `--seed` and `--device` options for reproducibility and device selection.
- All training commands accept `--config` (YAML/JSON) and `--override key=value` for runtime overrides.
- Graceful error messages when optional extras are missing (e.g., `optiq[rl]` not installed).
- Node.js scripts (`scripts/extract_fbx_anim.js`, Mixamo downloader) remain untouched.

### Implementation notes
- Entry point: `optiq.cli:main` in `pyproject.toml`
- Smoke tests: `tests/unit/test_cli.py` (25 tests covering argument parsing and dispatch)
- The `train model` command builds models via the registry but delegates actual training loops to user configs/scripts.
- The `train rl` command integrates with `optiq.rl.bootstrap` for pretrained encoder adaptation.
