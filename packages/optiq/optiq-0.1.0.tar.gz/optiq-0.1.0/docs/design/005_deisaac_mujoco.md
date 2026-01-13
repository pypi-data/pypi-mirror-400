## Remove Isaac / Isaac Lab, Standardize on Mujoco + SB3

### Isaac references to remove
- Humanoid example imports and conversion calls:  
```
16:18:examples/humanoid_imitation/run.py
from optiq.rl.isaac_utils import convert_motion_to_isaac_npy, generate_isaac_gym_config
126:239:examples/humanoid_imitation/run.py
isaac_motion_path = os.path.join(data_dir, "isaac_motion.npy")
...
bone_order = convert_motion_to_isaac_npy(gt_path, isaac_motion_path)
generate_isaac_gym_config("HumanoidBootstrap", isaac_motion_path, output_path=isaac_config_path)
```
- Isaac utilities (to delete):  
```
1:111:src/optiq/rl/isaac_utils.py
def convert_motion_to_isaac_npy(...):
    ...
def generate_isaac_gym_config(...):
    ...
```
- Pipeline script supports Isaac backend; should be pruned to Mujoco-only:  
```
1:114:examples/humanoid_imitation/run_pipeline.sh
BACKEND="${BACKEND:-mujoco}"
...
if [[ "${BACKEND}" == "mujoco" ]]; then
  ...
fi
...
./isaaclab.sh ...
```
- Isaac launcher script (remove):  
```
1:132:examples/humanoid_imitation/train_rl.py
"""Bootstrap Isaac Lab RL training ..."""
...
subprocess.check_call(cmd, cwd=isaaclab_path)
```
- Isaac config artifact: `examples/humanoid_imitation/isaac_task.yaml`
- Dockerfile installs Isaac Sim (remove those sections/env vars):  
```
5:71:Dockerfile
ARG ISAAC_SIM_GIT_URL=...
... apt-get install isaac-sim ...
ENV ISAACSIM_PATH=...
```

### Target Mujoco-only behavior
- Example pipeline should: extract FBX → build dataset (HDF5/Parquet) → pretrain model → optional SB3 PPO/SAC bootstrap → visualize (Plotly/MoviePy). No Isaac steps.
- CLI should surface Mujoco/SB3 options only.

### Actions
1) Delete `src/optiq/rl/isaac_utils.py`; remove all imports/usages.
2) Simplify `examples/humanoid_imitation/run.py`: drop Isaac motion/config steps; keep extraction, pretrain, Plotly viz, and PPO bootstrap.
3) Rewrite `examples/humanoid_imitation/run_pipeline.sh` to only run Mujoco path (remove BACKEND switch, IsaacLab checks).
4) Remove `examples/humanoid_imitation/train_rl.py` and `examples/humanoid_imitation/isaac_task.yaml`.
5) Strip Isaac Sim install blocks and env vars from `Dockerfile` (and any other Dockerfile variants if present); ensure Mujoco deps remain.
6) Search for `isaac` mentions elsewhere (docs/tests/configs) and remove or update to Mujoco equivalents.

### Replacement guidance
- For motion export and configs, rely on the new dataset layer (HDF5/Parquet) and Mujoco retargeting already present in `HumanoidPoseActionDataset`.
- For RL launches, use `examples/humanoid_imitation/train_mujoco.py` (to be refactored into framework CLI per other docs).
- Ensure logging/metrics paths remain valid after file deletions.
