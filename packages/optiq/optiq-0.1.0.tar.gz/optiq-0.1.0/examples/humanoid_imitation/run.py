import os
import sys
import json
import yaml
import argparse
import subprocess
import torch
import trimesh
from pathlib import Path
from torch import nn
from torch.utils.data import DataLoader

# Ensure src is in path
sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "src")
)

from optiq.data.frame_sequence import FrameSequence
from optiq.rl.fbx_dataset import FBXDataSet

try:
    from examples.fbx_capoeira.extract_motion import generate_mock_data
except ImportError:

    def generate_mock_data(out_path: str):
        # Minimal mock: single bone spinning in place
        frames = 30
        bones = {"hip": []}
        for i in range(frames):
            bones["hip"].append({"position": [0, 0, 0], "quaternion": [0, 0, 0, 1]})
        with open(out_path, "w") as f:
            json.dump({"bones": bones, "fps": 30}, f)


def _run_node_extract(fbx_path: Path, out_json: Path, fps: int = 30):
    project_root = Path(__file__).resolve().parents[2]
    extract_script = project_root / "scripts" / "extract_fbx_anim.js"
    if not extract_script.exists():
        raise FileNotFoundError(f"Extraction script not found at {extract_script}")
    cmd = ["node", str(extract_script), str(fbx_path), str(out_json), f"--fps={fps}"]
    print(f"Executing: {' '.join(cmd)}")
    subprocess.check_call(cmd)


class TinyAutoencoder(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 256, bottleneck: int = 128):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, bottleneck),
            nn.ReLU(),
        )
        self.decoder = nn.Sequential(
            nn.Linear(bottleneck, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, input_dim),
        )

    def forward(self, x):
        z = self.encoder(x)
        out = self.decoder(z)
        return out

    def encode(self, x):
        return self.encoder(x)


def _fit_autoencoder(
    json_path: Path, epochs: int = 5, batch_size: int = 64, lr: float = 1e-3
):
    ds = FBXDataSet(str(json_path))
    input_dim = ds[0][0].numel()
    model = TinyAutoencoder(input_dim=input_dim)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loader = DataLoader(ds, batch_size=batch_size, shuffle=True)
    model.train()
    for _ in range(epochs):
        for x, _ in loader:
            opt.zero_grad()
            recon = model(x)
            loss = nn.functional.mse_loss(recon, x)
            loss.backward()
            opt.step()
    return model, input_dim


def _export_torchscript_encoder(model: TinyAutoencoder, input_dim: int, out_path: Path):
    model.eval()
    example = torch.zeros(1, input_dim)
    scripted = torch.jit.trace(model.encoder, example)
    scripted.save(str(out_path))
    return out_path


def _launch_ppo(
    scripted_encoder: Path, mode: str, input_dim: int, total_timesteps: int = 100000
):
    trainer = Path(__file__).parent / "train_mujoco.py"
    cmd = [
        sys.executable,
        str(trainer),
        "--torchscript-path",
        str(scripted_encoder),
        "--adapter-mode",
        mode,
        "--total-timesteps",
        str(total_timesteps),
        "--torchscript-in-dim",
        str(input_dim),
    ]
    subprocess.check_call(cmd)


