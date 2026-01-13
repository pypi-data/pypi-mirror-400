from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, Optional, Sequence, Tuple, Union

import numpy as np
import torch
from torch.utils.data import Dataset

from .frame_sequence import FrameSequence, LabeledSequence, load_sequence


class NextStepDataset(Dataset):
    """Single-step next-state prediction dataset with optional conditioning."""

    def __init__(self, seq: LabeledSequence, horizon: int = 1):
        self.seq = seq
        self.horizon = horizon
        self.frames = seq.frames  # (T, F)
        self.labels = seq.labels

    def __len__(self) -> int:
        return max(0, self.frames.shape[0] - self.horizon)

    def __getitem__(
        self, idx: int
    ) -> Tuple[torch.Tensor, torch.Tensor, Optional[torch.Tensor]]:
        x = self.frames[idx]
        y = self.frames[idx + self.horizon]
        cond = None
        if self.labels is not None:
            cond = self.labels[idx]
        return (
            torch.tensor(x, dtype=torch.float32),
            torch.tensor(y, dtype=torch.float32),
            torch.tensor(cond, dtype=torch.float32) if cond is not None else None,
        )


class RandomHorizonDataset(Dataset):
    """
    Dataset that randomly samples frame pairs with variable time gaps.

    This helps the model learn to predict frames at different temporal distances,
    making it more robust during autoregressive rollout.

    Args:
        seq: LabeledSequence with frames
        min_horizon: Minimum frame gap (default: 1)
        max_horizon: Maximum frame gap (default: 5)
        noise_std: Optional noise to add to input frames for robustness
    """

    def __init__(
        self,
        seq: LabeledSequence,
        min_horizon: int = 1,
        max_horizon: int = 5,
        noise_std: float = 0.0,
    ):
        self.seq = seq
        self.frames = seq.frames  # (T, F)
        self.labels = seq.labels
        self.min_horizon = min_horizon
        self.max_horizon = max_horizon
        self.noise_std = noise_std

    def __len__(self) -> int:
        return max(0, self.frames.shape[0] - self.max_horizon)

    def __getitem__(
        self, idx: int
    ) -> Tuple[torch.Tensor, torch.Tensor, Optional[torch.Tensor]]:
        # Randomly sample horizon
        horizon = np.random.randint(self.min_horizon, self.max_horizon + 1)

        x = self.frames[idx].copy()
        y = self.frames[idx + horizon]

        # Add noise to input for robustness
        if self.noise_std > 0:
            x = x + np.random.randn(*x.shape) * self.noise_std

        cond = None
        if self.labels is not None:
            cond = self.labels[idx]

        return (
            torch.tensor(x, dtype=torch.float32),
            torch.tensor(y, dtype=torch.float32),
            torch.tensor(cond, dtype=torch.float32) if cond is not None else None,
        )


class MultiStepDataset(Dataset):
    """
    Dataset for multi-step prediction training.

    Returns sequences of (input, [target1, target2, ..., targetN]) where the model
    should predict multiple future frames. This trains the model to maintain
    coherence over longer horizons.

    Args:
        seq: LabeledSequence with frames
        num_steps: Number of future steps to predict
        noise_std: Optional noise to add to inputs
    """

    def __init__(
        self,
        seq: LabeledSequence,
        num_steps: int = 5,
        noise_std: float = 0.0,
    ):
        self.seq = seq
        self.frames = seq.frames  # (T, F)
        self.labels = seq.labels
        self.num_steps = num_steps
        self.noise_std = noise_std

    def __len__(self) -> int:
        return max(0, self.frames.shape[0] - self.num_steps)

    def __getitem__(
        self, idx: int
    ) -> Tuple[torch.Tensor, torch.Tensor, Optional[torch.Tensor]]:
        x = self.frames[idx].copy()

        # Get sequence of targets
        targets = self.frames[idx + 1 : idx + 1 + self.num_steps]

        # Add noise to input
        if self.noise_std > 0:
            x = x + np.random.randn(*x.shape) * self.noise_std

        cond = None
        if self.labels is not None:
            cond = self.labels[idx]

        return (
            torch.tensor(x, dtype=torch.float32),
            torch.tensor(targets, dtype=torch.float32),  # (num_steps, F)
            torch.tensor(cond, dtype=torch.float32) if cond is not None else None,
        )


