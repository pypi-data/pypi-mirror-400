"""API clients for optiq communication with web and infra packages.

These clients handle all communication via JSON HTTP APIs, respecting the defined schemas.
"""

import httpx
import json
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import time
from urllib.parse import urljoin

from .schemas import (
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
    JobStatus,
    ModelType,
    TrainingType,
)


class OptiqAPIClient:
    """Base client for optiq API communication."""

    def __init__(self, config: ServiceConfig):
        self.config = config
        self.client = httpx.Client(timeout=config.timeout, follow_redirects=True)

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling and retries."""
        url = urljoin(
            self.config.web_url if "web" in endpoint else self.config.infra_url,
            endpoint,
        )

        for attempt in range(self.config.retries + 1):
            try:
                response = self.client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 500 and attempt < self.config.retries:
                    time.sleep(2**attempt)  # Exponential backoff
                    continue
                error_data = (
                    e.response.json()
                    if e.response.headers.get("content-type") == "application/json"
                    else {}
                )
                raise APIException(
                    f"HTTP {e.response.status_code}: {e.response.text}",
                    status_code=e.response.status_code,
                    error_data=error_data,
                )
            except (httpx.ConnectError, httpx.TimeoutException) as e:
                if attempt < self.config.retries:
                    time.sleep(2**attempt)
                    continue
                raise APIException(f"Connection error: {e}")

        raise APIException("Max retries exceeded")

    def close(self):
        """Close the HTTP client."""
        self.client.close()


class OptiqWebClient(OptiqAPIClient):
    """Client for communicating with optiq-web service."""

    def __init__(self, config: ServiceConfig):
        super().__init__(config)

    # ============================================================================
    # Training Job Management
    # ============================================================================

    def submit_training_job(self, request: TrainingJobRequest) -> TrainingJobResponse:
        """Submit a training job to the web service."""
        data = request.dict()
        response_data = self._make_request("POST", "/models/train", json=data)
        return TrainingJobResponse(**response_data)

    def get_job_status(self, job_id: str) -> JobStatusResponse:
        """Get status of a training job."""
        response_data = self._make_request("GET", f"/api/models/{job_id}/status")
        return JobStatusResponse(**response_data)

    def get_job_metrics_history(self, job_id: str) -> JobMetricsHistory:
        """Get historical metrics for a training job."""
        response_data = self._make_request("GET", f"/api/models/{job_id}/metrics")
        return JobMetricsHistory(**response_data)

    def retry_training_job(self, job_id: str) -> TrainingJobResponse:
        """Retry a failed training job."""
        response_data = self._make_request("POST", f"/models/{job_id}/retry")
        return TrainingJobResponse(**response_data)

    # ============================================================================
    # Model Management
    # ============================================================================

    def list_models(self, limit: int = 50, offset: int = 0) -> ModelListResponse:
        """List available trained models."""
        response_data = self._make_request(
            "GET", f"/api/models?limit={limit}&offset={offset}"
        )
        return ModelListResponse(**response_data)

    def get_model_info(self, model_id: str) -> ModelInfo:
        """Get information about a specific model."""
        response_data = self._make_request("GET", f"/api/models/{model_id}")
        return ModelInfo(**response_data)

    def download_model_artifact(
        self, model_id: str, artifact_name: str
    ) -> ModelArtifactResponse:
        """Download a model artifact."""
        response = self.client.get(
            urljoin(
                self.config.web_url, f"/api/models/{model_id}/artifacts/{artifact_name}"
            )
        )
        response.raise_for_status()

        return ModelArtifactResponse(
            job_id=model_id,
            artifact_name=artifact_name,
            content_type=response.headers.get(
                "content-type", "application/octet-stream"
            ),
            data=response.content,
        )

    # ============================================================================
    # Animation Generation
    # ============================================================================

    def generate_animation(self, request: AnimationRequest) -> AnimationResponse:
        """Generate animation using a trained model."""
        data = request.dict(exclude_unset=True)
        response_data = self._make_request(
            "POST", f"/api/generate/{request.model_id}", json=data
        )
        return AnimationResponse(**response_data)

    # ============================================================================
    # Health and Status
    # ============================================================================

    def health_check(self) -> HealthStatus:
        """Check health status of web service."""
        response_data = self._make_request("GET", "/api/health")
        return HealthStatus(**response_data)

    def get_service_info(self) -> Dict[str, Any]:
        """Get service information."""
        return self._make_request("GET", "/api/info")


class OptiqInfraClient(OptiqAPIClient):
    """Client for communicating with optiq-infra service."""

    def __init__(self, config: ServiceConfig):
        super().__init__(config)

    # ============================================================================
    # Worker Management
    # ============================================================================

    def get_worker_status(self) -> Dict[str, Any]:
        """Get status of worker service."""
        return self._make_request("GET", "/api/worker/status")

    def get_worker_metrics(self) -> Dict[str, Any]:
        """Get worker performance metrics."""
        return self._make_request("GET", "/api/worker/metrics")

    # ============================================================================
    # Job Queue Management
    # ============================================================================

    def get_queue_status(self) -> Dict[str, Any]:
        """Get status of job queue."""
        return self._make_request("GET", "/api/queue/status")

    def cancel_job(self, job_id: str) -> Dict[str, Any]:
        """Cancel a running job."""
        return self._make_request("POST", f"/api/jobs/{job_id}/cancel")

    def get_active_jobs(self) -> List[Dict[str, Any]]:
        """Get list of currently active jobs."""
        return self._make_request("GET", "/api/jobs/active")

    # ============================================================================
    # Resource Management
    # ============================================================================

    def get_system_resources(self) -> Dict[str, Any]:
        """Get system resource usage."""
        return self._make_request("GET", "/api/system/resources")

    # ============================================================================
    # Health and Status
    # ============================================================================

    def health_check(self) -> HealthStatus:
        """Check health status of infra service."""
        response_data = self._make_request("GET", "/api/health")
        return HealthStatus(**response_data)

    def get_service_info(self) -> Dict[str, Any]:
        """Get service information."""
        return self._make_request("GET", "/api/info")


class OptiqClient:
    """Unified client for accessing both web and infra services."""

    def __init__(self, config: Optional[ServiceConfig] = None):
        if config is None:
            config = ServiceConfig()
        self.config = config
        self.web = OptiqWebClient(config)
        self.infra = OptiqInfraClient(config)

    def close(self):
        """Close all client connections."""
        self.web.close()
        self.infra.close()

    # ============================================================================
    # High-level convenience methods
    # ============================================================================

    def train_model(self, **kwargs) -> TrainingJobResponse:
        """Convenience method to train a model."""
        request = TrainingJobRequest(**kwargs)
        return self.web.submit_training_job(request)

    def get_model_status(self, job_id: str) -> JobStatusResponse:
        """Convenience method to get model training status."""
        return self.web.get_job_status(job_id)

    def generate_from_model(self, model_id: str, **kwargs) -> AnimationResponse:
        """Convenience method to generate animation from a model."""
        request = AnimationRequest(model_id=model_id, **kwargs)
        return self.web.generate_animation(request)

    def list_available_models(self) -> List[ModelInfo]:
        """Convenience method to list available models."""
        response = self.web.list_models()
        return response.models

    def wait_for_completion(
        self, job_id: str, timeout: int = 3600
    ) -> JobStatusResponse:
        """Wait for a job to complete."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = self.get_model_status(job_id)
            if status.status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                return status
            time.sleep(5)  # Poll every 5 seconds
        raise TimeoutError(f"Job {job_id} did not complete within {timeout} seconds")

    # ============================================================================
    # Context manager support
    # ============================================================================

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class APIException(Exception):
    """Exception raised for API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        error_data: Optional[Dict] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.error_data = error_data or {}


# ============================================================================
# Default client instance
# ============================================================================

_default_config = ServiceConfig()
_default_client = None


def get_client(config: Optional[ServiceConfig] = None) -> OptiqClient:
    """Get the default optiq client instance."""
    global _default_client
    if _default_client is None or config is not None:
        if config is None:
            config = _default_config
        _default_client = OptiqClient(config)
    return _default_client


def close_client():
    """Close the default client."""
    global _default_client
    if _default_client is not None:
        _default_client.close()
        _default_client = None
