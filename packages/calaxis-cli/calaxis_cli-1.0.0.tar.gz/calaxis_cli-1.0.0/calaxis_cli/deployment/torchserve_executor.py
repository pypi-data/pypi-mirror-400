"""
TorchServe Model Server for Calaxis CLI

Production-grade model serving using TorchServe.

Features:
- REST API for model inference
- gRPC API for high-performance inference
- Model versioning and management
- Prometheus metrics
- Batch inference
- GPU acceleration

References:
- TorchServe: https://pytorch.org/serve/
"""
import logging
import os
import subprocess
import tempfile
from typing import Dict, Any, List, Optional
from pathlib import Path
import shutil

logger = logging.getLogger(__name__)

# Try to import requests
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class TorchServeModelServer:
    """
    TorchServe-based model server

    Provides production-grade model serving with TorchServe
    including model archiving, deployment, and management.
    """

    def __init__(
        self,
        model_store_dir: str = "/tmp/calaxis/torchserve/model-store",
        config_file: Optional[str] = None,
        host: str = "localhost",
        management_port: int = 8081,
        inference_port: int = 8080,
        metrics_port: int = 8082,
    ):
        """
        Initialize TorchServe model server

        Args:
            model_store_dir: Directory to store model archives
            config_file: Path to TorchServe config file
            host: TorchServe host
            management_port: Management API port
            inference_port: Inference API port
            metrics_port: Metrics API port
        """
        self.model_store_dir = model_store_dir
        self.config_file = config_file
        self.host = host
        self.management_port = management_port
        self.inference_port = inference_port
        self.metrics_port = metrics_port

        # Ensure model store directory exists
        os.makedirs(self.model_store_dir, exist_ok=True)

        # API endpoints
        self.management_url = f"http://{host}:{management_port}"
        self.inference_url = f"http://{host}:{inference_port}"
        self.metrics_url = f"http://{host}:{metrics_port}"

        logger.info(f"Initialized TorchServe executor with model store: {model_store_dir}")

    # ==================================================================
    # MODEL ARCHIVING
    # ==================================================================

    def create_model_archive(
        self,
        model_name: str,
        model_file: str,
        handler: str = "custom_handler.py",
        serialized_file: Optional[str] = None,
        version: str = "1.0",
        extra_files: Optional[List[str]] = None,
        requirements_file: Optional[str] = None,
        export_path: Optional[str] = None,
        force: bool = True,
    ) -> str:
        """
        Create TorchServe model archive (.mar file)

        Args:
            model_name: Name of the model
            model_file: Path to model file (.pt or .pth)
            handler: Path to custom handler script
            serialized_file: Path to serialized model (optional)
            version: Model version
            extra_files: Additional files to include
            requirements_file: Python requirements file
            export_path: Where to save .mar file
            force: Overwrite existing archive

        Returns:
            str: Path to created .mar file
        """
        logger.info(f"Creating model archive for: {model_name}")

        # Default export path
        if export_path is None:
            export_path = self.model_store_dir

        # Build torch-model-archiver command
        cmd = [
            "torch-model-archiver",
            "--model-name", model_name,
            "--version", version,
            "--serialized-file", serialized_file or model_file,
            "--handler", handler,
            "--export-path", export_path,
        ]

        if extra_files:
            cmd.extend(["--extra-files", ",".join(extra_files)])

        if requirements_file:
            cmd.extend(["--requirements-file", requirements_file])

        if force:
            cmd.append("--force")

        try:
            # Run torch-model-archiver
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )

            mar_file = os.path.join(export_path, f"{model_name}.mar")
            logger.info(f"Model archive created: {mar_file}")

            return mar_file

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create model archive: {e.stderr}")
            raise

    def create_huggingface_archive(
        self,
        model_name: str,
        model_path: str,
        version: str = "1.0",
        export_path: Optional[str] = None,
    ) -> str:
        """
        Create model archive for HuggingFace models

        Args:
            model_name: Name of the model
            model_path: Path to HuggingFace model directory
            version: Model version
            export_path: Where to save .mar file

        Returns:
            str: Path to created .mar file
        """
        logger.info(f"Creating HuggingFace model archive: {model_name}")

        # Default export path
        if export_path is None:
            export_path = self.model_store_dir

        # Create temporary handler for HuggingFace models
        handler_content = '''
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from ts.torch_handler.base_handler import BaseHandler

class TransformersHandler(BaseHandler):
    def __init__(self):
        super().__init__()
        self.initialized = False

    def initialize(self, context):
        """Initialize model and tokenizer"""
        self.manifest = context.manifest
        properties = context.system_properties
        model_dir = properties.get("model_dir")

        # Load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_dir,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        self.model.eval()
        self.initialized = True

    def preprocess(self, data):
        """Preprocess input data"""
        text = data[0].get("data") or data[0].get("body")
        if isinstance(text, bytes):
            text = text.decode("utf-8")

        # Tokenize
        inputs = self.tokenizer(text, return_tensors="pt")
        return inputs

    def inference(self, inputs):
        """Run inference"""
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=100,
                temperature=0.7,
                top_p=0.9,
                do_sample=True
            )
        return outputs

    def postprocess(self, outputs):
        """Postprocess outputs"""
        # Decode tokens to text
        text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return [text]
'''

        # Create temporary handler file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(handler_content)
            handler_path = f.name

        requirements_path = None
        try:
            # Create requirements file
            requirements = [
                "transformers>=4.35.0",
                "torch>=2.1.0",
                "accelerate>=0.24.0",
            ]

            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write("\n".join(requirements))
                requirements_path = f.name

            # Create model archive
            mar_file = self.create_model_archive(
                model_name=model_name,
                model_file=model_path,
                handler=handler_path,
                version=version,
                extra_files=[model_path],
                requirements_file=requirements_path,
                export_path=export_path,
            )

            return mar_file

        finally:
            # Clean up temp files
            if os.path.exists(handler_path):
                os.remove(handler_path)
            if requirements_path and os.path.exists(requirements_path):
                os.remove(requirements_path)

    # ==================================================================
    # MODEL MANAGEMENT
    # ==================================================================

    def register_model(
        self,
        model_name: str,
        mar_file: str,
        initial_workers: int = 1,
        batch_size: int = 1,
        max_batch_delay: int = 100,
        response_timeout: int = 120,
    ) -> Dict[str, Any]:
        """
        Register model with TorchServe

        Args:
            model_name: Name of the model
            mar_file: Path to .mar file
            initial_workers: Number of worker processes
            batch_size: Batch size for inference
            max_batch_delay: Max delay for batching (ms)
            response_timeout: Response timeout (seconds)

        Returns:
            dict: Registration response
        """
        if not HAS_REQUESTS:
            raise ImportError("requests library required. Install with: pip install requests")

        logger.info(f"Registering model: {model_name}")

        # Copy .mar file to model store if not already there
        if not mar_file.startswith(self.model_store_dir):
            dest_path = os.path.join(self.model_store_dir, os.path.basename(mar_file))
            shutil.copy2(mar_file, dest_path)
            mar_file = dest_path

        # Register via management API
        url = f"{self.management_url}/models"
        params = {
            "url": os.path.basename(mar_file),
            "model_name": model_name,
            "initial_workers": initial_workers,
            "batch_size": batch_size,
            "max_batch_delay": max_batch_delay,
            "response_timeout": response_timeout,
        }

        try:
            response = requests.post(url, params=params)
            response.raise_for_status()

            logger.info(f"Model registered: {model_name}")
            return response.json()

        except requests.RequestException as e:
            logger.error(f"Failed to register model: {e}")
            raise

    def unregister_model(self, model_name: str, version: Optional[str] = None) -> Dict[str, Any]:
        """Unregister model from TorchServe"""
        if not HAS_REQUESTS:
            raise ImportError("requests library required")

        logger.info(f"Unregistering model: {model_name}")

        url = f"{self.management_url}/models/{model_name}"
        if version:
            url += f"/{version}"

        try:
            response = requests.delete(url)
            response.raise_for_status()

            logger.info(f"Model unregistered: {model_name}")
            return response.json()

        except requests.RequestException as e:
            logger.error(f"Failed to unregister model: {e}")
            raise

    def list_models(self) -> List[Dict[str, Any]]:
        """List all registered models"""
        if not HAS_REQUESTS:
            raise ImportError("requests library required")

        try:
            response = requests.get(f"{self.management_url}/models")
            response.raise_for_status()

            data = response.json()
            return data.get("models", [])

        except requests.RequestException as e:
            logger.error(f"Failed to list models: {e}")
            return []

    def describe_model(self, model_name: str, version: Optional[str] = None) -> Dict[str, Any]:
        """Get model details"""
        if not HAS_REQUESTS:
            raise ImportError("requests library required")

        url = f"{self.management_url}/models/{model_name}"
        if version:
            url += f"/{version}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            logger.error(f"Failed to describe model: {e}")
            raise

    # ==================================================================
    # WORKER MANAGEMENT
    # ==================================================================

    def scale_workers(
        self,
        model_name: str,
        min_workers: int,
        max_workers: int,
        version: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Scale model workers"""
        if not HAS_REQUESTS:
            raise ImportError("requests library required")

        logger.info(f"Scaling workers for {model_name}: min={min_workers}, max={max_workers}")

        url = f"{self.management_url}/models/{model_name}"
        if version:
            url += f"/{version}"

        params = {
            "min_worker": min_workers,
            "max_worker": max_workers,
        }

        try:
            response = requests.put(url, params=params)
            response.raise_for_status()

            logger.info(f"Workers scaled for: {model_name}")
            return response.json()

        except requests.RequestException as e:
            logger.error(f"Failed to scale workers: {e}")
            raise

    # ==================================================================
    # INFERENCE
    # ==================================================================

    def predict(
        self,
        model_name: str,
        data: Any,
        version: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run inference on model

        Args:
            model_name: Name of the model
            data: Input data (text, dict, etc.)
            version: Model version (optional)

        Returns:
            dict: Inference result
        """
        if not HAS_REQUESTS:
            raise ImportError("requests library required")

        url = f"{self.inference_url}/predictions/{model_name}"
        if version:
            url += f"/{version}"

        # Prepare payload
        if isinstance(data, str):
            payload = {"data": data}
        elif isinstance(data, dict):
            payload = data
        else:
            payload = {"data": str(data)}

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            logger.error(f"Inference failed: {e}")
            raise

    # ==================================================================
    # METRICS
    # ==================================================================

    def get_metrics(self) -> str:
        """Get Prometheus metrics"""
        if not HAS_REQUESTS:
            raise ImportError("requests library required")

        try:
            response = requests.get(f"{self.metrics_url}/metrics")
            response.raise_for_status()
            return response.text

        except requests.RequestException as e:
            logger.error(f"Failed to get metrics: {e}")
            return ""

    def get_model_metrics(self, model_name: str) -> Dict[str, Any]:
        """Get metrics for specific model"""
        # Parse Prometheus metrics
        metrics_text = self.get_metrics()

        # Extract model-specific metrics
        model_metrics = {}
        for line in metrics_text.split("\n"):
            if model_name in line and not line.startswith("#"):
                parts = line.split()
                if len(parts) >= 2:
                    metric_name = parts[0].split("{")[0]
                    metric_value = parts[-1]
                    model_metrics[metric_name] = metric_value

        return model_metrics

    # ==================================================================
    # SERVER MANAGEMENT
    # ==================================================================

    def start_server(
        self,
        ncs: bool = True,
        foreground: bool = False,
    ) -> subprocess.Popen:
        """
        Start TorchServe server

        Args:
            ncs: Start with no-config-snapshots mode
            foreground: Run in foreground (blocking)

        Returns:
            subprocess.Popen: Server process
        """
        logger.info("Starting TorchServe server...")

        cmd = [
            "torchserve",
            "--start",
            "--model-store", self.model_store_dir,
            "--ts-config", self.config_file or self._create_default_config(),
        ]

        if ncs:
            cmd.append("--ncs")

        if foreground:
            cmd.append("--foreground")

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            logger.info("TorchServe server started")
            return process

        except Exception as e:
            logger.error(f"Failed to start TorchServe: {e}")
            raise

    def stop_server(self):
        """Stop TorchServe server"""
        logger.info("Stopping TorchServe server...")

        try:
            subprocess.run(["torchserve", "--stop"], check=True)
            logger.info("TorchServe server stopped")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to stop TorchServe: {e}")
            raise

    def _create_default_config(self) -> str:
        """Create default TorchServe config file"""
        config = {
            "inference_address": f"http://0.0.0.0:{self.inference_port}",
            "management_address": f"http://0.0.0.0:{self.management_port}",
            "metrics_address": f"http://0.0.0.0:{self.metrics_port}",
            "grpc_inference_port": 7070,
            "grpc_management_port": 7071,
            "enable_metrics_api": "true",
            "metrics_format": "prometheus",
            "number_of_netty_threads": 4,
            "job_queue_size": 100,
            "model_store": self.model_store_dir,
            "load_models": "all",
        }

        config_path = os.path.join(self.model_store_dir, "config.properties")

        with open(config_path, "w") as f:
            for key, value in config.items():
                f.write(f"{key}={value}\n")

        return config_path

    # ==================================================================
    # HEALTH CHECK
    # ==================================================================

    def health_check(self) -> bool:
        """Check if TorchServe is healthy"""
        if not HAS_REQUESTS:
            return False

        try:
            response = requests.get(f"{self.inference_url}/ping")
            return response.status_code == 200

        except requests.RequestException:
            return False
