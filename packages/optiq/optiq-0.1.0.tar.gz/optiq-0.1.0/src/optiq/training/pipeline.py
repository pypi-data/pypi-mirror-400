from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import torch
import torch.nn as nn

# Optional physics stack (may be absent in minimal installs)
try:
    # Import physics components
    from optiq.physics.pybullet_adapter import PyBulletAdapter  # type: ignore

    # Placeholder imports for future neurophysinverse module
    SceneGraph = None  # type: ignore
    InverseTrainer = None  # type: ignore
    NeuralPhysicsInstance = None  # type: ignore
    TrainingMode = None  # type: ignore

    HAS_PHYSICS = True
except Exception:
    SceneGraph = None
    InverseTrainer = None
    NeuralPhysicsInstance = None
    PyBulletAdapter = None
    TrainingMode = None
    HAS_PHYSICS = False

# RL Imports
try:
    import gymnasium as gym
    from stable_baselines3 import PPO, SAC, A2C, TD3, DQN
    from stable_baselines3.common.env_util import make_vec_env
    from stable_baselines3.common.torch_layers import BaseFeaturesExtractor

    from optiq.utils.env_loader import load_environment
    from optiq.utils.class_loader import load_class_from_file

    HAS_SB3 = True
except Exception:
    HAS_SB3 = False


def create_adapted_policy(user_policy_class, observation_space, action_space):
    """
    Creates a FeaturesExtractor class that wraps the user policy network.
    Automatically adds linear layers if dimensions mismatch.
    """

    class AdaptedFeaturesExtractor(BaseFeaturesExtractor):
        def __init__(self, observation_space: gym.spaces.Box, features_dim: int = 256):
            super().__init__(observation_space, features_dim)

            obs_dim = observation_space.shape[0]

            try:
                self.user_model = user_policy_class(input_dim=obs_dim)
            except TypeError:
                try:
                    self.user_model = user_policy_class()
                except TypeError as e:
                    raise ValueError(
                        f"Could not instantiate custom policy {user_policy_class.__name__}: {e}"
                    )

            self.input_adapter = nn.Identity()

            expected_in = obs_dim
            for _, module in self.user_model.named_modules():
                if isinstance(module, nn.Linear):
                    expected_in = module.in_features
                    break

            if expected_in != obs_dim:
                self.input_adapter = nn.Linear(obs_dim, expected_in)

            with torch.no_grad():
                dummy_input = torch.zeros(1, obs_dim)
                adapted_input = self.input_adapter(dummy_input)
                output = self.user_model(adapted_input)
                out_dim = output.shape[1]

            self._features_dim = out_dim

        def forward(self, observations):
            x = self.input_adapter(observations)
            return self.user_model(x)

    return AdaptedFeaturesExtractor


def run_rl_training(scene: SceneGraph, output_path: str):
    if not HAS_SB3:
        raise ImportError(
            "Stable Baselines3 is required for RL training. Install with 'pip install stable-baselines3'."
        )

    rl_settings = scene.config.global_settings.rl_settings
    if not rl_settings:
        raise ValueError("RL Settings not found in config.")

    print(
        f"Starting RL Training with {rl_settings.algorithm} on {rl_settings.environment}..."
    )

    def env_factory():
        return load_environment(rl_settings.environment)

    env = make_vec_env(env_factory, n_envs=1)

    policy_kwargs: Dict[str, Any] = {}
    if rl_settings.custom_policy_path:
        print(
            f"Loading custom policy architecture from {rl_settings.custom_policy_path}..."
        )
        user_policy_class = load_class_from_file(
            rl_settings.custom_policy_path, base_class=nn.Module
        )

        class WrappedFeaturesExtractor(BaseFeaturesExtractor):
            def __init__(
                self, observation_space: gym.spaces.Box, features_dim: int = 256
            ):
                super().__init__(observation_space, features_dim)

                obs_dim = observation_space.shape[0]

                try:
                    self.user_model = user_policy_class(input_dim=obs_dim)
                except TypeError:
                    try:
                        self.user_model = user_policy_class()
                    except TypeError as e:
                        raise ValueError(
                            f"Could not instantiate {user_policy_class.__name__}: {e}"
                        )

                self.input_adapter = nn.Identity()
                expected_in = obs_dim
                found_linear = False
                for _, module in self.user_model.named_modules():
                    if isinstance(module, nn.Linear):
                        expected_in = module.in_features
                        found_linear = True
                        break

                if found_linear and expected_in != obs_dim:
                    self.input_adapter = nn.Linear(obs_dim, expected_in)

                with torch.no_grad():
                    dummy = torch.zeros(1, obs_dim)
                    out = self.user_model(self.input_adapter(dummy))
                    self._features_dim = out.shape[1]

            def forward(self, observations):
                return self.user_model(self.input_adapter(observations))

        policy_kwargs["features_extractor_class"] = WrappedFeaturesExtractor

    algos = {
        "PPO": PPO,
        "SAC": SAC,
        "A2C": A2C,
        "TD3": TD3,
        "DQN": DQN,
    }

    algo_class = algos.get(rl_settings.algorithm.upper())
    if not algo_class:
        raise ValueError(f"Unknown algorithm: {rl_settings.algorithm}")

    device_cfg = scene.config.global_settings.device
    if device_cfg == "cuda" and torch.cuda.is_available():
        device = "cuda"
    elif device_cfg == "mps" and torch.backends.mps.is_available():
        device = "mps"
    elif device_cfg == "cpu":
        device = "cpu"
    else:
        device = "auto"

    model = algo_class(
        "MlpPolicy",
        env,
        verbose=1,
        device=device,
        learning_rate=rl_settings.learning_rate,
        policy_kwargs=policy_kwargs,
    )

    if rl_settings.load_model_path:
        if os.path.exists(rl_settings.load_model_path):
            print(f"Loading pre-trained model from {rl_settings.load_model_path}...")
            model = algo_class.load(rl_settings.load_model_path, env=env, device=device)
        else:
            print(
                f"Warning: Pre-trained model not found at {rl_settings.load_model_path}. Training from scratch."
            )

    if rl_settings.total_timesteps > 0:
        print(f"Training for {rl_settings.total_timesteps} timesteps...")
        model.learn(total_timesteps=rl_settings.total_timesteps)
    else:
        print("Skipping training (total_timesteps=0). Using loaded model for rollout.")

    model_path = output_path.replace(".json", ".zip")
    model.save(model_path)
    print(f"Model saved to {model_path}")

    print("Running evaluation rollout...")
    obs = env.reset()
    trajectory = []
    scene_history: Dict[str, List[Any]] = {}

    max_steps = int(
        scene.config.global_settings.simulation_duration
        / scene.config.global_settings.dt
    )
    if max_steps <= 0:
        max_steps = 1000

    for i in range(max_steps):
        action, _states = model.predict(obs, deterministic=True)
        obs, rewards, dones, info = env.step(action)

        try:
            full_states = env.env_method("get_full_state")
            current_state = full_states[0]
            for obj_name, obj_state in current_state.items():
                scene_history.setdefault(obj_name, []).append(obj_state)
        except Exception:
            pass

        trajectory.append(
            {
                "step": i,
                "observation": obs.tolist(),
                "action": action.tolist(),
                "reward": float(rewards[0]),
            }
        )

        if dones[0]:
            break

    output_data = {
        "rl_rollout": trajectory,
        "model_path": model_path,
        "trajectories": scene_history,
    }

    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)


