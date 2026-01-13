# Contributing to optiq

We welcome contributions from the community! This guide explains how to get started with contributing to optiq.

## Ways to Contribute

### 🐛 Report Bugs
Found a bug? [Open an issue](https://github.com/tedtroxell/optiq/issues) with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)

### 💡 Suggest Features
Have an idea? [Start a discussion](https://github.com/tedtroxell/optiq/discussions) or [open a feature request](https://github.com/tedtroxell/optiq/issues).

### 🛠️ Code Contributions
Want to contribute code? See the development setup below.

## Development Setup

### Prerequisites

- Python 3.9+
- Git
- (Optional) CUDA for GPU acceleration

### Clone and Install

```bash
# Clone the repository
git clone https://github.com/tedtroxell/optiq.git
cd optiq

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .[dev]
```

### Verify Installation

```bash
# Run tests
pytest tests/

# Check code style
flake8 src/optiq
black --check src/optiq
isort --check-only src/optiq

# Build docs locally
mkdocs serve
```

## Development Workflow

### 1. Choose an Issue

- Check [open issues](https://github.com/tedtroxell/optiq/issues) for tasks
- Look for issues labeled `good first issue` or `help wanted`
- Comment on the issue to indicate you're working on it

### 2. Create a Branch

```bash
# Create and switch to a feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

### 3. Make Changes

- Write clear, focused commits
- Add tests for new functionality
- Update documentation as needed
- Follow the coding standards

### 4. Test Your Changes

```bash
# Run the full test suite
pytest tests/ -v

# Run specific tests
pytest tests/unit/test_models.py -v

# Check code coverage
pytest tests/ --cov=optiq --cov-report=html
open htmlcov/index.html  # View coverage report
```

### 5. Update Documentation

```bash
# Build docs locally
mkdocs build

# Serve docs for preview
mkdocs serve
```

### 6. Commit and Push

```bash
# Stage your changes
git add .

# Commit with clear message
git commit -m "feat: add new motion prediction model

- Add transformer-based architecture
- Support for causal masking
- Comprehensive tests included"

# Push to your branch
git push origin feature/your-feature-name
```

### 7. Create Pull Request

- Go to [GitHub](https://github.com/tedtroxell/optiq/pulls)
- Click "New pull request"
- Select your branch as "compare"
- Fill out the pull request template
- Link to any related issues

## Coding Standards

### Python Style

We follow [PEP 8](https://pep8.org/) with some modifications:

```python
# ✅ Good
def process_motion_data(data: np.ndarray, fps: float = 30.0) -> dict:
    """Process motion capture data.

    Args:
        data: Motion data as numpy array
        fps: Frames per second

    Returns:
        Processed motion data dictionary
    """
    if data is None:
        raise ValueError("Motion data cannot be None")

    processed = {
        "frames": len(data),
        "joints": data.shape[1] // 3,  # 3 values per joint (x,y,z)
        "duration": len(data) / fps,
    }

    return processed

# ❌ Avoid
def process_motion_data(data,fps=30.0):
    if not data:
        raise ValueError("bad data")
    return {"frames":len(data),"joints":data.shape[1]/3,"dur":len(data)/fps}
```

### Code Formatting

We use automated formatters:

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Check formatting
black --check src/ tests/
isort --check-only src/ tests/
```

### Type Hints

Use type hints for function parameters and return values:

```python
from typing import Optional, List, Dict, Any
import numpy as np

def load_sequence(path: str, compute_velocities: bool = False) -> 'MotionSequence':
    """Load motion sequence from file.

    Args:
        path: Path to motion data file
        compute_velocities: Whether to compute velocity features

    Returns:
        Motion sequence object
    """
    pass
```

## Testing

### Writing Tests

- Put tests in `tests/` directory
- Mirror source structure: `tests/unit/test_models.py` for `src/optiq/models.py`
- Use descriptive test names

```python
import pytest
from optiq.models import build_mlp

class TestMLP:
    def test_basic_initialization(self):
        """Test MLP can be created with basic parameters."""
        model = build_mlp(input_dim=10, hidden_dims=[32, 16], output_dim=5)

        assert model.input_dim == 10
        assert model.output_dim == 5
        assert len(model.layers) == 3  # input + 2 hidden + output

    def test_forward_pass(self):
        """Test MLP forward pass produces correct output shape."""
        model = build_mlp(input_dim=10, hidden_dims=[32], output_dim=5)
        input_tensor = torch.randn(4, 10)  # batch_size=4

        output = model(input_tensor)

        assert output.shape == (4, 5)

    @pytest.mark.parametrize("input_dim,output_dim", [
        (10, 5),
        (20, 10),
        (100, 50),
    ])
    def test_different_dimensions(self, input_dim, output_dim):
        """Test MLP works with different input/output dimensions."""
        model = build_mlp(input_dim=input_dim, hidden_dims=[32], output_dim=output_dim)
        batch_size = 2
        input_tensor = torch.randn(batch_size, input_dim)

        output = model(input_tensor)

        assert output.shape == (batch_size, output_dim)
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_models.py

# Run specific test
pytest tests/unit/test_models.py::TestMLP::test_basic_initialization

# Run with coverage
pytest --cov=optiq --cov-report=html

# Run slow tests only
pytest -m slow
```

## Documentation

### Building Docs

```bash
# Install docs dependencies
pip install -r docs/requirements.txt

# Build docs
mkdocs build

# Serve docs locally
mkdocs serve
```

### Writing Documentation

- Use Markdown for documentation
- Follow the existing structure
- Include code examples
- Keep API documentation up to date

## Pull Request Process

### Before Submitting

- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

### During Review

- Address reviewer feedback
- Keep conversations focused
- Make incremental changes if requested

### After Merge

- Delete your feature branch
- Pull latest changes to your local main branch

## Recognition

Contributors are recognized in:
- GitHub repository contributors
- Changelog for significant contributions
- Documentation acknowledgments

## Questions?

- 📖 [Documentation](https://optiq.readthedocs.io)
- 💬 [GitHub Discussions](https://github.com/tedtroxell/optiq/discussions)
- 🐛 [Issue Tracker](https://github.com/tedtroxell/optiq/issues)

Thank you for contributing to optiq! 🎉
