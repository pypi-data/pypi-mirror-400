## CLI Command Surface (Detailed)

### Command groups
- `optiq data`
  - `convert`: `optiq data convert --in foo.fbx --out data/seq.parquet --format parquet --fps 30 --label movement=kick`
    - Uses node extractor (unchanged) to JSON, then `FrameSequence.to_parquet/hdf5`.
  - `label`: `optiq data label --in data/seq.parquet --out data/labeled.parquet --label phase=windup --label subject=human`
    - Adds per-sequence labels; optional per-frame labels via `--frame-labels path.json`.
  - `split`: `optiq data split --in data/labeled.parquet --train 0.8 --val 0.1 --test 0.1 --seed 7`
    - Writes metadata splits.
- `optiq train`
  - `model`: `optiq train model --arch transformer --config configs/model_transformer.yaml --data data/labeled.parquet --out ckpt.pth`
    - Builds datasets (`NextStepDataset`/`AutoregressiveDataset`) per config; logs metrics.
  - `rl`: `optiq train rl --env Humanoid-v5 --pretrained ckpt.pth --algo ppo --total-steps 300000 --record-video`
    - Uses SB3 bootstrap helpers; adapter-mode options `obs|feature|none`; supports TorchScript encoder path.
- `optiq viz`
  - `plotly`: `optiq viz plotly --dataset data/labeled.parquet --out viz.html --gt data/gt.parquet --tubes`
  - `video`: `optiq viz video --policy sb3.zip --env Humanoid-v5 --out video.mp4 --adapter-mode obs --adapter-path adapter.pth`

### Common flags
- `--device cpu|cuda`, `--seed`, `--num-workers` for dataloaders, `--batch-size`.
- Config override via `--config` plus `--override key=value` (YAML/JSON dot notation).
- Friendly errors when extras missing (e.g., `optiq[rl]` not installed → message).

### Implementation mapping
- `optiq.cli` should expose `cli = typer.Typer()` (or click group) with subcommands wiring to:
  - `optiq.data.*` for convert/label/split.
  - `optiq.models` + `optiq.data.datasets` for model training.
  - `optiq.rl.bootstrap` + `optiq.rl.sb3` for RL.
  - `optiq.vis.*` for visualization.
- Console script entry in `pyproject.toml` points to `optiq.cli:cli`.

### Exit codes
- `0` success, `2` usage error (argparse/typer default), `10` missing-extra/dependency, `20` data/IO error, `30` training failure.

### Logging
- Default to stdout progress; optional `--mlflow-uri` and `--experiment-name` for runs if `mlflow` present.
- `--log-json` flag for structured logs (one JSON per line).

### Tests
- CLI smoke tests (pytest) using `CliRunner`/`typer.testing`: ensure commands parse, fail gracefully without extras, and create expected output files for tiny dummy data.
