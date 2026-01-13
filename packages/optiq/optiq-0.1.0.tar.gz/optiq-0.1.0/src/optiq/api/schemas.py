"""API schemas for optiq communication with web and infra packages.

All communication between optiq, optiq-web, and optiq-infra must respect these schemas.
Communication happens via JSON over HTTP APIs.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from enum import Enum


# ============================================================================
# Common Types
# ============================================================================


class ModelType(str, Enum):
    """Supported model types."""

    CNN = "cnn"
    TRANSFORMER = "transformer"
    UNET1D = "unet1d"
    UNET_AUTOREG = "unet_autoreg"
    CONDITIONAL_AUTOREG = "conditional_autoreg"
    CUSTOM = "custom"


class TrainingType(str, Enum):
    """Supported training types."""

    NEXT = "next"  # Next-frame prediction
    CONDITIONAL = "conditional"  # Conditional autoregressive
    CUSTOM = "custom"  # Custom training runner


class JobStatus(str, Enum):
    """Training job status."""

    PENDING = "pending"
    TRAINING = "training"
    COMPLETED = "completed"
    FAILED = "failed"


class MetricType(str, Enum):
    """Supported metric types for tracking."""

    LOSS = "loss"
    ACCURACY = "accuracy"
    F1_SCORE = "f1_score"
    PRECISION = "precision"
    RECALL = "recall"
    CUSTOM = "custom"


# ============================================================================
# Training Job Schemas
# ============================================================================


class TrainingConfig(BaseModel):
    """Configuration for training a model."""

    json_path: Optional[str] = Field(None, description="Path to JSON dataset file")
    runner_path: Optional[str] = Field(
        None, description="Path to custom training runner"
    )
    pairs: Optional[List[List[str]]] = Field(
        None, description="Data pairs for conditional training"
    )

    class Config:
        json_encoders = {str: str}


class TrainingJobRequest(BaseModel):
    """Request to start a training job."""

    name: str = Field(..., description="Human-readable job name")
    model_type: ModelType = Field(..., description="Type of model to train")
    training_type: TrainingType = Field(..., description="Type of training to perform")

    # Training parameters
    epochs: int = Field(25, description="Number of training epochs", ge=1)
    batch_size: int = Field(32, description="Batch size for training", ge=1)
    learning_rate: float = Field(1e-3, description="Learning rate", gt=0)
    hidden_dim: int = Field(64, description="Hidden dimension size", ge=1)
    layers: int = Field(3, description="Number of layers", ge=1)
    checkpoint_every: int = Field(0, description="Save checkpoint every N epochs", ge=0)

    # Data configuration
    config: TrainingConfig = Field(..., description="Training data configuration")

    # Metrics to track
    metrics: List[str] = Field(
        default_factory=lambda: ["train_loss"], description="Metrics to track"
    )

    class Config:
        use_enum_values = True


class TrainingJobResponse(BaseModel):
    """Response when training job is submitted."""

    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Initial job status")
    message: str = Field(..., description="Response message")

    class Config:
        use_enum_values = True


class JobStatusResponse(BaseModel):
    """Response for job status queries."""

    job_id: str = Field(..., description="Job identifier")
    name: str = Field(..., description="Job name")
    status: JobStatus = Field(..., description="Current job status")
    progress: float = Field(..., description="Training progress (0-100)", ge=0, le=100)
    model_type: ModelType = Field(..., description="Model type")
    training_type: TrainingType = Field(..., description="Training type")

    # Training metrics
    epochs: Optional[int] = Field(None, description="Total epochs")
    current_epoch: Optional[int] = Field(None, description="Current epoch")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Current metrics")

    # Timestamps
    created_at: str = Field(..., description="Job creation timestamp")
    started_at: Optional[str] = Field(None, description="Job start timestamp")
    completed_at: Optional[str] = Field(None, description="Job completion timestamp")

    # Logs and artifacts
    logs: str = Field("", description="Training logs")
    artifacts: List[str] = Field(
        default_factory=list, description="Available artifacts"
    )

    class Config:
        use_enum_values = True


class JobMetricsHistory(BaseModel):
    """Historical metrics for a job."""

    job_id: str = Field(..., description="Job identifier")
    metrics: Dict[str, List[Dict[str, Union[int, float]]]] = Field(
        default_factory=dict,
        description="Metrics history as list of {step, value} dicts",
    )


# ============================================================================
# Model Management Schemas
# ============================================================================


class ModelInfo(BaseModel):
    """Information about a trained model."""

    id: str = Field(..., description="Model identifier")
    name: str = Field(..., description="Model name")
    model_type: ModelType = Field(..., description="Type of model")
    training_type: TrainingType = Field(..., description="Type of training")
    status: JobStatus = Field(..., description="Training status")
    created_at: str = Field(..., description="Creation timestamp")
    epochs: Optional[int] = Field(None, description="Training epochs")
    progress: float = Field(0, description="Training progress", ge=0, le=100)

    class Config:
        use_enum_values = True


class ModelListResponse(BaseModel):
    """Response for listing models."""

    models: List[ModelInfo] = Field(default_factory=list, description="List of models")
    total: int = Field(..., description="Total number of models")


class ModelArtifactResponse(BaseModel):
    """Response for downloading model artifacts."""

    job_id: str = Field(..., description="Job identifier")
    artifact_name: str = Field(..., description="Artifact name")
    content_type: str = Field(..., description="Content type")
    data: bytes = Field(..., description="Artifact data")


# ============================================================================
# Animation/Generation Schemas
# ============================================================================


class AnimationRequest(BaseModel):
    """Request to generate animation from a trained model."""

    model_id: str = Field(..., description="Model to use for generation")
    steps: int = Field(60, description="Number of animation steps", ge=1)
    class_label: Optional[int] = Field(
        None, description="Class label for conditional models"
    )
    seed_data: Optional[List[List[List[float]]]] = Field(
        None, description="Initial seed data [frames x joints x coords]"
    )

    class Config:
        json_encoders = {
            bytes: lambda v: v.decode("utf-8") if isinstance(v, bytes) else str(v)
        }


class AnimationFrame(BaseModel):
    """Single animation frame."""

    frame_number: int = Field(..., description="Frame number")
    joints: List[List[float]] = Field(..., description="Joint positions [joint][x,y,z]")

    class Config:
        json_encoders = {float: lambda x: round(x, 6) if abs(x) < 1e6 else x}


class AnimationResponse(BaseModel):
    """Response containing generated animation."""

    model_id: str = Field(..., description="Model used for generation")
    frames: List[AnimationFrame] = Field(
        default_factory=list, description="Animation frames"
    )
    fps: int = Field(30, description="Frames per second")
    duration: float = Field(..., description="Animation duration in seconds")


# ============================================================================
# Error Schemas
# ============================================================================


class APIError(BaseModel):
    """API error response."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional error details"
    )


