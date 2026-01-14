"""
Calaxis Platform API Client

Provides integration with the Calaxis AI Platform for:
- Model upload to registry
- Job status tracking
- Metrics reporting
"""
import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import requests
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class CalaxisAPIClient:
    """
    Client for interacting with Calaxis AI Platform API
    """

    def __init__(
        self,
        api_url: str = None,
        api_key: str = None,
    ):
        """
        Initialize Calaxis API client

        Args:
            api_url: Platform API URL (or set CALAXIS_API_URL env var)
            api_key: API key for authentication (or set CALAXIS_API_KEY env var)
        """
        if not HAS_REQUESTS:
            raise ImportError("requests library is required. Install with: pip install requests")

        self.api_url = api_url or os.environ.get("CALAXIS_API_URL", "https://api.calaxis.ai")
        self.api_key = api_key or os.environ.get("CALAXIS_API_KEY")

        if not self.api_key:
            logger.warning("No API key provided. Some features may be unavailable.")

        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            })

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Make API request

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request body data
            files: Files to upload
            params: Query parameters

        Returns:
            dict: Response data
        """
        url = f"{self.api_url}{endpoint}"

        try:
            if method == "GET":
                response = self.session.get(url, params=params)
            elif method == "POST":
                if files:
                    # Remove Content-Type header for multipart
                    headers = {k: v for k, v in self.session.headers.items() if k != "Content-Type"}
                    response = requests.post(url, files=files, data=data, headers=headers)
                else:
                    response = self.session.post(url, json=data, params=params)
            elif method == "PUT":
                response = self.session.put(url, json=data, params=params)
            elif method == "DELETE":
                response = self.session.delete(url, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise

    # ==================================================================
    # AUTHENTICATION
    # ==================================================================

    def validate_api_key(self) -> bool:
        """
        Validate API key

        Returns:
            bool: True if API key is valid
        """
        try:
            response = self._request("GET", "/api/v1/auth/me")
            return "id" in response
        except:
            return False

    def get_user_info(self) -> Dict[str, Any]:
        """Get current user information"""
        return self._request("GET", "/api/v1/auth/me")

    # ==================================================================
    # MODEL REGISTRY
    # ==================================================================

    def upload_model(
        self,
        model_path: str,
        model_name: str,
        description: str = "",
        tags: Optional[list] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Upload trained model to Calaxis model registry

        Args:
            model_path: Path to model directory or archive
            model_name: Name for the model
            description: Model description
            tags: List of tags
            metadata: Additional metadata

        Returns:
            dict: Upload response with model ID
        """
        logger.info(f"Uploading model: {model_name}")

        # Check if model path exists
        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(f"Model path not found: {model_path}")

        # Prepare metadata
        model_metadata = {
            "name": model_name,
            "description": description,
            "tags": tags or [],
            "metadata": metadata or {},
        }

        # If it's a directory, create a tar.gz archive
        if model_path.is_dir():
            import tarfile
            import tempfile

            archive_path = Path(tempfile.gettempdir()) / f"{model_name}.tar.gz"

            logger.info(f"Creating archive: {archive_path}")
            with tarfile.open(archive_path, "w:gz") as tar:
                tar.add(model_path, arcname=model_name)

            model_file_path = archive_path
        else:
            model_file_path = model_path

        # Upload file
        try:
            with open(model_file_path, "rb") as f:
                files = {"file": (model_file_path.name, f)}
                response = self._request(
                    "POST",
                    "/api/v1/deployment/models/upload",
                    data=model_metadata,
                    files=files,
                )

            logger.info(f"Model uploaded successfully: {response.get('model_id')}")
            return response

        finally:
            # Clean up temp archive
            if model_path.is_dir() and model_file_path.exists():
                os.remove(model_file_path)

    def list_models(self) -> list:
        """List all uploaded models"""
        response = self._request("GET", "/api/v1/deployment/models")
        return response.get("models", [])

    def get_model(self, model_id: str) -> Dict[str, Any]:
        """Get model details"""
        return self._request("GET", f"/api/v1/deployment/models/{model_id}")

    def delete_model(self, model_id: str) -> Dict[str, Any]:
        """Delete model from registry"""
        return self._request("DELETE", f"/api/v1/deployment/models/{model_id}")

    # ==================================================================
    # TRAINING JOBS
    # ==================================================================

    def create_training_job(
        self,
        config: Dict[str, Any],
        job_name: str = None,
    ) -> Dict[str, Any]:
        """
        Create a new training job on the platform

        Args:
            config: Training configuration
            job_name: Optional job name

        Returns:
            dict: Job details with job_id
        """
        data = {
            "config": config,
            "name": job_name,
        }
        return self._request("POST", "/api/v1/finetuning/jobs", data=data)

    def get_training_job(self, job_id: str) -> Dict[str, Any]:
        """Get training job status"""
        return self._request("GET", f"/api/v1/finetuning/jobs/{job_id}")

    def list_training_jobs(self, status: str = None) -> list:
        """List training jobs"""
        params = {}
        if status:
            params["status"] = status
        response = self._request("GET", "/api/v1/finetuning/jobs", params=params)
        return response.get("jobs", [])

    def cancel_training_job(self, job_id: str) -> Dict[str, Any]:
        """Cancel a running training job"""
        return self._request("POST", f"/api/v1/finetuning/jobs/{job_id}/cancel")

    # ==================================================================
    # DEPLOYMENT
    # ==================================================================

    def deploy_model(
        self,
        model_id: str,
        deployment_config: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Deploy model to Calaxis cloud

        Args:
            model_id: Model ID from registry
            deployment_config: Deployment configuration

        Returns:
            dict: Deployment details
        """
        data = {
            "model_id": model_id,
            "config": deployment_config or {},
        }
        return self._request("POST", "/api/v1/deployment/deploy", data=data)

    def get_deployment(self, deployment_id: str) -> Dict[str, Any]:
        """Get deployment status"""
        return self._request("GET", f"/api/v1/deployment/{deployment_id}")

    def list_deployments(self) -> list:
        """List all deployments"""
        response = self._request("GET", "/api/v1/deployment")
        return response.get("deployments", [])

    def stop_deployment(self, deployment_id: str) -> Dict[str, Any]:
        """Stop a deployment"""
        return self._request("POST", f"/api/v1/deployment/{deployment_id}/stop")

    # ==================================================================
    # METRICS
    # ==================================================================

    def report_training_metrics(
        self,
        job_id: str,
        metrics: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Report training metrics to platform

        Args:
            job_id: Training job ID
            metrics: Metrics dictionary (loss, accuracy, etc.)

        Returns:
            dict: Response
        """
        return self._request(
            "POST",
            f"/api/v1/finetuning/jobs/{job_id}/metrics",
            data=metrics,
        )

    def get_training_metrics(self, job_id: str) -> list:
        """Get training metrics history"""
        response = self._request("GET", f"/api/v1/finetuning/jobs/{job_id}/metrics")
        return response.get("metrics", [])
