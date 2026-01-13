"""Optiq API clients for communication with web and infra services.

This module provides the official API for communicating with optiq-web and optiq-infra
services via JSON HTTP APIs. All communication must respect the defined schemas.
"""

from .schemas import (
    # Enums
    ModelType,
    TrainingType,
    JobStatus,
    MetricType,
    # Schemas
    TrainingConfig,
    TrainingJobRequest,
    TrainingJobResponse,
    JobStatusResponse,
    JobMetricsHistory,
    ModelInfo,
    ModelListResponse,
    ModelArtifactResponse,
    AnimationRequest,
    AnimationResponse,
    APIError,
    HealthStatus,
    ServiceConfig,
    # Validation
    validate_training_config,
    validate_model_compatibility,
)

from .clients import (
    OptiqClient,
    OptiqWebClient,
    OptiqInfraClient,
    get_client,
    close_client,
    APIException,
)

__all__ = [
    # Enums
    "ModelType",
    "TrainingType",
    "JobStatus",
    "MetricType",
    # Schemas
    "TrainingConfig",
    "TrainingJobRequest",
    "TrainingJobResponse",
    "JobStatusResponse",
    "JobMetricsHistory",
    "ModelInfo",
    "ModelListResponse",
    "ModelArtifactResponse",
    "AnimationRequest",
    "AnimationResponse",
    "APIError",
    "HealthStatus",
    "ServiceConfig",
    # Clients
    "OptiqClient",
    "OptiqWebClient",
    "OptiqInfraClient",
    "get_client",
    "close_client",
    "APIException",
    # Validation
    "validate_training_config",
    "validate_model_compatibility",
]
