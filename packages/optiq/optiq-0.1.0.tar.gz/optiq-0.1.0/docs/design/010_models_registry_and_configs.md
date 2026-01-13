## Model Registry, Architectures, and Training Defaults

**Status: ✅ Implemented**

### Registry API (implemented)
- `optiq.models.build(name: str, **cfg) -> nn.Module`
  - Supported: `transformer`, `mlp`, `unet1d`
- `optiq.models.list_models() -> List[str>`
- `optiq.models.load_checkpoint(path) -> (model, metadata)`; supports state_dict with metadata and TorchScript.
- `optiq.models.export_torchscript(model, example_input, out_path)`

### Architectures (supported)
- **TransformerModel**: causal mask, conditioning token, `(B, T, F)` → `(B, F)`
- **MLPModel**: horizon flattening, conditioning concat, `(B, F)`/`(B, T, F)` → `(B, F)`
- **UNet1DModel**: temporal 1D UNet, optional attention, `(B, C_in, T)` → `(B, F)`

### Default config templates (added)
- `configs/model_transformer.yaml`
- `configs/model_mlp.yaml`
- `configs/model_unet1d.yaml`

Each template includes input/output/conditioning dims, optimizer (AdamW), cosine scheduler, and grad clip.

### Training expectations (unchanged)
- Forward signature: `forward(prev_state, condition=None, context=None) -> next_state`
- Loss targets: next-step or sequence MSE; optional masking

### Checkpoints (implemented)
- State dict with metadata: `{"arch", "config", "model_state_dict", ...}`
- TorchScript export via `export_torchscript`

### Integration with RL bootstrap
- TorchScript artifacts can be wrapped with `TorchScriptFeatureExtractor`
- Adapter inference covered by `infer_linear_adapter_from_models`

### Tests (added)
- Shape tests per model
- Serialization roundtrip via `load_checkpoint`
- TorchScript export smoke test
- Adapter inference test
- Config template presence check
