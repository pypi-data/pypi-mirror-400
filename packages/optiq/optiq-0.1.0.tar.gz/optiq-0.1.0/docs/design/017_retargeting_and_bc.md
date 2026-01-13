## Retargeting and Behavior Cloning (Generalized)

### Current reference
- `HumanoidPoseActionDataset` in `src/optiq/rl/fbx_dataset.py` builds (obs, action) for Humanoid-v5 using `HumanoidRetarget`.

### Target design
- Provide a general BC dataset builder that:
  - Accepts `FrameSequence` with `raw_bones`.
  - Requires a `retarget_fn(frame_dict) -> qpos`.
  - Uses env (`gymnasium.make(env_id)`) to compute obs via `_get_obs()` and actions via `(qpos_tp1 - qpos_t)/dt` scaled by `action_space.high`.
  - Works for arbitrary envs with compatible set_state/_get_obs interfaces.
- Expose utilities:
  - `optiq.rl.retargeting.load_mapping(name: str)` to retrieve known skeleton mappings (e.g., mixamo→humanoid).
  - `optiq.rl.retargeting.frame_to_qpos(frame_dict, mapping, defaults) -> qpos`.
  - `optiq.rl.bc.build_dataset(sequence, env_id, retarget_fn, action_fn=None, dt=None) -> BehaviorCloneDataset`.

### Configuration knobs
- `dt`: defaults to `1/fps`.
- `action_fn`: pluggable; default finite-difference normalized by action scale.
- `clip_actions`: bool (default True).
- `obs_postprocess`: optional function to massage obs (e.g., center-of-mass offsets).

### Error handling
- If `gymnasium` missing, raise friendly ImportError suggesting `pip install optiq[rl]`.
- If `raw_bones` absent, instruct to load from JSON (node extract) and keep raw structure.

### Testing
- Create a tiny synthetic skeleton (2 bones, 3 frames) with identity quats; retarget_fn returns small qpos; verify dataset lengths, obs/action shapes, and value ranges.
- Ensure action clipping respects env action bounds.
