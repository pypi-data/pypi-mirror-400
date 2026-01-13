import json
from typing import Dict, List, Tuple, Optional, Union

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

BONE_EDGES: List[Tuple[str, str]] = [
    ("mixamorigHips", "mixamorigSpine"),
    ("mixamorigSpine", "mixamorigSpine1"),
    ("mixamorigSpine1", "mixamorigSpine2"),
    ("mixamorigSpine2", "mixamorigNeck"),
    ("mixamorigNeck", "mixamorigHead"),
    ("mixamorigSpine2", "mixamorigLeftShoulder"),
    ("mixamorigLeftShoulder", "mixamorigLeftArm"),
    ("mixamorigLeftArm", "mixamorigLeftForeArm"),
    ("mixamorigLeftForeArm", "mixamorigLeftHand"),
    ("mixamorigSpine2", "mixamorigRightShoulder"),
    ("mixamorigRightShoulder", "mixamorigRightArm"),
    ("mixamorigRightArm", "mixamorigRightForeArm"),
    ("mixamorigRightForeArm", "mixamorigRightHand"),
    ("mixamorigHips", "mixamorigLeftUpLeg"),
    ("mixamorigLeftUpLeg", "mixamorigLeftLeg"),
    ("mixamorigLeftLeg", "mixamorigLeftFoot"),
    ("mixamorigLeftFoot", "mixamorigLeftToeBase"),
    ("mixamorigHips", "mixamorigRightUpLeg"),
    ("mixamorigRightUpLeg", "mixamorigRightLeg"),
    ("mixamorigRightLeg", "mixamorigRightFoot"),
    ("mixamorigRightFoot", "mixamorigRightToeBase"),
]


def load_anim(path: str):
    with open(path, "r") as f:
        data = json.load(f)
    bones: Dict[str, List[Dict]] = data["bones"]
    fps = data.get("fps", 30)
    frames = data["frames"]
    # Preserve provided bone order if it covers all bones; otherwise fall back to all bones present.
    bone_names = data.get("bone_names") or []
    if not bone_names or len(bone_names) < len(bones):
        # Use the order stored in the dict; JSON preserves insertion order.
        bone_names = list(bones.keys())

    positions: List[Dict[str, Tuple[float, float, float]]] = []
    for frame_idx in range(frames):
        positions.append(
            {name: tuple(bones[name][frame_idx]["position"]) for name in bone_names}
        )
    return fps, bone_names, positions


def load_edges(path: Optional[str]) -> Optional[List[Tuple[str, str]]]:
    if not path:
        return None
    try:
        import yaml
    except Exception as e:  # pragma: no cover
        raise ImportError("pyyaml is required to load edge lists") from e
    with open(path, "r") as f:
        data = yaml.safe_load(f) or []
    edges: List[Tuple[str, str]] = []
    for item in data:
        if isinstance(item, (list, tuple)) and len(item) == 2:
            edges.append((item[0], item[1]))
    return edges or None


def _cylinder_mesh(
    p0, p1, radius=1.5, segments=12, color="orange", name="edge", opacity=0.35
):
    p0 = np.array(p0, dtype=float)
    p1 = np.array(p1, dtype=float)
    axis = p1 - p0
    length = np.linalg.norm(axis)
    if length < 1e-6:
        # degenerate; draw a small sphere-like point cloud
        axis = np.array([0, 0, 1.0])
        length = 1e-3
    axis = axis / length
    # find a perpendicular vector
    perp = np.cross(axis, np.array([1, 0, 0]))
    if np.linalg.norm(perp) < 1e-3:
        perp = np.cross(axis, np.array([0, 1, 0]))
    perp = perp / np.linalg.norm(perp)
    # build orthonormal basis
    b1 = perp
    b2 = np.cross(axis, b1)

    angles = np.linspace(0, 2 * np.pi, segments, endpoint=False)
    circle = np.array(
        [radius * (np.cos(a) * b1 + np.sin(a) * b2) for a in angles]
    )  # (segments, 3)
    top = p1 + circle
    bottom = p0 + circle
    verts = np.vstack([top, bottom])

    # faces
    faces = []
    for i in range(segments):
        j = (i + 1) % segments
        faces.append([i, j, segments + j])
        faces.append([i, segments + j, segments + i])
    faces = np.array(faces)

    return go.Mesh3d(
        x=verts[:, 0],
        y=verts[:, 1],
        z=verts[:, 2],
        i=faces[:, 0],
        j=faces[:, 1],
        k=faces[:, 2],
        opacity=opacity,
        color=color,
        name=name,
        showscale=False,
    )


