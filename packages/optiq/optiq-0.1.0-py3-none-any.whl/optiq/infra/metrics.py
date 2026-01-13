from __future__ import annotations

from typing import Dict, Optional


def setup_mlflow(tracking_uri: Optional[str] = None, experiment: Optional[str] = None):
    try:
        import mlflow
    except Exception:
        return None
    if tracking_uri:
        try:
            mlflow.set_tracking_uri(tracking_uri)
        except Exception:
            pass
    if experiment:
        try:
            mlflow.set_experiment(experiment)
        except Exception:
            pass
    return mlflow if "mlflow" in locals() else None


def log_params_safe(params: Dict):
    try:
        import mlflow
    except Exception:
        return
    try:
        mlflow.log_params(params)
    except Exception:
        return


def log_metrics_safe(metrics: Dict, step: Optional[int] = None):
    try:
        import mlflow
    except Exception:
        return
    try:
        mlflow.log_metrics(metrics, step=step)
    except Exception:
        return
