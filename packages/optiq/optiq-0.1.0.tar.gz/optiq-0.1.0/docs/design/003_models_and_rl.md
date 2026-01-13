## Models, Adapters, and RL Bootstrapping

### Current state (reference code)
- Adapters wrap pretrained features to policy inputs:  
```
18:74:src/optiq/rl/adapter.py
class LinearAdapter(nn.Module):
    ...
def build_linear_adapter(...):
    return LinearAdapter(...)
```
- TorchScript feature extractor wrapper used in Mujoco trainer:  
```
77:99:src/optiq/rl/adapter.py
class TorchScriptFeatureExtractor(nn.Module):
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.script(x)
        if self.adapter:
            out = self.adapter(out)
        return out
```
- Mujoco trainer already accepts TorchScript models and adapter modes:  
```
37:139:examples/humanoid_imitation/train_mujoco.py
from optiq.rl.adapter import build_linear_adapter, TorchScriptFeatureExtractor
...
parser.add_argument("--adapter-mode", choices=["obs", "feature", "none"], default="none", ...)
parser.add_argument("--torchscript-path", default=None, ...)
parser.add_argument("--torchscript-in-dim", type=int, default=None, ...)
```

### Target model suite
- **Transformer**: sequence-to-sequence next-state predictor with optional causal masking; supports conditioning tokens for labels.
- **MLP**: feedforward predictor for single-step or short horizon; baseline for small datasets.
- **UNet (temporal 1D)**: multi-scale temporal convs for smoother motion prediction; supports noise conditioning for diffusion-style training (align with existing `train_unet_diffusion.yaml`).
- All models registered via `optiq.models.registry` with config-driven construction; expose standardized forward signature: `forward(prev_state, condition=None, context=None) -> next_state`.

### Adapters and feature space
- Keep `LinearAdapter` and `TorchScriptFeatureExtractor`; extend with:
  - Shape inference helper for pretrain→policy (already present as `infer_linear_adapter_from_models`; expand tests).
  - Observation wrapper for SB3 that applies pretrained encoder before env observation is passed to policy (obs mode).
  - Feature-extractor mode using SB3 `BaseFeaturesExtractor` subclass wrapping pretrained encoder output.

### RL bootstrapping (stable-baselines3)
- Policy initialization path:
  - Load pretrained model weights (state_dict or TorchScript) from disk.
  - If feature dims mismatch, auto-build adapter to map pretrained output → policy input.
  - Support PPO and SAC initializers (matching existing trainer CLI).
- Behavior cloning option:
  - Use `HumanoidPoseActionDataset`-like loader but generalized over datasets to run BC steps before RL fine-tuning.
- Checkpointing:
  - Primary: SB3 `.zip`.
  - Fallback: torch `state_dict` (already used when TorchScript fails to serialize full policy).

### Proposed APIs
- `optiq.models.build(name, **cfg) -> nn.Module` (names: `transformer`, `mlp`, `unet1d`).
- `optiq.rl.bootstrap.load_pretrained(path, adapter_mode, env_obs_dim, torchscript_in_dim=None) -> (features_extractor, adapter, metadata)`.
- SB3 integration: `optiq.rl.sb3.make_policy(algo, env, features_extractor, adapter)` that returns PPO/SAC policy with initialized weights.

### Migration steps
- Implement model registry + default configs for three architectures.
- Refactor Mujoco trainer to use registry and bootstrap helper instead of ad-hoc TorchScript handling.
- Add tests for adapter inference and weight loading.
- Remove Isaac references from trainer and examples; ensure Mujoco-only pipeline remains. 
