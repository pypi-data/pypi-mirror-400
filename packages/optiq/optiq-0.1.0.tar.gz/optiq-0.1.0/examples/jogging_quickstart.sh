#!/usr/bin/env bash
# Quickstart: train and visualize on the jogging example from a clean repo checkout.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

JSON_PATH="$ROOT/extracted_jogging/jogging_anim.json"
GT_JSON="$JSON_PATH"

if [ ! -f "$JSON_PATH" ]; then
  FBX_PATH="$ROOT/Jogging.fbx"
  if [ ! -f "$FBX_PATH" ]; then
    echo "ERROR: Missing animation JSON at $JSON_PATH and no FBX found at $FBX_PATH to regenerate it."
    exit 1
  fi
  echo "Animation JSON not found. Extracting from $FBX_PATH ..."
  uv run node scripts/extract_fbx_anim.js "$FBX_PATH" "$JSON_PATH"
fi

echo "Training (CNN, next-frame) on $JSON_PATH ..."
uv run --python ./.uv-venv/bin/python python scripts/train_sphere_cnn.py \
  --config configs/train_cnn_next.yaml "$JSON_PATH"

echo "Rendering Plotly animation with GT overlay..."
uv run --python ./.uv-venv/bin/python --with plotly --with trimesh --with numpy \
  python scripts/plotly_anim.py predicted_bones.json --gt "$GT_JSON" --out anim_pred.html

echo "Done. Open anim_pred.html in your browser."

