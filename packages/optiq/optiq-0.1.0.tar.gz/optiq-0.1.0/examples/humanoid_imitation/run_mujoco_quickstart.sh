#!/usr/bin/env bash
# Minimal Mujoco humanoid PPO run with zero required parameters.
# Requires: uv, gymnasium[mujoco], mujoco (Python package).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

uv run python "${SCRIPT_DIR}/train_mujoco.py" \
  --env-id Humanoid-v5 \
  --total-timesteps 100000 \
  --num-envs 4

echo "Done. Logs/models under ${SCRIPT_DIR}/data"