class RolloutDataset(Dataset):
    """
    Dataset for autoregressive rollout training with scheduled sampling.

    Each sample returns (input_frame, sequence_of_targets) where:
    - input_frame: A single frame from the sequence
    - sequence_of_targets: The next `rollout_len` consecutive frames

    The dataset randomly samples starting positions from the sequence,
    allowing you to control the epoch size independently from the data.

    Args:
        seq: LabeledSequence with frames
        rollout_len: Number of future frames to include (default: 10)
        size: Number of samples per epoch (default: 1000)
              Set this to control how many random samples per epoch.
        input_noise_std: Noise to add to the input frame (default: 0.0)
    """

    def __init__(
        self,
        seq: LabeledSequence,
        rollout_len: int = 10,
        size: int = 1000,
        input_noise_std: float = 0.0,
    ):
        self.seq = seq
        self.frames = seq.frames  # (T, F)
        self.labels = seq.labels
        self.rollout_len = rollout_len
        self.size = size
        self.input_noise_std = input_noise_std

        # Calculate valid range for starting indices
        # Need at least rollout_len + 1 frames (1 input + rollout_len targets)
        self.max_start = max(0, self.frames.shape[0] - rollout_len - 1)

        if self.max_start < 0:
            raise ValueError(
                f"Sequence too short ({self.frames.shape[0]} frames) for rollout_len={rollout_len}. "
                f"Need at least {rollout_len + 1} frames."
            )

    def __len__(self) -> int:
        return self.size

    def __getitem__(
        self, idx: int
    ) -> Tuple[torch.Tensor, torch.Tensor, Optional[torch.Tensor]]:
        # Randomly sample a starting position (ignores idx for randomness)
        start = np.random.randint(0, self.max_start + 1)

        # Input is the starting frame
        x = self.frames[start].copy()
        if self.input_noise_std > 0:
            x = x + np.random.randn(*x.shape) * self.input_noise_std

        # Targets are the next rollout_len frames
        targets = self.frames[start + 1 : start + 1 + self.rollout_len].copy()

        cond = None
        if self.labels is not None:
            cond = self.labels[start]

        return (
            torch.tensor(x, dtype=torch.float32),
            torch.tensor(targets, dtype=torch.float32),  # (rollout_len, F)
            torch.tensor(cond, dtype=torch.float32) if cond is not None else None,
        )


class AutoregressiveDataset(Dataset):
    """Chunked sequence dataset for autoregressive training."""

    def __init__(self, seq: LabeledSequence, chunk_len: int, stride: int = 1):
        self.seq = seq
        self.chunk_len = chunk_len
        self.stride = stride
        self.frames = seq.frames  # (T, F)
        self.labels = seq.labels

    def __len__(self) -> int:
        if self.frames.shape[0] < self.chunk_len:
            return 0
        return 1 + (self.frames.shape[0] - self.chunk_len) // self.stride

    def __getitem__(
        self, idx: int
    ) -> Tuple[torch.Tensor, torch.Tensor, Optional[torch.Tensor]]:
        start = idx * self.stride
        end = start + self.chunk_len
        chunk = self.frames[start:end]  # (chunk_len, F)
        # Predict the next chunk (shift by one)
        target = self.frames[start + 1 : end + 1]
        if target.shape[0] < chunk.shape[0]:
            # Pad target with last frame
            pad = np.repeat(
                target[-1][None, :], chunk.shape[0] - target.shape[0], axis=0
            )
            target = np.concatenate([target, pad], axis=0)
        cond = None
        if self.labels is not None:
            cond = self.labels[start:end]
        return (
            torch.tensor(chunk, dtype=torch.float32),
            torch.tensor(target, dtype=torch.float32),
            torch.tensor(cond, dtype=torch.float32) if cond is not None else None,
        )


