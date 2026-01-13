## Visualization Standardization (Plotly/MoviePy)

### Existing visualization code
- Plotly skeletal animation helper:  
```
1:158:src/optiq/vis/plotly_anim_runner.py
BONE_EDGES = [...]
def load_anim(path: str): ...
def frame_traces(...): ...
```
- Mujoco trainer video recording with optional adapter wrapper:  
```
400:458:examples/humanoid_imitation/train_mujoco.py
if args.post_train_video:
    import moviepy
    class AdapterObsWrapper(gym.ObservationWrapper): ...
```
- Scripts for plotly videos: `scripts/plotly_anim.py`, `plotly_anim_obj.py`, etc.

### Target API in `optiq.vis`
- `optiq.vis.plotly.build_skeleton_html(pred_path, gt_path=None, out_path=None, use_tubes=False, edges=BONE_EDGES) -> Path`
  - Loads FrameSequence-compatible JSON (or parquet/hdf5 via load_sequence), renders comparison HTML.
- `optiq.vis.video.render_policy(model_path, env_id, adapter=None, steps, out_path, video_length=1000, fps=30)`
  - Wraps SB3 model; supports adapter-mode obs wrapper; records via MoviePy if installed.
- `optiq.vis.plotly.frame_traces` remains as a low-level utility but should accept np arrays as well as lists.

### CLI integration
- `optiq viz plotly --dataset data/seq.parquet --out viz.html --gt data/gt.parquet --tubes`
- `optiq viz video --policy sb3.zip --env Humanoid-v5 --out video.mp4 --adapter-mode obs --adapter-path adapter.pth`

### Data compatibility
- Plotly loader should accept:
  - JSON from node extractor (`bones`, `fps`, `frames`, `bone_names`).
  - `FrameSequence` parquet/hdf5 via `optiq.data.load_sequence`.
- Bone edge defaults remain `BONE_EDGES`, but allow override via args.

### Testing
- Plotly: generate a tiny 2-frame synthetic sequence, render HTML, assert file exists and non-empty.
- MoviePy: skip if moviepy missing; otherwise render a 5-step dummy video with a stub policy.

### Migration steps
- Move reusable visualization logic from `examples/humanoid_imitation/train_mujoco.py` and `scripts/plotly_anim*.py` into `optiq.vis`.
- Expose via CLI (`optiq viz ...`).
- Keep node/FBX extract scripts untouched; only wrap their outputs. 
