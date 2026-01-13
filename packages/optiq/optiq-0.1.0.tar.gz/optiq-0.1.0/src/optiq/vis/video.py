from __future__ import annotations

import os
from typing import Optional


def render_policy_video(
    policy_path: str,
    env_id: str,
    out_path: str,
    steps: int = 1000,
    render_fps: int = 30,
) -> str:
    """
    Roll out an SB3 policy and export MP4 via moviepy.

    Requires stable-baselines3, gymnasium, and moviepy (install via extras [rl] and [viz]).
    """
    try:
        import gymnasium as gym
        from stable_baselines3 import PPO, SAC
    except Exception as e:  # pragma: no cover - optional dep
        raise ImportError(
            "stable-baselines3 and gymnasium are required for video rendering"
        ) from e
    try:
        import moviepy.editor as mpy
    except Exception as e:  # pragma: no cover - optional dep
        raise ImportError(
            "moviepy is required for video rendering; install optiq[viz]."
        ) from e

    if not os.path.exists(policy_path):
        raise FileNotFoundError(f"Policy not found: {policy_path}")

    algo = None
    if policy_path.endswith(".zip"):
        # heuristic: PPO/SAC both save .zip; try PPO then SAC
        try:
            model = PPO.load(policy_path, device="cpu")
            algo = "ppo"
        except Exception:
            model = SAC.load(policy_path, device="cpu")
            algo = "sac"
    else:
        # fallback assume PPO state_dict
        model = PPO.load(policy_path, device="cpu")
        algo = "ppo"

    env = gym.make(env_id, render_mode="rgb_array")
    frames = []
    obs, _ = env.reset()
    for _ in range(steps):
        action, _ = model.predict(obs, deterministic=True)
        obs, _, done, truncated, _ = env.step(action)
        frame = env.render()
        if frame is not None:
            frames.append(frame)
        if done or truncated:
            obs, _ = env.reset()
    env.close()

    if not frames:
        raise RuntimeError("No frames captured; check render_mode support for env.")

    clip = mpy.ImageSequenceClip(frames, fps=render_fps)
    clip.write_videofile(out_path, codec="libx264", audio=False)
    return out_path
