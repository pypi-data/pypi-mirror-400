# optiq Documentation

Welcome to the optiq docs. Here you'll find tutorials, theory notes, and runnable examples for the imitation-first motion learning framework.

- [Tutorials](tutorials.md) – start-to-finish guides (data → model → RL/viz).
- [Theory](theory.md) – background on motion representations, conditioning, and adapters.
- [Examples](examples.md) – runnable scripts and CLI recipes.

## Quick start

```bash
uv venv .venv
source .venv/bin/activate
uv pip install -e .[dev]

# Convert FBX JSON to Parquet and train + visualize
uv run python -m optiq.cli data convert --in ground_truth.json --out seq.parquet --compute-velocities
uv run python examples/humanoid_imitation/run.py --fbx Walking.fbx --ppo-bootstrap
uv run python -m optiq.cli viz plotly --pred examples/humanoid_imitation/data/ground_truth.json --out /tmp/anim.html
```
