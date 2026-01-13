#!/usr/bin/env bash
# End-to-end humanoid pipeline (Mujoco-only).
# Requirements:
# - uv installed (or edit commands to use python directly)
# - mujoco python package + gymnasium[mujoco]
#
# Env overrides (all optional):
#   MUJOCO_ENV_ID        Gym Mujoco env id (default: Humanoid-v5)
#   MUJOCO_NUM_ENVS      Number of parallel Mujoco envs (default: 4)
#   MUJOCO_TOTAL_STEPS   Total PPO steps for Mujoco (default: 300000)
#   MUJOCO_RECORD        true/false to record Mujoco videos (default: false)
#   MUJOCO_VIDEO_EVERY   Record video every N steps (default: 50000)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

MUJOCO_ENV_ID="${MUJOCO_ENV_ID:-Humanoid-v5}"
MUJOCO_NUM_ENVS="${MUJOCO_NUM_ENVS:-4}"
MUJOCO_TOTAL_STEPS="${MUJOCO_TOTAL_STEPS:-300000}"
MUJOCO_RECORD="${MUJOCO_RECORD:-false}"
MUJOCO_VIDEO_EVERY="${MUJOCO_VIDEO_EVERY:-50000}"

echo "=== Humanoid pipeline (Mujoco) ==="
echo "Project root: ${PROJECT_ROOT}"
echo "Mujoco env: ${MUJOCO_ENV_ID}"
echo "Mujoco num envs: ${MUJOCO_NUM_ENVS}"
echo "Mujoco total steps: ${MUJOCO_TOTAL_STEPS}"
echo "Mujoco record: ${MUJOCO_RECORD}"
echo "========================="

echo "--- Running Mujoco locomotion (no Isaac Sim required) ---"
RECORD_FLAG=()
if [[ "${MUJOCO_RECORD}" == "true" || "${MUJOCO_RECORD}" == "True" ]]; then
  RECORD_FLAG+=(--record-video)
fi

uv run python "${SCRIPT_DIR}/train_mujoco.py" \
  --env-id "${MUJOCO_ENV_ID}" \
  --total-timesteps "${MUJOCO_TOTAL_STEPS}" \
  --num-envs "${MUJOCO_NUM_ENVS}" \
  --video-every "${MUJOCO_VIDEO_EVERY}" \
  "${RECORD_FLAG[@]:-}"

echo "=== Done. Mujoco PPO launched ==="
