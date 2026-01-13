## Data Pipeline and Labeling (FBX → HDF5/Parquet)

### Current state (reference code)
- `FBXDataSet` loads per-frame positions/quaternions from JSON and returns `(x, x)` autoencoder pairs (no labels, no compression):  
```
36:60:src/optiq/rl/fbx_dataset.py
class FBXDataSet(Dataset):
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        x = self.features[idx]
        return x, x  # autoencoder-style
```
- `HumanoidPoseActionDataset` converts FBX JSON into (obs, action) aligned to Gymnasium Mujoco Humanoid via retargeting and finite differences (behavior-clone pretrain path):  
```
63:139:src/optiq/rl/fbx_dataset.py
class HumanoidPoseActionDataset(Dataset):
    ...
    obs = self.env.unwrapped._get_obs()
    act = np.clip(delta / action_scale, -1.0, 1.0)
```

### Target design
1) **Canonical dataset format**: HDF5 or Parquet with:
   - `frames`: dense table/array of per-frame features (positions, quaternions, optional velocities).
   - `metadata`: fps, bone list/order, coordinate conventions, source FBX path, extraction params.
   - `labels`: user-defined conditions per-frame and/or per-sequence (e.g., movement class, phase, subject).
   - `splits`: train/val/test indices or masks.
   - Compression: gzip/snappy (Parquet) or chunked HDF5; include dtype choices (fp32 default).
2) **Schema**:
   - `frames`: shape `(T, F)` where `F = bones * (3 + 4 [+ 3 vel?])`.
   - `labels`: optional `(T, L)` dense or per-sequence dict; allow string→int mapping stored in metadata.
   - `conditions`: JSON sidecar embedded in HDF5/Parquet metadata for custom condition namespaces.
3) **APIs**:
   - `optiq.data.load_fbx(path) -> FrameSequence` (in-memory representation with bones, fps).
   - `FrameSequence.to_table(format="parquet"| "hdf5", out_path, labels=None, compression=...)`.
   - `optiq.data.load_dataset(path, split="train") -> torch.utils.data.Dataset` producing `(prev_state, next_state, condition)`.
   - `optiq.data.build_bc_dataset(path, env_id, retarget_cfg) -> (obs, action)` for behavior cloning.
4) **Labeling flow**:
   - CLI: `optiq data label --in fbx1.fbx fbx2.fbx --out data/seq.parquet --label movement=kick --label phase=windup`.
   - Python: `seq.with_labels(frame_labels=..., seq_labels=...)`.
5) **Conditioning interface**:
   - Models receive `(prev_state, condition)` and output `next_state`.
   - Support optional teacher-forcing for autoregressive rollouts.

### Migration steps
- Add converters: JSON → HDF5/Parquet (preserve original JSON ingest for compatibility).
- Implement `FrameSequence` abstraction + dataset builders (imitation next-step, BC obs-action, autoregressive).
- Update existing uses (e.g., humanoid pipelines) to consume the new loaders while retaining JSON fallback.

### Open decisions
- Whether to store quaternions normalized or raw; default: normalized, validated on write.
- Velocity inclusion: gate via config flag; default enabled for BC datasets.
- Chunk sizing defaults for HDF5 to balance I/O vs. memory. 
