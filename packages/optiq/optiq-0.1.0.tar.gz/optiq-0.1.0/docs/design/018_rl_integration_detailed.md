## RL Integration (Mujoco + SB3) — Detailed Plan

### Scope
- Standardize RL on Gymnasium Mujoco + stable-baselines3 (PPO/SAC first).
- Support two entry paths:
  1) **Behavior Cloning (BC)** from labeled motion datasets → policy init.
  2) **Pretrained sequence model bootstrap** → SB3 policy with adapters.
- Provide reusable helpers under `optiq.rl` and CLI entry `optiq train rl`.

### Components
1) **Dataset builders**
   - `BehaviorCloneDataset` (see `017_retargeting_and_bc.md`): produces `(obs, action)` aligned to env action space. Requires `retarget_fn`.
   - `NextStepDataset` / `AutoregressiveDataset` can be used for supervised warmup of encoders feeding RL (feature-mode).
2) **Bootstrap helpers (`optiq.rl.bootstrap`)**
   - `load_pretrained(path, device, adapter_mode, env_obs_dim, torchscript_in_dim=None, feature_pool="last") -> BootstrapArtifacts`
     - Loads TorchScript or state_dict via model registry.
     - Infers `F_src`; builds `LinearAdapter` to `F_tgt` when needed.
   - `build_features_extractor(pretrained, adapter, mode) -> BaseFeaturesExtractor | None`
   - `make_adapter_obs_wrapper(adapter, env_fn) -> gym.ObservationWrapper`
   - `save_bundle(model, adapter, pre_ts_adapter, path, metadata)`
3) **Policy factory (`optiq.rl.sb3`)**
   - `make_policy(algo, env, features_extractor=None, policy_kwargs=None) -> (model, adapter_metadata)`
   - Support PPO/SAC; allow passing `policy_kwargs` for net_arch, activation_fn, ortho_init, etc.
4) **Evaluation and video**
   - `evaluate(model, env_id, n_episodes, render_mode=None) -> metrics`
   - `record_video(model, env_id, steps, out_path, adapter=None, video_length=1000, fps=30)`; uses VecVideoRecorder/MoviePy.

### Adapter modes (restate with edge cases)
- `obs`: env obs → (optional pre-adapter to torchscript_in_dim) → TorchScript encoder → (optional adapter to env obs dim) → policy.  
  - Use ObservationWrapper; must adjust `observation_space` shape to adapter output.  
  - If env returns dict obs, either disallow or require key selection (CLI flag `--obs-key`).
- `feature`: TorchScript/encoder runs as SB3 `BaseFeaturesExtractor`; adapter maps encoder output to policy feature dim.  
  - Policy sees adapted features; env obs passes through unchanged inside extractor.
- `none`: no pretrained; regular SB3 policy.

### Weight transfer rules (detailed)
- If pretrained is MLP and SB3 policy net has matching linear layer shapes (input/output), copy weights/bias for first N matching layers. Stop copying on first mismatch.
- For CNN/UNet/Transformer encoders used in feature mode, do not attempt layer copy into policy; only reuse encoder outputs (plus adapter).
- Always log:
  - `pretrained_arch`, `F_src`, `F_tgt`, `adapter_hidden`, `mode`.
  - `copied_layers`: list of `(layer_name, copied_bool)`.
  - `random_init_layers`: list of policy layers not touched.

### Config/CLI (augment `012_cli_commands_detailed.md`)
- `optiq train rl --env Humanoid-v5 --algo ppo --total-steps 300000 --num-envs 8 --pretrained ckpt.pth --adapter-mode feature --torchscript-in-dim 128 --adapter-hidden 256,128 --record-video --video-every 50000 --bc-json data/ground_truth.json --bc-steps 5000`
- Flags:
  - `--pretrained`: path to TorchScript/state_dict.
  - `--adapter-mode`: `obs|feature|none`.
  - `--torchscript-in-dim`: if encoder expects different input than env obs.
  - `--adapter-hidden`: comma-separated.
  - `--feature-pool`: `last|mean` for sequence encoders.
  - `--bc-json`: optional ground_truth.json for BC warmup; uses BehaviorCloneDataset with retarget_fn mapping (HumanoidRetarget or custom).
  - `--bc-steps`, `--bc-batch-size`.
  - `--eval-freq`, `--eval-episodes`, `--record-video`, `--video-every`, `--video-length`.
  - `--state-dict-out`: fallback bundle path.
  - `--resume`: SB3 zip to continue.

### Environment handling
- Vectorized envs via `make_vec_env`; seed all envs; set `render_mode` when recording.
- Adapter in obs mode must wrap each env in the vectorized stack; ensure wrapper is applied inside `make_vec_env` callable.
- Action space: assume symmetric Box; clip actions in BC dataset builder; SB3 already squashes actions.

### Evaluation plan
- Periodic EvalCallback with deterministic=True.
- Metrics to log: average reward, episode length, success rate (if available), entropy, value loss, clipped frac (PPO).
- Post-train short rollout for video (if moviepy installed).

### Failure modes and fallbacks
- TorchScript load failure → try state_dict load; if both fail, abort with clear message.
- Shape mismatch when building adapter → raise informative error with src/tgt dims.
- Missing extras (gymnasium/mujoco/stable-baselines3) → friendly ImportError suggesting `pip install optiq[rl]`.
- MoviePy missing → skip video with warning.

### Tests (add to `tests/rl` later)
- Adapter mode obs: dummy encoder projecting obs_dim→obs_dim; confirm wrapper changes observation_space and model trains for few steps.
- Feature mode: dummy encoder output dim != policy feature dim; ensure adapter created, forward passes.
- Weight copy: small MLP pretrained copied into PPO MlpPolicy torso; assert first linear weights equal.
- State bundle roundtrip: save_bundle → load → run one predict step and compare outputs (within tolerance).

### Migration of existing example (`examples/humanoid_imitation/train_mujoco.py`)
- Replace ad-hoc TorchScript/adapter handling with bootstrap helpers.
- Use BehaviorCloneDataset from `optiq.data` + `retarget_fn` (HumanoidRetarget) for `--bc-json`.
- Keep post-train video, but move implementation into `optiq.vis.video.render_policy` and call it.
- Ensure CLI flags map to new helper parameters; preserve current defaults where sensible.

### Explicit wiring: pretrained model → RL policy
1) Load pretrained sequence model (state_dict via registry or TorchScript).
2) Infer encoder output dim (`F_src`) with dummy forward; flatten if sequence output.
3) Determine target dim:
   - `obs` mode: env obs dim.
   - `feature` mode: first Linear in SB3 policy features extractor; probe policy or use registry helper.
4) Build adapters:
   - If `torchscript_in_dim` is set and different from env obs dim, create `pre_ts_adapter` mapping env obs → TS input.
   - If `F_src != F_tgt`, create `adapter` mapping encoder out → policy expected dim.
5) Plug into SB3:
   - `obs` mode: wrap env with `AdapterObsWrapper(pre_ts_adapter + encoder + adapter)`; policy stays vanilla.
   - `feature` mode: pass encoder (+adapter) as `features_extractor` in `policy_kwargs`.
6) Weight transfer (if shapes align for MLP torso): copy matching Linear layers; log copied vs randomized.
7) Train with SB3; save both SB3 zip and state_dict bundle (policy + adapters + metadata).
