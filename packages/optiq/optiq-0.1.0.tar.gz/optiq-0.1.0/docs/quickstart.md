# Quick Start

Get up and running with optiq in minutes. This guide covers the basic workflow from data to trained model.

## Prerequisites

Make sure you have optiq installed:

```bash
pip install optiq[ml,viz]  # For training and visualization
# or
pip install optiq[all]     # For everything
```

## 1. Prepare Your Data

optiq works with motion capture data. You can either:

### Option A: Use Sample Data

Download sample walking motion data:

```bash
# Download sample FBX file
curl -O https://example.com/sample-walking.fbx  # Replace with actual URL
```

### Option B: Use Your Own Data

Convert your FBX animation files to optiq format:

```bash
# Convert FBX to Parquet dataset
optiq data convert --in your-animation.fbx --out dataset.parquet --compute-velocities
```

## 2. Explore Your Data

Load and inspect your motion data:

```python
from optiq import load_sequence

# Load the dataset
seq = load_sequence("dataset.parquet")

# View basic info
print(f"Sequence length: {len(seq)}")
print(f"Joint count: {seq.joint_count}")
print(f"Frame rate: {seq.fps}")

# Plot the motion
optiq viz plotly --dataset dataset.parquet --out exploration.html
```

## 3. Train a Model

Train a simple MLP model for motion prediction:

```bash
# Create a basic model configuration
cat > model_config.yaml << EOF
input_dim: 465  # Adjust based on your data
hidden_dims: [256, 128]
output_dim: 465
horizon: 1
EOF

# Train the model
optiq train model \
  --config model_config.yaml \
  --arch mlp \
  --data dataset.parquet \
  --out trained_model.pt \
  --epochs 50 \
  --batch-size 32
```

## 4. Evaluate Results

Generate predictions and visualize:

```bash
# Generate predictions
optiq predict \
  --model trained_model.pt \
  --data dataset.parquet \
  --out predictions.json

# Create comparison visualization
optiq viz plotly \
  --dataset dataset.parquet \
  --pred predictions.json \
  --out comparison.html
```

## 5. RL Bootstrapping (Optional)

Use your trained model as a starting point for RL:

```bash
# Bootstrap an RL policy
optiq train rl \
  --env Humanoid-v5 \
  --algo ppo \
  --pretrained trained_model.pt \
  --adapter-mode feature \
  --total-steps 100000 \
  --out rl_policy.zip

# Evaluate the policy
optiq viz video \
  --policy rl_policy.zip \
  --env Humanoid-v5 \
  --out policy_rollout.mp4
```

## Complete Example

Here's a complete script that does it all:

```python
#!/usr/bin/env python3
"""
Complete optiq quickstart example
"""
import optiq
from pathlib import Path

def main():
    # 1. Load and prepare data
    print("Loading data...")
    seq = optiq.load_sequence("walking.parquet")

    # 2. Create training dataset
    print("Creating dataset...")
    dataset = optiq.build_imitation_dataset(seq, mode="next", horizon=1)

    # 3. Build and train model
    print("Training model...")
    model = optiq.models.build("mlp",
                               input_dim=seq.feature_dim,
                               hidden_dims=[256, 128],
                               output_dim=seq.feature_dim)

    # Training loop (simplified)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    for epoch in range(10):
        for batch in dataset:
            pred = model(batch["state"])
            loss = F.mse_loss(pred, batch["target"])
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        print(f"Epoch {epoch}: loss = {loss.item():.4f}")

    # 4. Save model
    optiq.models.save_checkpoint(model, "trained_model.pt")
    print("Model saved!")

    # 5. Generate visualization
    print("Creating visualization...")
    optiq.viz.plotly_animation(seq, out_path="result.html")
    print("Done! Open result.html to see the animation")

if __name__ == "__main__":
    main()
```

## What Next?

- **Learn the API**: Check out the [API reference](api.md)
- **Explore examples**: See [examples](examples/index.md) for common use cases
- **Customize training**: Read about [model configuration](user-guide/model-training.md)
- **Advanced RL**: Learn about [policy bootstrapping](user-guide/reinforcement-learning.md)

## Troubleshooting

### Common Issues

**"Module not found" errors:**
```bash
pip install optiq[all]  # Make sure all dependencies are installed
```

**Memory errors during training:**
```bash
# Reduce batch size
optiq train model --batch-size 8 ...

# Use CPU if GPU memory is limited
optiq train model --device cpu ...
```

**Data format issues:**
```bash
# Check your data format
optiq data validate dataset.parquet
```

**Slow training:**
```bash
# Enable GPU acceleration
optiq train model --device cuda ...

# Use mixed precision
export TORCH_USE_CUDA_DSA=1
```

## Get Help

- 📖 **Documentation**: Full guides at [optiq.readthedocs.io](https://optiq.readthedocs.io)
- 💬 **Discussions**: GitHub Discussions for questions
- 🐛 **Issues**: Report bugs on GitHub
- 📧 **Contact**: ted@example.com for direct support

---

**🎉 Congratulations!** You've completed your first optiq workflow. Your motion learning journey starts here!
