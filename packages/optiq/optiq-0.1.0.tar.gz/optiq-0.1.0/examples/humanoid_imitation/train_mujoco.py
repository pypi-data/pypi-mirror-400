"""
Mujoco locomotion launcher for the humanoid example.

This mirrors the DeepMind `mujoco_playground` locomotion notebook and runs a
Humanoid PPO baseline using Gymnasium's Mujoco tasks (requires the `mujoco`
python package and Gymnasium installed with the `mujoco` extra).

Example:
    uv run python examples/humanoid_imitation/train_mujoco.py \
      --env-id Humanoid-v5 \
      --total-timesteps 500000 \
      --num-envs 8 \
      --record-video

If you want a closer match to the notebook defaults, bump `--total-timesteps`
and set `--eval-freq` to the interval you want videos/checkpoints for.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import List, Optional, Sequence

import gymnasium as gym
import numpy as np
import torch
from stable_baselines3 import PPO, SAC
from stable_baselines3.common.callbacks import EvalCallback
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
from stable_baselines3.common.vec_env import VecVideoRecorder
from torch.utils.data import DataLoader

from optiq.rl.bootstrap import (
    AdapterSpec,
    PretrainedSpec,
    build_adapters,
    load_pretrained,
    make_obs_wrapper,
    make_policy,
)
from optiq.rl.fbx_dataset import HumanoidPoseActionDataset

try:
    import mlflow
except Exception:  # pragma: no cover - optional dependency
    mlflow = None


def _maybe_wrap_video(
    env, record_video: bool, video_folder: str, video_length: int, video_every: int
):
    """Wrap the vectorized env with a video recorder when requested."""
    if not record_video:
        return env

    os.makedirs(video_folder, exist_ok=True)

    def _trigger(step: int) -> bool:
        return step % video_every == 0

    return VecVideoRecorder(
        env,
        video_folder,
        record_video_trigger=_trigger,
        video_length=video_length,
        name_prefix="mujoco-locomotion",
    )


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train Mujoco Humanoid locomotion with PPO."
    )
    parser.add_argument(
        "--env-id", default="Humanoid-v5", help="Gymnasium Mujoco env id."
    )
    parser.add_argument(
        "--total-timesteps", type=int, default=300_000, help="Training horizon."
    )
    parser.add_argument(
        "--num-envs", type=int, default=4, help="Number of parallel envs."
    )
    parser.add_argument(
        "--seed", type=int, default=7, help="Random seed for reproducibility."
    )
    parser.add_argument(
        "--algo", choices=["ppo", "sac"], default="ppo", help="RL algorithm."
    )
    parser.add_argument(
        "--learning-rate", type=float, default=3e-4, help="Policy learning rate."
    )
    parser.add_argument(
        "--n-steps",
        type=int,
        default=2048,
        help="Rollout steps per env before update (PPO).",
    )
    parser.add_argument(
        "--batch-size", type=int, default=256, help="Mini-batch size (PPO/SAC)."
    )
    parser.add_argument("--gamma", type=float, default=0.99, help="Discount factor.")
    parser.add_argument(
        "--gae-lambda", type=float, default=0.95, help="GAE lambda (PPO)."
    )
    parser.add_argument("--clip-range", type=float, default=0.2, help="PPO clip range.")
    parser.add_argument(
        "--ent-coef", type=float, default=0.0, help="Entropy regularization weight."
    )
    parser.add_argument(
        "--model-out",
        default=os.path.join(
            os.path.dirname(__file__), "data", "mujoco_humanoid_ppo.zip"
        ),
    )
    parser.add_argument(
        "--log-dir",
        default=os.path.join(os.path.dirname(__file__), "data", "mujoco_logs"),
        help="Tensorboard/log directory.",
    )
    parser.add_argument(
        "--record-video", action="store_true", help="Enable VecVideoRecorder."
    )
    parser.add_argument(
        "--video-folder",
        default=os.path.join(os.path.dirname(__file__), "data", "mujoco_videos"),
    )
    parser.add_argument(
        "--video-length", type=int, default=1000, help="Frames per recorded video."
    )
    parser.add_argument(
        "--video-every", type=int, default=50_000, help="Record every N steps."
    )
    parser.add_argument(
        "--post-train-video",
        dest="post_train_video",
        action="store_true",
        help="Record a short evaluation video after training.",
    )
    parser.add_argument(
        "--no-post-train-video",
        dest="post_train_video",
        action="store_false",
        help="Disable post-training video recording.",
    )
    parser.set_defaults(post_train_video=True)
    parser.add_argument(
        "--eval-freq", type=int, default=50_000, help="Evaluation frequency (steps)."
    )
    parser.add_argument(
        "--eval-episodes", type=int, default=5, help="Episodes per evaluation."
    )
    parser.add_argument(
        "--render-after", type=int, default=0, help="Optional post-train render steps."
    )
    parser.add_argument(
        "--resume",
        default=None,
        help="Path to an existing SB3 .zip to continue training.",
    )
    parser.add_argument(
        "--adapter-in-dim",
        type=int,
        default=None,
        help="If set, wrap obs with a LinearAdapter from this dim to env obs dim.",
    )
    parser.add_argument(
        "--adapter-hidden",
        type=str,
        default=None,
        help="Comma-separated hidden dims for the adapter (e.g., '256,128').",
    )
    parser.add_argument(
        "--torchscript-path",
        default=None,
        help="Path to a TorchScript model to use as encoder/feature extractor.",
    )
    parser.add_argument(
        "--adapter-mode",
        choices=["obs", "feature", "none"],
        default="none",
        help="How to apply the TorchScript model (observation wrapper or policy feature extractor).",
    )
    parser.add_argument(
        "--torchscript-in-dim",
        type=int,
        default=None,
        help="If set and different from env obs dim, build a pre-adapter to match TorchScript input.",
    )
    parser.add_argument(
        "--state-dict-out",
        default=os.path.join(
            os.path.dirname(__file__), "data", "mujoco_policy_state.pth"
        ),
        help="Optional path to save a PyTorch state_dict fallback when full SB3 save is not available.",
    )
    parser.add_argument(
        "--bc-json",
        default=None,
        help="Optional ground_truth.json from animation to behavior-clone before RL.",
    )
    parser.add_argument(
        "--bc-steps",
        type=int,
        default=0,
        help="Number of gradient steps for behavior cloning pretrain.",
    )
    parser.add_argument(
        "--bc-batch-size", type=int, default=256, help="BC mini-batch size."
    )
    parser.add_argument(
        "--bc-env-id",
        default=None,
        help="Env id to use for BC dataset (defaults to env-id).",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)

    mlflow_client = mlflow
    mlflow_run = None
    if mlflow_client:
        tracking_uri = os.environ.get(
            "MLFLOW_TRACKING_URI",
            f"file:{os.path.join(os.path.dirname(__file__), 'mlruns_mujoco')}",
        )
        (
            os.makedirs(tracking_uri.replace("file:", ""), exist_ok=True)
            if tracking_uri.startswith("file:")
            else None
        )
        try:
            mlflow_client.set_tracking_uri(tracking_uri)
            mlflow_client.set_experiment(
                os.environ.get("MLFLOW_EXPERIMENT_NAME", "mujoco-locomotion")
            )
        except Exception as e:
            print(f"MLflow setup failed ({e}); continuing without MLflow.")
            mlflow_client = None

    render_mode = "rgb_array" if args.record_video or args.render_after > 0 else None

    os.makedirs(args.log_dir, exist_ok=True)

    adapter_hidden: Optional[Sequence[int]] = None
    if args.adapter_hidden:
        adapter_hidden = [int(x) for x in args.adapter_hidden.split(",") if x.strip()]

    # Probe obs dim once to size the adapter before creating vectorized envs.
    base_env = gym.make(args.env_id, render_mode=render_mode)
    obs_dim = base_env.observation_space.shape[0]

    base_env.close()

    pretrained: Optional[PretrainedSpec] = None
    adapter_spec: AdapterSpec = AdapterSpec(
        pre_adapter=None, adapter=None, features_extractor_class=None
    )
    if args.torchscript_path:
        ts_in = args.torchscript_in_dim or obs_dim
        pretrained = load_pretrained(
            args.torchscript_path,
            torchscript_in_dim=ts_in,
            adapter_hidden=adapter_hidden,
            device="cpu",
        )
        adapter_spec = build_adapters(
            env_obs_dim=obs_dim,
            pretrained=pretrained,
            adapter_mode=args.adapter_mode,
            adapter_hidden=adapter_hidden,
        )

    wrapper = None
    if args.adapter_mode == "obs" and pretrained is not None:
        wrapper = make_obs_wrapper(pretrained, adapter_spec, target_obs_dim=obs_dim)

    env = make_vec_env(
        env_id=args.env_id,
        n_envs=args.num_envs,
        seed=args.seed,
        monitor_dir=args.log_dir,
        env_kwargs={"render_mode": render_mode},
        wrapper_class=wrapper,
    )
    env = _maybe_wrap_video(
        env, args.record_video, args.video_folder, args.video_length, args.video_every
    )

    eval_env = make_vec_env(
        env_id=args.env_id,
        n_envs=1,
        seed=args.seed + 1,
        monitor_dir=None,
        env_kwargs={"render_mode": "rgb_array"},
        wrapper_class=wrapper,
    )

    best_dir = os.path.dirname(args.model_out) or "."
    os.makedirs(best_dir, exist_ok=True)

    callbacks = []
    best_path = best_dir
    if pretrained is not None and args.adapter_mode == "feature":
        best_path = None
    callbacks.append(
        EvalCallback(
            eval_env,
            best_model_save_path=best_path,
            log_path=args.log_dir,
            eval_freq=args.eval_freq // max(args.num_envs, 1),
            n_eval_episodes=args.eval_episodes,
        )
    )

    policy_kwargs = dict()
    tb_log_dir: Optional[str] = args.log_dir
    try:
        from torch.utils.tensorboard import SummaryWriter  # noqa: F401
    except Exception:
        print("TensorBoard not installed; disabling tensorboard logging.")
        tb_log_dir = None

    if args.adapter_mode == "feature" and adapter_spec.features_extractor_class is None:
        raise ValueError("--adapter-mode=feature requires --torchscript-path")

    if adapter_spec.features_extractor_class:
        policy_kwargs["features_extractor_class"] = (
            adapter_spec.features_extractor_class
        )

    algo_kwargs = dict(
        verbose=1,
        learning_rate=args.learning_rate,
        tensorboard_log=tb_log_dir,
    )
    if args.algo == "ppo":
        algo_kwargs.update(
            n_steps=args.n_steps,
            batch_size=args.batch_size,
            gamma=args.gamma,
            gae_lambda=args.gae_lambda,
            clip_range=args.clip_range,
            ent_coef=args.ent_coef,
        )
    else:
        algo_kwargs.update(batch_size=args.batch_size, gamma=args.gamma)

    if args.resume:
        if not os.path.exists(args.resume):
            sys.exit(f"Resume path not found: {args.resume}")
        if args.algo == "ppo":
            model = PPO.load(args.resume, env=env, device="auto")
        else:
            model = SAC.load(args.resume, env=env, device="auto")
    else:
        model = make_policy(
            args.algo,
            env,
            args.adapter_mode,
            adapter_spec,
            policy_kwargs=policy_kwargs,
            **algo_kwargs,
        )

    if mlflow_client:
        try:
            mlflow_run = mlflow_client.start_run(run_name=f"{args.env_id}-ppo")
            mlflow_client.log_params(
                {
                    "env_id": args.env_id,
                    "total_timesteps": args.total_timesteps,
                    "num_envs": args.num_envs,
                    "seed": args.seed,
                    "learning_rate": args.learning_rate,
                    "n_steps": args.n_steps,
                    "batch_size": args.batch_size,
                    "gamma": args.gamma,
                    "gae_lambda": args.gae_lambda,
                    "clip_range": args.clip_range,
                    "ent_coef": args.ent_coef,
                    "record_video": args.record_video,
                }
            )
        except Exception as e:
            print(f"MLflow run start failed ({e}); continuing without MLflow.")
            mlflow_run = None
            mlflow_client = None

    def _run_bc_if_requested():
        if not args.bc_json or args.bc_steps <= 0:
            return
        bc_env_id = args.bc_env_id or args.env_id
        try:
            dataset = HumanoidPoseActionDataset(args.bc_json, env_id=bc_env_id)
        except Exception as e:
            print(f"BC dataset creation failed: {e}")
            return

        loader = DataLoader(
            dataset, batch_size=args.bc_batch_size, shuffle=True, drop_last=True
        )
        device = model.policy.device
        print(
            f"Running behavior cloning pretrain for {args.bc_steps} steps on {len(dataset)} samples..."
        )
        model.policy.set_training_mode(True)
        steps_done = 0
        while steps_done < args.bc_steps:
            for obs, act in loader:
                obs = obs.to(device)
                act = act.to(device)
                dist = model.policy.get_distribution(obs)
                log_prob = dist.log_prob(act)
                if log_prob.dim() > 1:
                    log_prob = log_prob.sum(-1)
                loss = -(log_prob.mean())
                model.policy.optimizer.zero_grad()
                loss.backward()
                model.policy.optimizer.step()
                steps_done += 1
                if steps_done % 50 == 0 or steps_done == 1:
                    print(
                        f"[BC] step {steps_done}/{args.bc_steps} loss={loss.item():.4f}"
                    )
                if steps_done >= args.bc_steps:
                    break
        print("Behavior cloning pretrain complete.")

    try:
        _run_bc_if_requested()
        model.learn(total_timesteps=args.total_timesteps, callback=callbacks)
    finally:
        if mlflow_run and mlflow_client:
            try:
                eval_cb = callbacks[0]
                if (
                    hasattr(eval_cb, "best_mean_reward")
                    and getattr(eval_cb, "best_mean_reward", None) is not None
                ):
                    mlflow_client.log_metric(
                        "best_mean_reward", eval_cb.best_mean_reward
                    )
                if os.path.exists(args.model_out):
                    try:
                        mlflow_client.log_artifact(args.model_out)
                    except Exception as e:
                        print(
                            f"MLflow artifact log failed ({e}); skipped model artifact."
                        )
                if os.path.isdir(args.log_dir):
                    mlflow_client.log_artifacts(args.log_dir, artifact_path="logs")
                mlflow_client.end_run()
            except Exception as e:
                print(f"MLflow logging failed ({e}); run not recorded.")

    os.makedirs(os.path.dirname(args.model_out), exist_ok=True)
    model_save_ok = False
    try:
        model.save(args.model_out)
        model_save_ok = True
        print(f"Saved PPO model to {args.model_out}")
    except Exception as e:
        print(f"Model save failed (likely due to TorchScript components): {e}")

    # Always try to emit a state_dict fallback so videos / reloads can work.
    state_payload = {
        "policy_state_dict": model.policy.state_dict(),
        "adapter_state_dict": (
            adapter_spec.adapter.state_dict() if adapter_spec.adapter else None
        ),
        "pre_ts_adapter_state_dict": (
            adapter_spec.pre_adapter.state_dict() if adapter_spec.pre_adapter else None
        ),
        "torchscript_path": args.torchscript_path,
        "adapter_mode": args.adapter_mode,
        "obs_dim": obs_dim,
    }
    try:
        torch.save(state_payload, args.state_dict_out)
        print(f"Saved policy state_dict fallback to {args.state_dict_out}")
    except Exception as e:
        print(f"Failed to save state_dict fallback: {e}")

    if args.render_after > 0:
        print(f"Rendering {args.render_after} steps with the trained policy...")
        obs = eval_env.reset()
        for _ in range(args.render_after):
            action, _ = model.predict(obs, deterministic=True)
            obs, _, dones, _ = eval_env.step(action)
            if render_mode:
                eval_env.render()
            if dones.any():
                obs = eval_env.reset()

    if args.post_train_video:
        try:
            import moviepy  # noqa: F401
        except Exception:
            print(
                "MoviePy not installed; skipping post-training video. Install with `pip install moviepy`."
            )
        else:
            os.makedirs(args.video_folder, exist_ok=True)
            wrapper_for_video = None
            if args.adapter_mode == "obs" and pretrained is not None:
                wrapper_for_video = make_obs_wrapper(
                    pretrained, adapter_spec, target_obs_dim=obs_dim
                )

            video_env = make_vec_env(
                env_id=args.env_id,
                n_envs=1,
                seed=args.seed + 1234,
                monitor_dir=None,
                env_kwargs={"render_mode": "rgb_array"},
                wrapper_class=wrapper_for_video,
            )
            video_env = VecVideoRecorder(
                video_env,
                args.video_folder,
                record_video_trigger=lambda step: step == 0,
                video_length=args.video_length,
                name_prefix="mujoco-posttrain",
            )
            obs = video_env.reset()
            for _ in range(args.video_length):
                action, _ = model.predict(obs, deterministic=True)
                obs, _, dones, _ = video_env.step(action)
                if dones.any():
                    obs = video_env.reset()
            video_env.close()
            print(f"Saved post-training video to {args.video_folder}")


if __name__ == "__main__":
    main()