def run_training_pipeline(
    config_path: str, output_path: str, data_path: Optional[str] = None
):
    if not HAS_PHYSICS:
        # Graceful fallback: write a stub results file and return.
        stub = {
            "prediction": {},
            "ground_truth": {},
            "physics_verification": {},
            "warning": "Physics training pipeline unavailable: neurophysinverse components are not installed.",
        }
        with open(output_path, "w") as f:
            json.dump(stub, f, indent=2)
        print(stub["warning"])
        return

    scene = SceneGraph(config_path)  # type: ignore

    if scene.config.global_settings.training_mode == TrainingMode.RL:  # type: ignore
        run_rl_training(scene, output_path)
        return

    if data_path:
        with open(data_path, "r") as f:
            raw_data = json.load(f)
        if "bones" in raw_data:
            trajectories = raw_data["bones"]
            if "objects" in raw_data:
                trajectories.update(raw_data["objects"])
        else:
            trajectories = raw_data
    else:
        print("Generating Ground Truth from Simulation...")
        engine = PyBulletAdapter()  # type: ignore
        duration = scene.config.global_settings.simulation_duration
        trajectories = engine.generate_ground_truth(scene, duration)

    custom_net_path = scene.config.global_settings.custom_network_path
    trainer = InverseTrainer(scene, trajectories, custom_network_path=custom_net_path)  # type: ignore

    phases = scene.config.global_settings.dg_pinn_phases
    pretrain_epochs = phases.get("pretrain_epochs", 100)
    finetune_epochs = phases.get("finetune_epochs", 500)

    print(f"--- Phase 1: Kinematic Pre-training ({pretrain_epochs} epochs) ---")
    trainer.train_kinematics(epochs=pretrain_epochs)

    print(f"--- Phase 2: Physics Identification ({finetune_epochs} epochs) ---")
    trainer.train_physics(epochs=finetune_epochs)

    results: Dict[str, Dict[str, Any]] = {}
    for name, instance in trainer.instances.items():
        learned_params = {
            n: instance.obj.get_parameter(n).item() for n in instance.param_names
        }
        results[name] = {"learned_parameters": learned_params}

    print("Running Physics Verification Simulation...")
    for name, instance in trainer.instances.items():
        learned_params = {
            n: instance.obj.get_parameter(n).item() for n in instance.param_names
        }
        for param_name, value in learned_params.items():
            if param_name in instance.obj.params:
                instance.obj.params[param_name].data = torch.tensor(
                    value, device=scene.device
                )

    verify_engine = PyBulletAdapter()  # type: ignore
    duration = scene.config.global_settings.simulation_duration
    physics_verify_trajectories = verify_engine.generate_ground_truth(scene, duration)

    output_data = {
        "prediction": results,
        "ground_truth": trajectories,
        "physics_verification": physics_verify_trajectories,
    }

    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"Results saved to {output_path}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Kindr Training (Supervised & RL)")
    parser.add_argument("--config", required=True, help="Path to config.yaml")
    parser.add_argument("--output", required=True, help="Path to output results.json")
    parser.add_argument(
        "--data",
        required=False,
        help="Path to external ground truth data (Supervised only)",
    )

    args = parser.parse_args()

    run_training_pipeline(args.config, args.output, args.data)


if __name__ == "__main__":
    main()