class BehaviorCloneDataset(Dataset):
    """
    Generalized behavior cloning dataset using a retargeting function to map
    raw bone transforms to environment qpos/qvel -> (obs, action).

    The retarget_fn should accept a dict[bone_name] -> {position, quaternion}
    for a single frame and return qpos (np.ndarray). The action_fn maps
    (qpos_t, qpos_tp1, dt, action_scale) -> action vector.
    """

    def __init__(
        self,
        seq: FrameSequence,
        env_id: str,
        retarget_fn: Callable[[Dict[str, Dict]], np.ndarray],
        action_fn: Optional[
            Callable[[np.ndarray, np.ndarray, float, np.ndarray], np.ndarray]
        ] = None,
        dt: Optional[float] = None,
        device: str = "cpu",
    ):
        try:
            import gymnasium as gym  # noqa: F401
        except Exception as e:  # pragma: no cover - optional dep
            raise ImportError(
                "gymnasium is required for BehaviorCloneDataset. Install optiq[rl]."
            ) from e

        self.seq = seq
        self.env_id = env_id
        self.retarget_fn = retarget_fn
        self.action_fn = action_fn or self._default_action_fn
        self.dt = float(dt) if dt is not None else 1.0 / float(seq.fps)
        self.device = device

        bones = seq.raw_bones
        if bones is None:
            # Reconstruct bone dicts from flat frames (positions + quaternions)
            bones = {name: [] for name in seq.bone_names}
            feat_per_bone = 7  # 3 pos + 4 quat
            if seq.frames.shape[1] != len(seq.bone_names) * feat_per_bone:
                raise ValueError(
                    "Cannot reconstruct bones without raw_bones and positional/quaternion layout."
                )
            for frame in seq.frames:
                for i, name in enumerate(seq.bone_names):
                    start = i * feat_per_bone
                    bones[name].append(
                        {
                            "position": frame[start : start + 3].tolist(),
                            "quaternion": frame[start + 3 : start + 7].tolist(),
                        }
                    )

        # Build qpos per frame
        bone_names = seq.bone_names
        frames = len(next(iter(bones.values())))
        qpos_list = []
        for t in range(frames):
            frame_dict = {b: bones[b][t] for b in bone_names}
            qpos_list.append(self.retarget_fn(frame_dict))
        self.qpos = qpos_list
        self.frames = frames

        import gymnasium as gym

        env = gym.make(env_id)
        self.obs_template_env = env
        self.action_scale = env.action_space.high

        self.observations: Sequence[np.ndarray] = []
        self.actions: Sequence[np.ndarray] = []

        for t in range(frames - 1):
            qpos_t = self.qpos[t]
            qpos_tp1 = self.qpos[t + 1]
            qvel_t = (qpos_tp1 - qpos_t) / self.dt

            env.unwrapped.set_state(qpos_t, qvel_t)
            obs = env.unwrapped._get_obs()
            self.observations.append(np.asarray(obs, dtype=np.float32))

            act = self.action_fn(qpos_t, qpos_tp1, self.dt, self.action_scale)
            self.actions.append(act.astype(np.float32))

        env.close()

        self.observations = torch.tensor(
            np.stack(self.observations, axis=0), dtype=torch.float32
        )
        self.actions = torch.tensor(np.stack(self.actions, axis=0), dtype=torch.float32)

    @staticmethod
    def _default_action_fn(
        qpos_t: np.ndarray, qpos_tp1: np.ndarray, dt: float, action_scale
    ) -> np.ndarray:
        delta = (qpos_tp1 - qpos_t) / dt
        return np.clip(delta / action_scale, -1.0, 1.0)

    def __len__(self) -> int:
        return self.observations.shape[0]

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.observations[idx], self.actions[idx]