def frame_traces(
    frame_idx: int,
    bone_names,
    positions,
    gt_positions=None,
    use_tubes=False,
    tube_radius=1.5,
    tube_segments=12,
    edges: Optional[List[Tuple[str, str]]] = None,
):
    xs, ys, zs = zip(*[positions[frame_idx][n] for n in bone_names])
    pred_trace = go.Scatter3d(
        x=xs,
        y=ys,
        z=zs,
        mode="markers",
        marker=dict(
            size=6, color="rgba(65,105,225,0.9)"
        ),  # slightly larger, semi-opaque blue
        name="pred",
    )

    gt_trace = None
    if gt_positions is not None:
        gt_frame = gt_positions[frame_idx]
        gt_points = [gt_frame[n] for n in bone_names if n in gt_frame]
        if gt_points:
            xs_gt, ys_gt, zs_gt = zip(*gt_points)
            gt_trace = go.Scatter3d(
                x=xs_gt,
                y=ys_gt,
                z=zs_gt,
                mode="markers",
                marker=dict(
                    size=5, color="rgba(255,182,193,0.85)"
                ),  # light pink, larger
                name="gt",
            )

    edge_traces = []
    edge_list = edges if edges is not None else BONE_EDGES
    if edge_list:
        for a, b in edge_list:
            if a in positions[frame_idx] and b in positions[frame_idx]:
                xa, ya, za = positions[frame_idx][a]
                xb, yb, zb = positions[frame_idx][b]
                if use_tubes:
                    edge_traces.append(
                        _cylinder_mesh(
                            (xa, ya, za),
                            (xb, yb, zb),
                            radius=tube_radius,
                            segments=tube_segments,
                            color="rgba(70,130,180,0.35)",  # light blue, semi-transparent
                            opacity=0.5,
                            name=f"{a}-{b}",
                        )
                    )
                else:
                    edge_traces.append(
                        go.Scatter3d(
                            x=[xa, xb],
                            y=[ya, yb],
                            z=[za, zb],
                            mode="lines",
                            line=dict(color="rgba(70,130,180,0.6)", width=6),
                            showlegend=False,
                        )
                    )
            # GT edge tubes/lines
            if (
                gt_positions is not None
                and a in gt_positions[frame_idx]
                and b in gt_positions[frame_idx]
            ):
                xa, ya, za = gt_positions[frame_idx][a]
                xb, yb, zb = gt_positions[frame_idx][b]
                if use_tubes:
                    edge_traces.append(
                        _cylinder_mesh(
                            (xa, ya, za),
                            (xb, yb, zb),
                            radius=tube_radius,
                            segments=tube_segments,
                            color="rgba(255,105,180,0.35)",  # pink
                            opacity=0.45,
                            name=f"gt-{a}-{b}",
                        )
                    )
                else:
                    edge_traces.append(
                        go.Scatter3d(
                            x=[xa, xb],
                            y=[ya, yb],
                            z=[za, zb],
                            mode="lines",
                            line=dict(color="rgba(255,105,180,0.6)", width=5),
                            showlegend=False,
                        )
                    )

    return pred_trace, gt_trace, edge_traces


