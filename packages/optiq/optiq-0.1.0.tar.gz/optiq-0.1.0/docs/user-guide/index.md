# User Guide

Welcome to the optiq user guide! This comprehensive guide covers everything you need to know to effectively use optiq for motion learning tasks.

## Getting Started

- **[Installation](installation.md)**: How to install optiq and its dependencies
- **[Quick Start](quickstart.md)**: Your first steps with optiq
- **[CLI Reference](cli.md)**: Complete command-line interface guide

## Core Concepts

### Data Pipeline
- **[Data Formats](data-formats.md)**: Understanding optiq's data structures
- **[FBX Processing](fbx-processing.md)**: Converting FBX files to datasets
- **[Dataset Creation](dataset-creation.md)**: Building training datasets

### Model Training
- **[Model Architectures](model-architectures.md)**: Available model types
- **[Training Configuration](training-config.md)**: Configuring training runs
- **[Experiment Tracking](experiment-tracking.md)**: Monitoring and logging

### Reinforcement Learning
- **[Policy Bootstrapping](policy-bootstrapping.md)**: Using pretrained models in RL
- **[Stable-Baselines3 Integration](sb3-integration.md)**: RL training workflows
- **[Environment Setup](environment-setup.md)**: Configuring RL environments

## Advanced Topics

### Customization
- **[Custom Models](custom-models.md)**: Implementing new architectures
- **[Data Loaders](custom-dataloaders.md)**: Creating custom data pipelines
- **[Callbacks](callbacks.md)**: Extending training with custom logic

### Performance & Scaling
- **[GPU Training](gpu-training.md)**: Optimizing for GPU acceleration
- **[Distributed Training](distributed-training.md)**: Multi-GPU and cluster training
- **[Memory Optimization](memory-optimization.md)**: Handling large datasets

### Deployment
- **[Model Export](model-export.md)**: Exporting models for inference
- **[TorchScript](torchscript.md)**: Converting to TorchScript for deployment
- **[ONNX Export](onnx-export.md)**: Cross-platform model deployment

## API Reference

- **[Python API](api.md)**: Complete Python API documentation
- **[Configuration Files](config-files.md)**: YAML configuration reference
- **[Error Handling](error-handling.md)**: Troubleshooting common issues

## Best Practices

- **[Code Style](code-style.md)**: Writing maintainable optiq code
- **[Testing](testing.md)**: Writing and running tests
- **[Performance](performance.md)**: Optimizing for speed and memory

---

!!! note "API Documentation"
    For detailed API documentation, see the [API Reference](api.md) or use `help()` on any optiq object in Python.

!!! tip "Examples"
    Looking for hands-on examples? Check out the [examples](../examples/index.md) section.

!!! question "Need Help?"
    - 📖 [Read the Docs](https://optiq.readthedocs.io)
    - 💬 [GitHub Discussions](https://github.com/tedtroxell/optiq/discussions)
    - 🐛 [Issue Tracker](https://github.com/tedtroxell/optiq/issues)