def main():
    parser = argparse.ArgumentParser(
        description="Humanoid pipeline: FBX extract, pretrain, viz, optional PPO bootstrap."
    )
    parser.add_argument(
        "--fbx", default="Walking.fbx", help="FBX file name under this folder."
    )
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--skip-viz", action="store_true")
    parser.add_argument(
        "--ppo-bootstrap",
        action="store_true",
        help="Run Mujoco PPO bootstrap with TorchScript encoder.",
    )
    parser.add_argument(
        "--ppo-mode",
        choices=["obs", "feature"],
        default="obs",
        help="How to apply the TorchScript encoder.",
    )
    parser.add_argument("--ppo-steps", type=int, default=100000)
    parser.add_argument("--ae-epochs", type=int, default=5)
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    fbx_path = os.path.join(base_dir, args.fbx)
    gt_path = os.path.join(data_dir, "ground_truth.json")
    gt_parquet_path = os.path.join(data_dir, "ground_truth.parquet")
    results_path = os.path.join(data_dir, "results.json")
    config_path = os.path.join(base_dir, "config.yaml")

    print("--- Step 1: Ingest Animation Data ---")
    if os.path.exists(fbx_path):
        print(f"Found {fbx_path}, extracting using Node script...")
        try:
            _run_node_extract(Path(fbx_path), Path(gt_path), fps=args.fps)
            print("Extraction complete.")
        except Exception as e:
            print(f"Extraction failed: {e}. Using mock data.")
            generate_mock_data(gt_path)
    else:
        print(f"{fbx_path} not found. Generating mock walking data.")
        generate_mock_data(gt_path)

    # Verify data
    with open(gt_path, "r") as f:
        data = json.load(f)
    # Canonical Parquet export for downstream loaders
    try:
        seq = FrameSequence.from_json(gt_path, compute_velocities=True)
        seq.to_parquet(gt_parquet_path, compression="snappy")
        dataset_path = gt_parquet_path
    except Exception as e:
        print(f"Parquet export failed ({e}); continuing with JSON path.")
        dataset_path = gt_path

    # Handle new structure from Node script
    # Use only skeleton bones (no mesh objects) for physics verification.
    if "bones" in data:
        bone_names = list(data["bones"].keys())
    else:
        bone_names = list(data.keys())

    print(f"Loaded {len(bone_names)} bones from ground truth.")

    print("--- Step 1.5: Configure Simulation ---")
    # Ensure a base config exists before loading
    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            yaml.dump(
                {
                    "objects": [],
                    "global_settings": {"dt": 0.033, "gravity": [0, 0, -9.81]},
                    "training": {
                        "batch_size": 16,
                        "learning_rate": 1e-3,
                        "max_epochs": 5,  # Short for demo
                    },
                },
                f,
            )

    # Load base config template
    with open(config_path, "r") as f:
        config_data = yaml.safe_load(f) or {}

    # Check for exported meshes (from Node script)
    # The node script exports to "exported_objects" relative to CWD
    # We want to find matches for our objects
    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    export_dir = os.path.join(project_root, "exported_objects")

    new_objects = []
    # Prepare a small sphere mesh to represent each bone in physics sim
    sphere_mesh_path = os.path.join(data_dir, "bone_sphere.obj")
    if not os.path.exists(sphere_mesh_path):
        sphere = trimesh.creation.icosphere(radius=0.05)
        sphere.export(sphere_mesh_path)

    for name in bone_names:
        new_objects.append(
            {
                "name": name,
                "mesh_path": sphere_mesh_path,
                "is_static": False,
                "initial_transform": [
                    [1, 0, 0, 0],
                    [0, 1, 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1],
                ],
            }
        )

    config_data["objects"] = new_objects

    # Write updated config
    with open(config_path, "w") as f:
        yaml.dump(config_data, f)
    print(f"Updated config with {len(new_objects)} physical objects.")

    print("--- Step 2: Train Kinematic Prior (Bootstrapping) ---")
    # We train the ConditionalAutoreg model to learn the motion manifold.
    # This model can later be used to generate reference motions or act as a high-level planner.

    # Create a simple config if not exists
    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            yaml.dump(
                {
                    "objects": [],
                    "global_settings": {"dt": 0.033, "gravity": [0, 0, -9.81]},
                    "training": {
                        "batch_size": 16,
                        "learning_rate": 1e-3,
                        "max_epochs": 5,  # Short for demo
                    },
                },
                f,
            )

    # Train
    cmd = [
        sys.executable,
        "-m",
        "optiq.cli",
        "train",
        "--config",
        config_path,
        "--output",
        results_path,
        "--data",
        gt_path,
    ]
    print("Running optiq training...")
    subprocess.check_call(cmd)

    print("--- Step 3: Visualize Results (Plotly) ---")
    if args.skip_viz:
        print("Skipping visualization (per flag).")
    else:
        try:
            with open(results_path, "r") as f:
                res_data = json.load(f)
            physics_traj = res_data.get("physics_verification", {})
            with open(gt_path, "r") as f:
                orig_gt_full = json.load(f)
            if "bones" in orig_gt_full:
                physics_traj = orig_gt_full["bones"]

            if physics_traj:
                frames = 0
                if physics_traj:
                    first_key = list(physics_traj.keys())[0]
                    frames = len(physics_traj[first_key])

                mapping = {
                    "Beta_Surface": "mixamorigHips",
                    "Beta_Joints": "mixamorigSpine",
                }
                with open(gt_path, "r") as f:
                    orig_gt = json.load(f)
                gt_bone_names = []
                if isinstance(orig_gt.get("bone_names"), list):
                    gt_bone_names = orig_gt["bone_names"]
                elif "bones" in orig_gt:
                    gt_bone_names = list(orig_gt["bones"].keys())

                mapped_traj = {}
                mapped_names = []
                for src_name, seq in physics_traj.items():
                    tgt = mapping.get(src_name, src_name)
                    if gt_bone_names and tgt not in gt_bone_names:
                        continue
                    mapped_traj[tgt] = seq
                    mapped_names.append(tgt)

                if not mapped_traj:
                    for src_name, seq in physics_traj.items():
                        tgt = mapping.get(src_name, src_name)
                        mapped_traj[tgt] = seq
                        mapped_names.append(tgt)

                pred_anim = {
                    "fps": 30,
                    "frames": frames,
                    "bones": mapped_traj,
                    "bone_names": mapped_names,
                }
                pred_anim_path = os.path.join(data_dir, "prediction_anim.json")
                with open(pred_anim_path, "w") as f:
                    json.dump(pred_anim, f)

                pred_map_path = os.path.join(data_dir, "prediction_bone_map.json")
                with open(pred_map_path, "w") as f:
                    json.dump({"bone_names": pred_anim["bone_names"]}, f)

                gt_anim_data = {"fps": 30, "frames": 0, "bones": {}, "bone_names": []}
                with open(gt_path, "r") as f:
                    orig_gt = json.load(f)
                pred_keys = set(mapped_names)
                if "bones" in orig_gt:
                    intersection = (
                        pred_keys.intersection(orig_gt["bones"].keys())
                        if pred_keys
                        else set(orig_gt["bones"].keys())
                    )
                    use_all = not intersection
                    for bone_name, bone_data in orig_gt["bones"].items():
                        if use_all or bone_name in pred_keys or not pred_keys:
                            gt_anim_data["bones"][bone_name] = bone_data
                            gt_anim_data["bone_names"].append(bone_name)
                            if gt_anim_data["frames"] == 0 and len(bone_data) > 0:
                                gt_anim_data["frames"] = len(bone_data)

                gt_anim_path = os.path.join(data_dir, "ground_truth_anim.json")
                with open(gt_anim_path, "w") as f:
                    json.dump(gt_anim_data, f)
                gt_map_path = os.path.join(data_dir, "ground_truth_bone_map.json")
                with open(gt_map_path, "w") as f:
                    json.dump({"bone_names": gt_anim_data["bone_names"]}, f)

                project_root = os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                )
                plotly_script = os.path.join(project_root, "scripts", "plotly_anim.py")
                cmd_viz = [
                    "uv",
                    "run",
                    "--with",
                    "plotly",
                    "--with",
                    "trimesh",
                    "--with",
                    "numpy",
                    "python",
                    plotly_script,
                    pred_anim_path,
                    "--gt",
                    gt_anim_path,
                    "--out",
                    os.path.join(data_dir, "comparison.html"),
                    "--tubes",
                ]
                print(f"Generating animation: {' '.join(cmd_viz)}")
                subprocess.check_call(cmd_viz)
                print(f"Animation saved to {os.path.join(data_dir, 'comparison.html')}")
            else:
                print(
                    "No physics verification data found in results.json. Skipping visualization."
                )
        except Exception as e:
            print(f"Visualization failed: {e}")

    if args.ppo_bootstrap:
        print("--- Step 4: Mujoco PPO bootstrap with TorchScript encoder ---")
        ae, in_dim = _fit_autoencoder(Path(dataset_path), epochs=args.ae_epochs)
        ts_path = Path(data_dir) / "fbx_encoder.ts"
        _export_torchscript_encoder(ae, in_dim, ts_path)
        _launch_ppo(
            ts_path,
            mode=args.ppo_mode,
            input_dim=in_dim,
            total_timesteps=args.ppo_steps,
        )

    print("\n" + "=" * 50)
    print("DONE! Infrastructure ready.")
    print("=" * 50)


if __name__ == "__main__":
    main()