def build_fig(
    fps,
    bone_names,
    positions,
    gt_positions=None,
    repeats: int = 1,
    use_tubes: bool = False,
    tube_radius: float = 0.01,
    tube_segments: int = 12,
    edges: Optional[List[Tuple[str, str]]] = None,
):
    """
    Build a Plotly figure with animation frames.

    Uses a simple approach: each frame contains joint markers + bone lines.
    """
    n_frames = len(positions)
    edge_list = edges if edges is not None else BONE_EDGES

    # Build all animation frames
    fig_frames = []
    for frame_idx in range(n_frames):
        frame_positions = positions[frame_idx]

        # Joint markers
        xs, ys, zs = [], [], []
        for name in bone_names:
            if name in frame_positions:
                pos = frame_positions[name]
                xs.append(pos[0])
                ys.append(pos[1])
                zs.append(pos[2])

        frame_data = [
            go.Scatter3d(
                x=xs,
                y=ys,
                z=zs,
                mode="markers",
                marker=dict(size=5, color="rgba(65,105,225,0.9)"),
                name="joints",
            )
        ]

        # Bone lines
        for parent, child in edge_list:
            if parent in frame_positions and child in frame_positions:
                p1, p2 = frame_positions[parent], frame_positions[child]
                frame_data.append(
                    go.Scatter3d(
                        x=[p1[0], p2[0]],
                        y=[p1[1], p2[1]],
                        z=[p1[2], p2[2]],
                        mode="lines",
                        line=dict(color="rgba(255,165,0,0.8)", width=5),
                        showlegend=False,
                    )
                )

        # GT overlay if provided
        if gt_positions is not None and frame_idx < len(gt_positions):
            gt_frame = gt_positions[frame_idx]
            gt_xs, gt_ys, gt_zs = [], [], []
            for name in bone_names:
                if name in gt_frame:
                    pos = gt_frame[name]
                    gt_xs.append(pos[0])
                    gt_ys.append(pos[1])
                    gt_zs.append(pos[2])
            if gt_xs:
                frame_data.append(
                    go.Scatter3d(
                        x=gt_xs,
                        y=gt_ys,
                        z=gt_zs,
                        mode="markers",
                        marker=dict(size=4, color="rgba(255,105,180,0.7)"),
                        name="gt",
                    )
                )
                for parent, child in edge_list:
                    if parent in gt_frame and child in gt_frame:
                        p1, p2 = gt_frame[parent], gt_frame[child]
                        frame_data.append(
                            go.Scatter3d(
                                x=[p1[0], p2[0]],
                                y=[p1[1], p2[1]],
                                z=[p1[2], p2[2]],
                                mode="lines",
                                line=dict(color="rgba(255,105,180,0.5)", width=3),
                                showlegend=False,
                            )
                        )

        fig_frames.append(go.Frame(data=frame_data, name=str(frame_idx)))

    # Create figure with initial frame data
    fig = go.Figure(data=fig_frames[0].data if fig_frames else [], frames=fig_frames)

    # Frame names for animation controls
    frame_names = [str(i) for i in range(n_frames)]

    fig.update_layout(
        scene=dict(
            aspectmode="data",
            camera=dict(
                up=dict(x=0, y=0, z=1),
                eye=dict(x=2.5, y=-3.0, z=1.5),
                center=dict(x=0, y=0, z=0),
            ),
            xaxis=dict(
                showgrid=False,
                showticklabels=False,
                zeroline=False,
                showbackground=False,
            ),
            yaxis=dict(
                showgrid=False,
                showticklabels=False,
                zeroline=False,
                showbackground=False,
            ),
            zaxis=dict(
                showgrid=False,
                showticklabels=False,
                zeroline=False,
                showbackground=False,
            ),
        ),
        updatemenus=[
            {
                "type": "buttons",
                "showactive": False,
                "buttons": [
                    {
                        "label": "Play",
                        "method": "animate",
                        "args": [
                            None,
                            {
                                "frame": {"duration": 1000 / fps, "redraw": True},
                                "fromcurrent": True,
                                "mode": "immediate",
                            },
                        ],
                    },
                    {
                        "label": "Pause",
                        "method": "animate",
                        "args": [[None], {"mode": "immediate"}],
                    },
                ],
            }
        ],
        sliders=[
            {
                "active": 0,
                "steps": [
                    {
                        "args": [
                            [str(i)],
                            {
                                "frame": {"duration": 0, "redraw": True},
                                "mode": "immediate",
                            },
                        ],
                        "label": str(i),
                        "method": "animate",
                    }
                    for i in range(n_frames)
                ],
                "currentvalue": {"prefix": "Frame: "},
            }
        ],
        margin=dict(l=0, r=0, t=40, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )

    return fig


def render_animation(
    pred_path: Union[str, None],
    out_path: str,
    gt_path: Optional[str] = None,
    edges_path: Optional[str] = None,
    use_tubes: bool = True,
    tube_radius: float = 1.5,
    tube_segments: int = 12,
    title: str = "Animation",
) -> str:
    """
    Render a Plotly HTML comparison between predicted and ground-truth animations.

    Args:
        pred_path: JSON path with bones{bone_name:[{position, quaternion},...]}.
        out_path: Output HTML path.
        gt_path: Optional ground-truth JSON path for side-by-side comparison.
        edges_path: Optional YAML edge list; defaults to built-in Mixamo edges.
        use_tubes: Whether to draw tube meshes instead of line segments.
    """
    if pred_path is None:
        raise ValueError("pred_path is required")
    fps, bone_names, pred_positions = load_anim(pred_path)
    gt_positions = None
    if gt_path:
        fps_gt, gt_bones, gt_positions = load_anim(gt_path)
        # Use intersection to avoid missing bone keys
        if gt_bones:
            common = [b for b in bone_names if b in gt_bones]
            if not common:
                common = gt_bones
            bone_names = common
        fps = min(fps, fps_gt)

    # Filter bone_names to those present in loaded positions dicts
    if bone_names:
        bone_names = [b for b in bone_names if b in pred_positions[0]]
    if gt_positions is not None and bone_names:
        bone_names = [b for b in bone_names if b in gt_positions[0]]

    edges = load_edges(edges_path)
    fig = build_fig(
        fps=fps,
        bone_names=bone_names,
        positions=pred_positions,
        gt_positions=gt_positions,
        repeats=1,
        use_tubes=use_tubes,
        tube_radius=tube_radius,
        tube_segments=tube_segments,
        edges=edges,
    )
    fig.update_layout(title=title)
    fig.write_html(out_path, include_plotlyjs="cdn")
    return out_path
