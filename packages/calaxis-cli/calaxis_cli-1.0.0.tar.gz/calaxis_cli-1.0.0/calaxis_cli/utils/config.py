"""
Configuration utilities for Calaxis CLI
"""
import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML or JSON file

    Args:
        config_path: Path to configuration file (.yaml, .yml, or .json)

    Returns:
        dict: Configuration dictionary
    """
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(path, 'r') as f:
        if path.suffix in ['.yaml', '.yml']:
            return yaml.safe_load(f)
        elif path.suffix == '.json':
            return json.load(f)
        else:
            raise ValueError(f"Unsupported config file format: {path.suffix}")


def validate_config(config: Dict[str, Any], config_type: str = "training") -> Dict[str, Any]:
    """
    Validate configuration dictionary

    Args:
        config: Configuration dictionary
        config_type: Type of configuration ("training" or "deployment")

    Returns:
        dict: Validation result with 'valid' boolean and 'errors' list
    """
    errors = []
    warnings = []

    if config_type == "training":
        # Required fields for training
        required_fields = ["base_model", "dataset_path"]

        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")

        # Validate dataset path
        if "dataset_path" in config:
            dataset_path = config["dataset_path"]
            if not os.path.exists(dataset_path):
                errors.append(f"Dataset file not found: {dataset_path}")
            elif not dataset_path.endswith(('.jsonl', '.json', '.csv')):
                warnings.append(f"Dataset format may not be supported. Expected: .jsonl, .json, or .csv")

        # Validate numeric fields
        numeric_fields = {
            "num_epochs": (1, 100),
            "batch_size": (1, 64),
            "learning_rate": (1e-8, 1),
            "lora_r": (1, 256),
            "lora_alpha": (1, 512),
            "max_seq_length": (32, 8192),
        }

        for field, (min_val, max_val) in numeric_fields.items():
            if field in config:
                value = config[field]
                if not isinstance(value, (int, float)):
                    errors.append(f"Field '{field}' must be a number")
                elif value < min_val or value > max_val:
                    warnings.append(f"Field '{field}' value {value} is outside recommended range [{min_val}, {max_val}]")

        # Validate quantization options
        if config.get("use_4bit") and config.get("use_8bit"):
            errors.append("Cannot use both 4-bit and 8-bit quantization")

    elif config_type == "deployment":
        # Required fields for deployment
        required_fields = ["model_path"]

        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")

        # Validate model path
        if "model_path" in config:
            model_path = config["model_path"]
            if not os.path.exists(model_path):
                errors.append(f"Model path not found: {model_path}")

        # Validate port
        if "port" in config:
            port = config["port"]
            if not isinstance(port, int) or port < 1 or port > 65535:
                errors.append(f"Invalid port: {port}")

        # Validate model type
        valid_model_types = ["huggingface", "pytorch", "onnx"]
        if "model_type" in config and config["model_type"] not in valid_model_types:
            errors.append(f"Invalid model_type. Must be one of: {valid_model_types}")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


def get_default_training_config() -> Dict[str, Any]:
    """Get default training configuration"""
    return {
        "base_model": "meta-llama/Llama-3.1-8B",
        "dataset_path": "./dataset.jsonl",
        "output_dir": "./output",
        "num_epochs": 3,
        "batch_size": 4,
        "learning_rate": 2e-4,
        "max_seq_length": 512,
        "use_4bit": True,
        "use_8bit": False,
        "lora_r": 16,
        "lora_alpha": 32,
        "lora_dropout": 0.05,
        "gradient_accumulation_steps": 4,
        "warmup_steps": 100,
        "save_steps": 500,
        "logging_steps": 10,
    }


def get_default_deployment_config() -> Dict[str, Any]:
    """Get default deployment configuration"""
    return {
        "model_path": "./model",
        "model_type": "huggingface",
        "host": "0.0.0.0",
        "port": 8080,
        "max_batch_size": 4,
        "timeout": 120,
    }


def save_config(config: Dict[str, Any], output_path: str) -> str:
    """
    Save configuration to file

    Args:
        config: Configuration dictionary
        output_path: Output file path (.yaml or .json)

    Returns:
        str: Path to saved file
    """
    path = Path(output_path)

    with open(path, 'w') as f:
        if path.suffix in ['.yaml', '.yml']:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        elif path.suffix == '.json':
            json.dump(config, f, indent=2)
        else:
            raise ValueError(f"Unsupported config file format: {path.suffix}")

    return str(path)


def create_sample_config(output_dir: str = ".", config_type: str = "training") -> str:
    """
    Create a sample configuration file

    Args:
        output_dir: Directory to save the config file
        config_type: Type of configuration ("training" or "deployment")

    Returns:
        str: Path to created config file
    """
    os.makedirs(output_dir, exist_ok=True)

    if config_type == "training":
        config = get_default_training_config()
        output_path = os.path.join(output_dir, "training_config.yaml")
    elif config_type == "deployment":
        config = get_default_deployment_config()
        output_path = os.path.join(output_dir, "deployment_config.yaml")
    else:
        raise ValueError(f"Invalid config_type: {config_type}")

    return save_config(config, output_path)