def _slice_sequence(seq: FrameSequence, mask: Optional[np.ndarray]) -> FrameSequence:
    """Apply a boolean mask to frames/labels/velocities/raw_bones."""
    if mask is None:
        return seq
    mask = np.asarray(mask, dtype=bool)
    if mask.shape[0] != seq.frames.shape[0]:
        raise ValueError("Split mask length must match number of frames.")
    frames = seq.frames[mask]
    velocities = seq.velocities[mask] if seq.velocities is not None else None
    labels = seq.labels[mask] if seq.labels is not None else None
    raw_bones = None
    if seq.raw_bones is not None:
        raw_bones = {
            name: [f for f, keep in zip(frames_list, mask) if keep]
            for name, frames_list in seq.raw_bones.items()
        }
    splits = None
    if seq.splits:
        splits = {k: v[mask] for k, v in seq.splits.items()}
    return FrameSequence(
        fps=seq.fps,
        bone_names=seq.bone_names,
        frames=frames,
        velocities=velocities,
        labels=labels,
        label_names=seq.label_names,
        seq_labels=seq.seq_labels,
        metadata=seq.metadata,
        splits=splits,
        raw_bones=raw_bones,
    )


def build_imitation_dataset(
    path_or_seq: Union[str, FrameSequence],
    split: Optional[str] = None,
    horizon: int = 1,
    mode: str = "next",
    chunk_len: int = 32,
    stride: int = 1,
) -> Dataset:
    """
    Build an imitation dataset from Parquet/HDF5/JSON sequence.

    mode: "next" -> NextStepDataset, "autoregressive" -> AutoregressiveDataset.
    """
    seq = (
        load_sequence(path_or_seq)
        if isinstance(path_or_seq, (str, Path))
        else path_or_seq
    )
    mask = None
    if split and seq.splits and split in seq.splits:
        mask = seq.splits[split]
    seq_masked = _slice_sequence(seq, mask)
    labeled = seq_masked.with_labels(
        seq_masked.labels, seq_masked.seq_labels, label_names=seq_masked.label_names
    )
    if mode == "autoregressive":
        return AutoregressiveDataset(labeled, chunk_len=chunk_len, stride=stride)
    return NextStepDataset(labeled, horizon=horizon)


def build_bc_dataset(
    path_or_seq: Union[str, FrameSequence],
    env_id: str,
    retarget_fn: Optional[Callable[[Dict[str, Dict]], np.ndarray]] = None,
    action_fn: Optional[
        Callable[[np.ndarray, np.ndarray, float, np.ndarray], np.ndarray]
    ] = None,
    dt: Optional[float] = None,
    split: Optional[str] = None,
) -> BehaviorCloneDataset:
    """
    Create a behavior cloning dataset from a stored sequence.

    retarget_fn should map per-frame bone dict -> qpos for the target env.
    """
    seq = (
        load_sequence(path_or_seq)
        if isinstance(path_or_seq, (str, Path))
        else path_or_seq
    )
    mask = None
    if split and seq.splits and split in seq.splits:
        mask = seq.splits[split]
    seq_masked = _slice_sequence(seq, mask)
    if retarget_fn is None:
        try:
            from optiq.rl.humanoid_mapping import HumanoidRetarget  # local import
        except Exception as e:  # pragma: no cover - optional path
            raise ImportError(
                "HumanoidRetarget is required when retarget_fn is not provided."
            ) from e

        humanoid = HumanoidRetarget(
            scale=1.0
        )  # Data is already in meters (standardized at extraction time)
        retarget_fn = humanoid.frame_to_qpos
        action_fn = action_fn or humanoid.qpos_delta_to_action

    return BehaviorCloneDataset(
        seq=seq_masked,
        env_id=env_id,
        retarget_fn=retarget_fn,
        action_fn=action_fn,
        dt=dt,
    )
