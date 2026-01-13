"""
Example: render Plotly animation from prediction + ground truth.

Usage:
    uv run python examples/viz_plotly.py \
        --pred extracted_jogging/jogging_anim.json \
        --gt extracted_jogging/jogging_anim.json \
        --out /tmp/anim.html
"""

import argparse
from pathlib import Path

from optiq.vis import render_animation


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pred", required=True, help="Prediction JSON path.")
    parser.add_argument("--gt", default=None, help="Optional ground truth JSON path.")
    parser.add_argument("--out", required=True, help="Output HTML path.")
    parser.add_argument("--edges", default=None, help="Optional YAML edge list.")
    parser.add_argument(
        "--no-tubes", action="store_true", help="Disable tube rendering."
    )
    args = parser.parse_args()

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    render_animation(
        pred_path=args.pred,
        gt_path=args.gt,
        out_path=args.out,
        edges_path=args.edges,
        use_tubes=not args.no_tubes,
        title="optiq animation",
    )
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
