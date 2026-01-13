## Packaging Extras and Dependency Split

**Status: ✅ Implemented**

### Overview

optiq now uses optional dependency groups ("extras") to keep the base install lightweight while allowing users to install only the features they need.

### Core Dependencies (Always Installed)

```toml
dependencies = [
  "pydantic", "numpy", "scipy", "trimesh>=4.10.0", "pyyaml",
  "click", "torch>=2.8.0", "mesh-to-sdf>=0.0.15", "pybullet>=3.2.7",
  "torchvista>=0.2.6",
]
```

### Extras Layout

| Extra   | Key Dependencies                                      | Purpose                           |
|---------|-------------------------------------------------------|-----------------------------------|
| `[ml]`  | pytorch-lightning, torchmetrics, mlflow, h5py, pyarrow, scikit-image | Model training & experiment tracking |
| `[rl]`  | stable-baselines3, gymnasium[mujoco], mujoco          | RL policy training & simulation   |
| `[viz]` | plotly, moviepy, matplotlib, opencv-python-headless   | Visualization & video rendering   |
| `[web]` | fastapi, uvicorn, django, sqlmodel, jinja2, etc.      | Web apps & REST APIs              |
| `[infra]` | prometheus-client, kombu, redis, psycopg2-binary    | Monitoring & task queues          |
| `[all]` | All extras (via references)                           | Full installation                 |
| `[dev]` | All + pytest, pytest-cov                              | Development & testing             |

### Implementation Details

1. **Aggregate extras use references** (no duplication):
   ```toml
   all = ["optiq[ml]", "optiq[rl]", "optiq[viz]", "optiq[web]", "optiq[infra]"]
   dev = ["optiq[all]", "pytest>=8.4.2", "pytest-cov>=4.0.0"]
   ```

2. **Console script entry point**:
   ```toml
   [project.scripts]
   optiq = "optiq.cli:main"
   ```

3. **Package discovery** via setuptools find:
   ```toml
   [tool.setuptools.packages.find]
   where = ["src"]
   ```

### Installation Examples

```bash
# Minimal (core only)
pip install optiq

# RL and visualization
pip install "optiq[rl,viz]"

# Web deployment with monitoring
pip install "optiq[web,infra]"

# Development (everything + test tools)
pip install -e ".[dev]"
```

### CLI Friendly Errors

When a command requires an extra that isn't installed, the CLI provides actionable error messages:

```bash
$ optiq viz plotly --pred test.json --out viz.html
Error: Visualization requires optiq[viz]: No module named 'plotly'

$ optiq train rl --env Humanoid-v5 --out policy.zip
Error: RL training requires optiq[rl]: No module named 'stable_baselines3'
```

### Tests

Tests verify:
1. **Extras are defined correctly** in `pyproject.toml` (`test_packaging.py`)
2. **Import smoke tests** per extra, skipped if deps not installed
3. **CLI error messages** are helpful when extras are missing
4. **Core imports** always work regardless of which extras are installed

See `tests/unit/test_packaging.py` for comprehensive packaging tests. 
