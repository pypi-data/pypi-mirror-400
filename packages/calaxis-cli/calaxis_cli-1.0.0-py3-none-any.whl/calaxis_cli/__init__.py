"""
Calaxis AI Platform - Local Training & Deployment CLI

This package enables local fine-tuning and deployment of LLMs using the Calaxis AI Platform.

Features:
- Local fine-tuning with LoRA/QLoRA
- Apple Silicon (MLX) and CUDA GPU support
- Model deployment with FastAPI, TorchServe, or Triton
- Integration with Calaxis Platform for model registry and monitoring

Usage:
    calaxis --help                    # Show all commands
    calaxis system check              # Check system compatibility
    calaxis train --config config.yaml # Start local training
    calaxis deploy --model ./model    # Deploy model locally
    calaxis upload --model ./model    # Upload trained model to Calaxis Platform
"""

__version__ = "1.0.0"
__author__ = "Calaxis AI"
__email__ = "support@calaxis.ai"

# Import main classes for convenience
from .training.executor import LocalTrainingExecutor
from .deployment.fastapi_executor import FastAPIModelServer
from .deployment.torchserve_executor import TorchServeModelServer
from .utils.system_check import (
    check_system_compatibility,
    assess_training_feasibility,
    get_system_report,
)
from .utils.config import load_config, validate_config
from .utils.api_client import CalaxisAPIClient

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    # Training
    "LocalTrainingExecutor",
    # Deployment
    "FastAPIModelServer",
    "TorchServeModelServer",
    # Utils
    "check_system_compatibility",
    "assess_training_feasibility",
    "get_system_report",
    "load_config",
    "validate_config",
    "CalaxisAPIClient",
]
