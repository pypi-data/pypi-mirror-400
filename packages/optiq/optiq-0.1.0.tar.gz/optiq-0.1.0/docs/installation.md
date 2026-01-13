# Installation

This guide covers installing optiq and its optional dependencies.

## Requirements

- **Python**: 3.9 or later
- **Operating System**: Linux, macOS, or Windows

## Quick Install

### Core Installation

Install the minimal optiq package:

```bash
pip install optiq
```

This includes core dependencies for data processing and basic model training.

### Development Installation

For development and testing:

```bash
git clone https://github.com/tedtroxell/optiq.git
cd optiq
pip install -e .[dev]
```

## Optional Dependencies

optiq uses optional dependency groups to keep installations lightweight. Install only what you need:

### Machine Learning Training

```bash
pip install optiq[ml]
```

Includes:
- PyTorch Lightning for experiment management
- MLflow for experiment tracking
- TorchMetrics for evaluation
- H5Py and PyArrow for data handling
- Scikit-image for preprocessing

### Reinforcement Learning

```bash
pip install optiq[rl]
```

Includes:
- Stable-Baselines3 for RL algorithms
- Gymnasium with Mujoco support
- Mujoco physics engine

### Visualization

```bash
pip install optiq[viz]
```

Includes:
- Plotly for interactive visualization
- MoviePy for video generation
- Matplotlib for plotting
- OpenCV for image processing

### Web Interface

```bash
pip install optiq[web]
```

Includes:
- FastAPI for web APIs
- Django for web interface
- Uvicorn for serving
- SQLModel for database operations

### Monitoring & Infrastructure

```bash
pip install optiq[infra]
```

Includes:
- Prometheus for metrics
- Redis for caching
- Kombu for task queues
- PostgreSQL client

### Everything

```bash
pip install optiq[all]
```

Installs all optional dependencies.

## Installation Examples

### Data Science Environment

```bash
pip install optiq[ml,viz]
```

For training models and creating visualizations.

### RL Research Environment

```bash
pip install optiq[rl,viz,ml]
```

For end-to-end RL research with pretrained models.

### Web Deployment

```bash
pip install optiq[web,infra]
```

For deploying optiq as a web service.

## Verifying Installation

After installation, verify optiq is working:

```bash
# Check version
optiq --version

# View help
optiq --help

# List available commands
optiq
```

## Troubleshooting

### Common Issues

#### Import Errors

If you get import errors, ensure you're using the right Python version:

```bash
python --version  # Should be 3.9+
which python      # Check which Python is being used
```

#### Permission Errors

If you get permission errors during installation:

```bash
# Use user installation
pip install --user optiq

# Or use a virtual environment
python -m venv optiq-env
source optiq-env/bin/activate  # On Windows: optiq-env\Scripts\activate
pip install optiq
```

#### CUDA Issues

If you have CUDA-related issues with PyTorch:

```bash
# Install CPU-only version
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

#### Mujoco Issues

For RL installation issues:

```bash
# Install system dependencies (Linux)
sudo apt-get install libosmesa6-dev libgl1-mesa-glx libglfw3

# Or for macOS
brew install glfw
```

## Development Setup

For contributing to optiq:

```bash
# Clone repository
git clone https://github.com/tedtroxell/optiq.git
cd optiq

# Install in development mode with all dependencies
pip install -e .[dev]

# Run tests
pytest tests/

# Run linting
flake8 src/optiq
black --check src/optiq
```

## Next Steps

Once installed, check out the [quick start guide](quickstart.md) to learn the basics, or dive into specific topics:

- [Data Pipeline](user-guide/data-pipeline.md)
- [Model Training](user-guide/model-training.md)
- [Reinforcement Learning](user-guide/reinforcement-learning.md)
- [Visualization](user-guide/visualization.md)
