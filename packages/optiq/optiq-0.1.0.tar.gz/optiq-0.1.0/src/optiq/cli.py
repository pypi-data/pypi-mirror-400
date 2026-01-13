"""
Optiq CLI framework.

Usage:
    optiq data convert --in foo.fbx --out data/seq.parquet
    optiq data label --in data/seq.parquet --label movement=kick
    optiq train model --config configs/model.yaml --arch transformer --out ckpt.pt
    optiq train rl --env Humanoid-v5 --pretrained ckpt.pt --algo ppo --total-steps 3e5
    optiq viz plotly --dataset data/seq.parquet --out viz.html
    optiq viz video --policy sb3.zip --env Humanoid-v5 --out video.mp4
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import click
import yaml
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader

try:
    import pytorch_lightning as pl
except ImportError:
    pl = None

# ---------------------------------------------------------------------------
# Utility: config loading and merging
# ---------------------------------------------------------------------------


def _load_config(config_path: str) -> Dict[str, Any]:
    """Load config from JSON or YAML file."""
    path = Path(config_path)
    if not path.exists():
        raise click.ClickException(f"Config file not found: {config_path}")
    text = path.read_text()
    if path.suffix.lower() in {".yaml", ".yml"}:
        return yaml.safe_load(text) or {}
    return json.loads(text)


def _parse_overrides(overrides: tuple[str, ...]) -> Dict[str, Any]:
    """Parse key=value overrides into a dict with type inference."""
    result: Dict[str, Any] = {}
    for item in overrides:
        if "=" not in item:
            raise click.ClickException(f"Override must be key=value: {item}")
        key, value = item.split("=", 1)
        # Type inference
        if value.lower() in {"true", "false"}:
            result[key] = value.lower() == "true"
        else:
            try:
                result[key] = int(value)
            except ValueError:
                try:
                    result[key] = float(value)
                except ValueError:
                    result[key] = value
    return result


def _set_seed(seed: Optional[int]) -> None:
    """Set random seed for reproducibility."""
    if seed is None:
        return
    import random
    import numpy as np
    import torch

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def _resolve_device(device: str) -> str:
    """Resolve device string, handling 'auto'."""
    import torch

    if device == "auto":
        if torch.cuda.is_available():
            return "cuda"
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
        return "cpu"
    return device


# ---------------------------------------------------------------------------
# Root CLI group
# ---------------------------------------------------------------------------


@click.group()
@click.option("--seed", type=int, default=None, help="Random seed for reproducibility.")
@click.option(
    "--device", type=str, default="auto", help="Device: cpu, cuda, mps, or auto."
)
@click.pass_context
def cli(ctx: click.Context, seed: Optional[int], device: str):
    """Optiq CLI: data processing, model training, RL, and visualization."""
    ctx.ensure_object(dict)
    ctx.obj["seed"] = seed
    ctx.obj["device"] = device
    if seed is not None:
        _set_seed(seed)


# ---------------------------------------------------------------------------
# DATA subgroup (existing implementation)
# ---------------------------------------------------------------------------


try:
    from optiq.data.cli import data_cli as data_group

    cli.add_command(data_group, name="data")
except ImportError as exc:
    error_msg = str(exc)

    @cli.group()
    def data():
        """Data conversion and labeling (optiq[ml] required)."""
        raise click.ClickException(f"Data commands require optiq[ml]: {error_msg}")


# ---------------------------------------------------------------------------
# TRAIN subgroup
# ---------------------------------------------------------------------------


@cli.group()
def train():
    """Training commands for models and RL policies."""
    pass


@train.command("model")
@click.option(
    "--config",
    "config_path",
    required=True,
    help="Path to training config (YAML/JSON).",
)
@click.option(
    "--arch",
    type=click.Choice(["mlp", "transformer", "unet1d", "unet_autoreg"]),
    default=None,
    help="Override model architecture.",
)
@click.option("--out", "out_path", required=True, help="Output checkpoint path (.pt).")
@click.option("--epochs", type=int, default=None, help="Override training epochs.")
@click.option("--batch-size", type=int, default=None, help="Override batch size.")
@click.option("--lr", type=float, default=None, help="Override learning rate.")
@click.option(
    "--override",
    "overrides",
    multiple=True,
    help="Config override key=value (repeatable).",
)
@click.pass_context
def train_model(
    ctx: click.Context,
    config_path: str,
    arch: Optional[str],
    out_path: str,
    epochs: Optional[int],
    batch_size: Optional[int],
    lr: Optional[float],
    overrides: tuple[str, ...],
):
    """Train a model using the model registry (mlp, transformer, unet1d, unet_autoreg)."""
    if pl is None:
        raise click.ClickException(
            "Model training requires pytorch_lightning. Install with: pip install optiq[ml]"
        )

    try:
        from optiq.models.registry import build, available
        from optiq.data.datasets import NextStepDataset
        from optiq.data.frame_sequence import load_sequence
        from optiq.utils.class_loader import load_class_from_file
    except ImportError as e:
        raise click.ClickException(f"Model training requires optiq[ml]: {e}")

    # Load and merge config
    cfg = _load_config(config_path)
    override_dict = _parse_overrides(overrides)
    cfg.update(override_dict)

    # Apply CLI overrides
    if arch:
        cfg["arch"] = arch
    if epochs:
        cfg["epochs"] = epochs
    if batch_size:
        cfg["batch_size"] = batch_size
    if lr:
        cfg["lr"] = lr

    # Defaults
    model_arch = cfg.get("arch", "mlp")
    if model_arch not in available():
        raise click.ClickException(
            f"Unknown architecture '{model_arch}'. Available: {list(available().keys())}"
        )

    device = _resolve_device(ctx.obj.get("device", "auto"))
    click.echo(f"Training {model_arch} model on {device}...")

    # Extract model kwargs from config, dropping training-only keys
    training_keys = {
        "arch",
        "epochs",
        "batch_size",
        "lr",
        "data_path",
        "optimizer",
        "scheduler",
        "grad_clip",
        "dry_run",
        "loss",
        # Dataset/training augmentation keys
        "noise_std",
        "input_noise_std",
        "min_horizon",
        "max_horizon",
        "num_rollout_steps",
        "rollout_len",
        "rollout_stride",
        "dataset_type",
        "random_start",
        "num_samples",
        "dataset_size",
        # Lightning module keys
        "lightning_module",
        "initial_teacher_ratio",
        "final_teacher_ratio",
        "teacher_decay_steps",
        "horizon",
        "velocity_weight",
        # Loss configuration
        "loss_type",
        "num_bones",
        "features_per_bone",
        # Gradient control
        "gradient_steps",
    }
    model_kwargs = {k: v for k, v in cfg.items() if k not in training_keys}

    try:
        model = build(model_arch, **model_kwargs)
        model = model.to(device)
    except Exception as e:
        raise click.ClickException(f"Failed to build model: {e}")

    # ------------------------------------------------------------------
    # Actual training via PyTorch Lightning (configurable LightningModule)
    # ------------------------------------------------------------------
    data_path = cfg.get("data_path")
    if not data_path:
        # Allow a fast dry-run (used in tests) if no data is provided.
        if cfg.get("dry_run", True):
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "config": cfg,
                    "arch": model_arch,
                },
                out_path,
            )
            click.echo(
                f"No data_path provided; dry-run saved initialized model to {out_path}"
            )
            return
        raise click.ClickException(
            "Config must include 'data_path' pointing to a dataset (parquet/hdf5/json)."
        )

    seq = load_sequence(data_path)

    # Choose dataset type based on config
    # Default to "rollout" for scheduled_sampling module, otherwise "next_step"
    lightning_module_name = cfg.get("lightning_module", "")
    default_dataset = (
        "rollout" if "scheduled_sampling" in str(lightning_module_name) else "next_step"
    )
    dataset_type = cfg.get("dataset_type", default_dataset)

    if dataset_type == "rollout":
        from optiq.data import RolloutDataset

        rollout_len = cfg.get("rollout_len", cfg.get("num_rollout_steps", 10))
        dataset_size = cfg.get("dataset_size", 1000)  # Samples per epoch
        train_dataset = RolloutDataset(
            seq,
            rollout_len=rollout_len,
            size=dataset_size,
            input_noise_std=cfg.get("input_noise_std", 0.0),
        )
        click.echo(
            f"Using RolloutDataset: rollout_len={rollout_len}, size={dataset_size} samples/epoch"
        )
    elif dataset_type == "random_horizon":
        from optiq.data import RandomHorizonDataset

        train_dataset = RandomHorizonDataset(
            seq,
            min_horizon=cfg.get("min_horizon", 1),
            max_horizon=cfg.get("max_horizon", 5),
            noise_std=cfg.get("noise_std", 0.0),
        )
    elif dataset_type == "multi_step":
        from optiq.data import MultiStepDataset

        train_dataset = MultiStepDataset(
            seq,
            num_steps=cfg.get("num_rollout_steps", 5),
            noise_std=cfg.get("noise_std", 0.0),
        )
    else:
        train_dataset = NextStepDataset(seq, horizon=cfg.get("horizon", 1))

    if len(train_dataset) == 0:
        raise click.ClickException(
            "Dataset is empty or shorter than horizon; cannot train."
        )

    batch_size = cfg.get("batch_size", 32)
    target_dim = cfg.get("input_dim", None)

    def _adjust_feat(t: torch.Tensor, target: int) -> torch.Tensor:
        if target is None:
            return t
        if t.shape[-1] > target:
            return t[..., :target]
        if t.shape[-1] < target:
            pad = torch.zeros(*t.shape[:-1], target - t.shape[-1], dtype=t.dtype)
            return torch.cat([t, pad], dim=-1)
        return t

    def _collate_with_optional_cond(batch):
        xs, ys, conds = zip(*batch)
        xs = torch.stack([_adjust_feat(x, target_dim) for x in xs])

        # Handle both single-step (B, F) and multi-step (B, T, F) targets
        if ys[0].dim() == 1:
            # Single-step: (F,) -> stack to (B, F)
            ys = torch.stack([_adjust_feat(y, target_dim) for y in ys])
        else:
            # Multi-step: (T, F) -> stack to (B, T, F)
            # Adjust feature dim for each timestep
            adjusted_ys = []
            for y in ys:
                if target_dim is not None:
                    # y is (T, F), adjust each timestep
                    adjusted = torch.stack(
                        [_adjust_feat(y[t], target_dim) for t in range(y.shape[0])]
                    )
                else:
                    adjusted = y
                adjusted_ys.append(adjusted)
            ys = torch.stack(adjusted_ys)

        cond_non_null = [c for c in conds if c is not None]
        if cond_non_null:
            # Fill missing conds with zeros of the same shape as first non-null
            template = cond_non_null[0]
            filled = [c if c is not None else torch.zeros_like(template) for c in conds]
            cond_batch = torch.stack(filled)
        else:
            cond_batch = None
        return xs, ys, cond_batch

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        collate_fn=_collate_with_optional_cond,
    )

    # LightningModule selection: built-in, custom file, or default
    lightning_module_name = cfg.get("lightning_module")
    lr = cfg.get("lr", 1e-3)

    if lightning_module_name:
        # Check for built-in modules first
        builtin_modules = {
            "optiq.lightning_modules.ScheduledSamplingLitModule": "scheduled_sampling",
            "optiq.lightning_modules.MultiStepLitModule": "multi_step",
            "optiq.lightning_modules.NextStepLitModule": "next_step",
            "scheduled_sampling": "scheduled_sampling",
            "multi_step": "multi_step",
            "next_step": "next_step",
        }

        module_type = builtin_modules.get(lightning_module_name)

        if module_type == "scheduled_sampling":
            from optiq.lightning_modules import ScheduledSamplingLitModule

            # Determine num_bones from input_dim if possible
            input_dim = cfg.get("input_dim", 455)
            features_per_bone = cfg.get("features_per_bone", 7)
            num_bones = cfg.get("num_bones", input_dim // features_per_bone)

            lightning_model = ScheduledSamplingLitModule(
                model=model,
                lr=lr,
                initial_teacher_ratio=cfg.get("initial_teacher_ratio", 1.0),
                final_teacher_ratio=cfg.get("final_teacher_ratio", 0.0),
                decay_steps=cfg.get("teacher_decay_steps", 10000),
                rollout_steps=cfg.get("rollout_len", cfg.get("num_rollout_steps", 10)),
                noise_std=cfg.get("noise_std", 0.005),
                loss_type=cfg.get("loss_type", "mse"),
                num_bones=num_bones,
                velocity_weight=cfg.get("velocity_weight", 0.1),
                features_per_bone=features_per_bone,
                gradient_steps=cfg.get("gradient_steps", 5),
            )
            loss_type = cfg.get("loss_type", "mse")
            grad_steps = cfg.get("gradient_steps", 5)
            click.echo(
                f"Using ScheduledSamplingLitModule with {loss_type} loss, {grad_steps} gradient steps"
            )
        elif module_type == "multi_step":
            from optiq.lightning_modules import MultiStepLitModule

            lightning_model = MultiStepLitModule(
                model=model,
                lr=lr,
                num_steps=cfg.get("num_rollout_steps", 5),
                noise_std=cfg.get("noise_std", 0.0),
            )
            click.echo("Using MultiStepLitModule for multi-step training")
        elif module_type == "next_step":
            from optiq.lightning_modules import NextStepLitModule

            lightning_model = NextStepLitModule(model=model, lr=lr)
            click.echo("Using NextStepLitModule")
        else:
            # Try loading from file path
            try:
                LitCls = load_class_from_file(
                    lightning_module_name, base_class=pl.LightningModule
                )
            except Exception as e:
                raise click.ClickException(
                    f"Failed to load LightningModule '{lightning_module_name}': {e}"
                )
            try:
                lightning_model = LitCls(model=model, config=cfg)
            except Exception:
                try:
                    lightning_model = LitCls(model)
                except Exception as e:
                    raise click.ClickException(
                        f"Failed to instantiate LightningModule '{lightning_module_name}': {e}"
                    )
    else:
        # Default module
        class DefaultLitModule(pl.LightningModule):
            def __init__(self, model: torch.nn.Module, lr: float = 1e-3):
                super().__init__()
                self.model = model
                self.lr = lr

            def forward(self, x, condition=None):
                return self.model(x, condition=condition)

            def training_step(self, batch, batch_idx):
                x, y, cond = batch
                out = self(x, condition=cond)
                loss = F.mse_loss(out, y)
                self.log("train_loss", loss, prog_bar=True, on_step=True, on_epoch=True)
                return loss

            def configure_optimizers(self):
                return torch.optim.Adam(self.parameters(), lr=self.lr)

        lightning_model = DefaultLitModule(model=model, lr=lr)

    max_epochs = int(cfg.get("epochs", 1))
    trainer = pl.Trainer(
        max_epochs=max_epochs,
        accelerator="auto",
        devices=1,
        enable_checkpointing=False,
        logger=False,
    )
    trainer.fit(lightning_model, train_loader)

    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "config": cfg,
            "arch": model_arch,
        },
        out_path,
    )
    click.echo(f"Trained and saved checkpoint to {out_path}")


@train.command("rl")
@click.option(
    "--env",
    "env_id",
    required=True,
    help="Gymnasium environment ID (e.g., Humanoid-v5).",
)
@click.option(
    "--pretrained", default=None, help="Path to pretrained encoder (.pt TorchScript)."
)
@click.option(
    "--algo",
    type=click.Choice(["ppo", "sac", "a2c", "td3"]),
    default="ppo",
    help="RL algorithm.",
)
@click.option(
    "--total-steps",
    "total_steps",
    type=float,
    default=1e5,
    help="Total training timesteps.",
)
@click.option("--out", "out_path", required=True, help="Output policy path (.zip).")
@click.option(
    "--record-video", is_flag=True, help="Record evaluation videos during training."
)
@click.option("--n-envs", type=int, default=4, help="Number of parallel environments.")
@click.option(
    "--adapter-mode",
    type=click.Choice(["obs", "feature"]),
    default="feature",
    help="How to integrate pretrained encoder.",
)
@click.option(
    "--config",
    "config_path",
    default=None,
    help="Optional config file for RL hyperparameters.",
)
@click.option(
    "--override",
    "overrides",
    multiple=True,
    help="Config override key=value (repeatable).",
)
@click.pass_context
def train_rl(
    ctx: click.Context,
    env_id: str,
    pretrained: Optional[str],
    algo: str,
    total_steps: float,
    out_path: str,
    record_video: bool,
    n_envs: int,
    adapter_mode: str,
    config_path: Optional[str],
    overrides: tuple[str, ...],
):
    """Train an RL policy with optional pretrained encoder integration."""
    try:
        import gymnasium as gym
        from stable_baselines3 import PPO, SAC, A2C, TD3
        from stable_baselines3.common.env_util import make_vec_env
        from stable_baselines3.common.callbacks import EvalCallback
    except ImportError as e:
        raise click.ClickException(f"RL training requires optiq[rl]: {e}")

    import torch

    # Load config if provided
    cfg: Dict[str, Any] = {}
    if config_path:
        cfg = _load_config(config_path)
    cfg.update(_parse_overrides(overrides))

    device = _resolve_device(ctx.obj.get("device", "auto"))
    total_timesteps = int(total_steps)

    click.echo(f"Training {algo.upper()} on {env_id} for {total_timesteps} steps...")
    click.echo(f"Device: {device}, Envs: {n_envs}")

    # Create vectorized environment
    try:
        env = make_vec_env(env_id, n_envs=n_envs)
    except Exception as e:
        raise click.ClickException(f"Failed to create environment '{env_id}': {e}")

    # Algorithm selection
    algo_map = {"ppo": PPO, "sac": SAC, "a2c": A2C, "td3": TD3}
    algo_class = algo_map[algo]

    # Policy kwargs and pretrained integration
    policy_kwargs: Dict[str, Any] = cfg.get("policy_kwargs", {})

    if pretrained:
        click.echo(f"Loading pretrained encoder from {pretrained}...")
        try:
            from optiq.rl.bootstrap import (
                load_pretrained,
                build_adapters,
                make_obs_wrapper,
            )

            obs_dim = env.observation_space.shape[0]
            ts_in_dim = cfg.get("pretrained_in_dim", obs_dim)
            adapter_hidden = cfg.get("adapter_hidden", [])

            pretrained_spec = load_pretrained(
                pretrained, ts_in_dim, adapter_hidden, device=device
            )
            adapter_spec = build_adapters(
                obs_dim, pretrained_spec, adapter_mode, adapter_hidden
            )

            if adapter_mode == "feature" and adapter_spec.features_extractor_class:
                policy_kwargs["features_extractor_class"] = (
                    adapter_spec.features_extractor_class
                )
                click.echo("Integrated pretrained encoder as feature extractor.")
            elif adapter_mode == "obs":
                wrapper_class = make_obs_wrapper(pretrained_spec, adapter_spec, obs_dim)
                env = make_vec_env(env_id, n_envs=n_envs, wrapper_class=wrapper_class)
                click.echo("Integrated pretrained encoder as observation wrapper.")
        except Exception as e:
            raise click.ClickException(f"Failed to load pretrained encoder: {e}")

    # Extract hyperparameters from config
    learning_rate = cfg.get("learning_rate", cfg.get("lr", 3e-4))
    model_kwargs = {
        "policy": "MlpPolicy",
        "env": env,
        "verbose": 1,
        "device": device,
        "learning_rate": learning_rate,
    }
    if policy_kwargs:
        model_kwargs["policy_kwargs"] = policy_kwargs

    # Add algorithm-specific params from config
    for key in ["n_steps", "batch_size", "gamma", "gae_lambda", "ent_coef", "vf_coef"]:
        if key in cfg:
            model_kwargs[key] = cfg[key]

    model = algo_class(**model_kwargs)

    # Setup callbacks
    callbacks = []
    if record_video:
        click.echo("Video recording enabled (evaluation callback).")
        eval_env = make_vec_env(env_id, n_envs=1)
        eval_callback = EvalCallback(
            eval_env,
            best_model_save_path=str(Path(out_path).parent / "eval"),
            log_path=str(Path(out_path).parent / "eval_logs"),
            eval_freq=max(total_timesteps // 10, 1000),
            deterministic=True,
            render=False,
        )
        callbacks.append(eval_callback)

    # Train
    try:
        model.learn(
            total_timesteps=total_timesteps, callback=callbacks if callbacks else None
        )
    except KeyboardInterrupt:
        click.echo("\nTraining interrupted. Saving partial model...")

    # Save
    model.save(out_path)
    click.echo(f"Saved policy to {out_path}")


@train.command("legacy")
@click.option("--config", required=True, help="Path to config.yaml")
@click.option("--output", required=True, help="Path to output results.json")
@click.option("--data", required=False, help="Path to external ground truth data")
def train_legacy(config: str, output: str, data: Optional[str]):
    """Legacy training command (Inverse Dynamics / Physics)."""
    try:
        from optiq.training.pipeline import run_training_pipeline
    except ImportError as e:
        raise click.ClickException(f"Training pipeline not available: {e}")

    run_training_pipeline(config, output, data)


# ---------------------------------------------------------------------------
# VIZ subgroup
# ---------------------------------------------------------------------------


@cli.group()
def viz():
    """Visualization helpers (Plotly, video)."""
    pass


@viz.command("plotly")
@click.option("--pred", "pred_path", default=None, help="Prediction JSON path.")
@click.option(
    "--dataset", "dataset_path", default=None, help="Dataset path (parquet/hdf5)."
)
@click.option("--out", "out_path", required=True, help="Output HTML path.")
@click.option("--gt", "gt_path", default=None, help="Optional ground truth JSON path.")
@click.option("--edges", "edges_path", default=None, help="Optional YAML edge list.")
@click.option("--tubes/--no-tubes", default=True, help="Render tubes instead of lines.")
@click.option("--title", default="Animation", help="Plot title.")
def viz_plotly(
    pred_path: Optional[str],
    dataset_path: Optional[str],
    out_path: str,
    gt_path: Optional[str],
    edges_path: Optional[str],
    tubes: bool,
    title: str,
):
    """Render Plotly animation from predictions or dataset."""
    try:
        from optiq.vis import render_animation
    except ImportError as e:
        raise click.ClickException(f"Visualization requires optiq[viz]: {e}")

    if not pred_path and not dataset_path:
        raise click.ClickException("Provide either --pred or --dataset")

    if dataset_path:
        # Convert dataset to JSON for render_animation
        try:
            from optiq.data import load_sequence

            seq = load_sequence(dataset_path)
            # render_animation expects JSON format
            import tempfile
            import json

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False
            ) as f:
                bones_data = {}
                if seq.raw_bones:
                    bones_data = seq.raw_bones
                else:
                    # Fallback: construct from frames
                    for i, bone in enumerate(seq.bone_names):
                        bones_data[bone] = []
                        for frame_idx in range(seq.frames.shape[0]):
                            frame = seq.frames[frame_idx, i * 7 : (i + 1) * 7]
                            bones_data[bone].append(
                                {
                                    "position": frame[:3].tolist(),
                                    "quaternion": frame[3:7].tolist(),
                                }
                            )
                json.dump({"fps": seq.fps, "bones": bones_data}, f)
                pred_path = f.name
        except Exception as e:
            raise click.ClickException(f"Failed to load dataset: {e}")

    try:
        result = render_animation(
            pred_path=pred_path,
            gt_path=gt_path,
            out_path=out_path,
            edges_path=edges_path,
            use_tubes=tubes,
            title=title,
        )
        click.echo(f"Wrote Plotly animation to {result}")
    except Exception as e:
        raise click.ClickException(str(e))


@viz.command("video")
@click.option("--policy", required=True, help="Path to SB3 policy (.zip).")
@click.option("--env", "env_id", required=True, help="Gymnasium environment id.")
@click.option("--out", "out_path", required=True, help="Output mp4 path.")
@click.option("--steps", default=1000, type=int, help="Rollout steps.")
@click.option("--fps", default=30, type=int, help="Output video fps.")
def viz_video(policy: str, env_id: str, out_path: str, steps: int, fps: int):
    """Render an SB3 policy rollout to MP4 (requires optiq[rl,viz])."""
    try:
        from optiq.vis.video import render_policy_video
    except ImportError as e:
        raise click.ClickException(f"Video rendering requires optiq[rl,viz]: {e}")

    try:
        result = render_policy_video(
            policy, env_id, out_path, steps=steps, render_fps=fps
        )
        click.echo(f"Wrote video to {result}")
    except Exception as e:
        raise click.ClickException(str(e))


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def main():
    """Main entry point for the optiq CLI."""
    cli()


if __name__ == "__main__":
    main()