# ============================================================================
# Health Check Schemas
# ============================================================================


class HealthStatus(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status: 'healthy', 'unhealthy'")
    version: str = Field(..., description="Service version")
    uptime: Optional[float] = Field(None, description="Service uptime in seconds")
    services: Dict[str, str] = Field(
        default_factory=dict, description="Status of dependent services"
    )


# ============================================================================
# Configuration Schemas
# ============================================================================


class ServiceConfig(BaseModel):
    """Configuration for service endpoints."""

    web_url: str = Field("http://localhost:8000", description="Web service base URL")
    infra_url: str = Field(
        "http://localhost:8001", description="Infra service base URL"
    )
    timeout: int = Field(30, description="Request timeout in seconds")
    retries: int = Field(3, description="Number of retries for failed requests")


# ============================================================================
# Validation Helpers
# ============================================================================


def validate_training_config(
    config: TrainingConfig, training_type: TrainingType
) -> bool:
    """Validate training configuration for the given training type."""
    if training_type == TrainingType.NEXT:
        return config.json_path is not None
    elif training_type == TrainingType.CONDITIONAL:
        return config.pairs is not None or config.json_path is not None
    elif training_type == TrainingType.CUSTOM:
        return config.runner_path is not None
    return False


def validate_model_compatibility(
    model_type: ModelType, training_type: TrainingType
) -> bool:
    """Validate that model type is compatible with training type."""
    compatible_combinations = {
        TrainingType.NEXT: [ModelType.CNN],
        TrainingType.CONDITIONAL: [ModelType.CONDITIONAL_AUTOREG],
        TrainingType.CUSTOM: [ModelType.CUSTOM],
    }
    return model_type in compatible_combinations.get(training_type, [])
