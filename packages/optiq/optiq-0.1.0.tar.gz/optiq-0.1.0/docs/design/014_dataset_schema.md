## Dataset Schema (HDF5/Parquet) and Labeling Details

### Objects
- **FrameSequence**: base motion data.
- **LabeledSequence**: FrameSequence + labels/conditions.

### Field definitions
- `fps` (int): frames per second.
- `bone_names` (list[str]): ordered list used to flatten frames.
- `frames` (array float32): shape `(T, F)`, where `F = len(bone_names) * (3 + 4)` for pos+quat. Stored row-wise.
- `velocities` (optional array float32): shape `(T, F)`, same flattening; derived via finite differences.
- `labels` (optional array float32/int/one-hot): shape `(T, L)`; one row per frame. Could be multi-hot or numeric. Encourage metadata to include `label_names` or `label_vocab`.
- `seq_labels` (optional dict): sequence-level annotations (e.g., movement class, subject id).
- `metadata` (dict): free-form; include `source_fbx`, `extraction_fps`, `coordinate_system`, `created_at`, `conditions`.
- `splits` (optional): train/val/test indices or masks; suggested to store in `metadata["splits"]` or as columns in parquet.
- `conditions` (dict): namespace → mapping for condition embeddings; recommended to keep in `metadata["conditions"]`.

### Parquet layout
- Table columns:
  - `frames`: list<float32> length F.
  - Optional `velocities`: list<float32> length F.
  - Optional `labels`: list<float32|int> length L.
- Schema metadata (`optiq_metadata` JSON):
  - `fps`, `bone_names`, `metadata`, `has_velocities`, `has_labels`, `seq_labels`, optional `splits`.
- Compression: snappy (default); allow override to gzip/zstd via CLI flag.
- Row groups: leave to parquet defaults; allow CLI `--row-group-size`.

### HDF5 layout
- Datasets:
  - `/frames` float32 `(T, F)`
  - Optional `/velocities` float32 `(T, F)`
  - Optional `/labels` float32 `(T, L)`
- Attributes:
  - `fps` (int)
  - `bone_names` (JSON)
  - `metadata` (JSON)
  - Optional `seq_labels` (JSON)
  - Optional `splits` (JSON)
- Compression: gzip; allow CLI flag `--compression`.

### Labeling/conditions
- Per-frame labels:
  - CLI accepts `--frame-labels path.json` where JSON is either:
    - `{ "labels": [[...], [...]], "label_names": ["movement", "phase"] }` length T
    - or dict of arrays keyed by label name.
  - Store numeric labels in `labels`; store vocab in `metadata["label_vocab"]`.
- Conditions for models:
  - Flattened vector derived from labels; keep mapping in metadata:
    - `metadata["condition_keys"] = ["movement", "phase"]`
    - `metadata["condition_dim"] = L`
- Splits:
  - `metadata["splits"] = {"train": [0,1,...], "val": [...], "test": [...]}` or boolean masks.

### FBX ingestion defaults
- Coordinate system: keep as extracted; note in `metadata["coordinate_system"]`.
- Quaternion normalization: enforce on write; store flag `metadata["normalized_quaternions"]=true`.
- Missing bones: fill pos (0,0,0), quat (0,0,0,1).

### Validation rules
- Ensure consistent frame count across bones before write.
- Check `frames.shape[1] == len(bone_names)*7` (if pos+quat).
- If velocities provided, same shape as frames.
- If labels provided, `labels.shape[0] == frames.shape[0]`.
- Normalize quaternions and optionally clamp NaNs/inf → error unless `--allow-NaN` flag.

### CLI implications
- `optiq data convert`: writes parquet/hdf5; can emit both JSON + table if `--keep-json`.
- `optiq data label`: loads parquet/hdf5, applies labels, updates metadata, writes new file.
- `optiq data split`: updates metadata with split masks/indices. 
