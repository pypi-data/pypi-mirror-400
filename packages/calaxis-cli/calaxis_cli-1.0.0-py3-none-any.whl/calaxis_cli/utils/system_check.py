"""
System compatibility checker for Calaxis local training

Detects hardware capabilities:
- Apple Silicon with MLX (unified memory)
- NVIDIA CUDA GPUs
- System RAM and disk space
"""
import platform
import subprocess
from typing import Dict, Any

# Try to import torch (optional for system check)
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

# Try to import psutil
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


def check_mlx_availability() -> Dict[str, Any]:
    """Check if MLX is available for Apple Silicon"""
    mlx_info = {
        "available": False,
        "is_apple_silicon": False,
        "unified_memory_gb": None,
        "mlx_version": None,
    }

    # Check if running on Apple Silicon
    if platform.system() == "Darwin" and platform.machine() == "arm64":
        mlx_info["is_apple_silicon"] = True

        # Try to import MLX
        try:
            import mlx
            import mlx.core as mx
            mlx_info["available"] = True

            # Get MLX version from pip
            try:
                result = subprocess.run(['pip', 'show', 'mlx'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if line.startswith('Version:'):
                            mlx_info["mlx_version"] = line.split(':', 1)[1].strip()
                            break
            except:
                mlx_info["mlx_version"] = "unknown"

            # Get unified memory info (RAM on Apple Silicon = GPU memory)
            if HAS_PSUTIL:
                ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)
                mlx_info["unified_memory_gb"] = ram_gb

        except ImportError:
            mlx_info["error"] = "MLX not installed. Install with: pip install mlx mlx-lm"

    return mlx_info


def check_gpu_availability() -> Dict[str, Any]:
    """Check if CUDA GPUs are available and get their details"""
    gpu_info = {
        "available": False,
        "count": 0,
        "devices": [],
        "cuda_version": None,
        "driver_version": None,
    }

    if not HAS_TORCH:
        gpu_info["error"] = "PyTorch not installed"
        return gpu_info

    try:
        if torch.cuda.is_available():
            gpu_info["available"] = True
            gpu_info["count"] = torch.cuda.device_count()
            gpu_info["cuda_version"] = torch.version.cuda

            # Get driver version
            try:
                result = subprocess.run(['nvidia-smi', '--query-gpu=driver_version', '--format=csv,noheader'],
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    gpu_info["driver_version"] = result.stdout.strip().split('\n')[0]
            except:
                pass

            # Get GPU details
            for i in range(gpu_info["count"]):
                device_props = torch.cuda.get_device_properties(i)
                gpu_info["devices"].append({
                    "id": i,
                    "name": device_props.name,
                    "total_memory_gb": round(device_props.total_memory / (1024**3), 2),
                    "compute_capability": f"{device_props.major}.{device_props.minor}",
                })
    except Exception as e:
        gpu_info["error"] = str(e)

    return gpu_info


def check_system_resources() -> Dict[str, Any]:
    """Check system CPU and RAM"""
    info = {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "python_version": platform.python_version(),
        "machine": platform.machine(),
    }

    if HAS_PSUTIL:
        info.update({
            "cpu_count": psutil.cpu_count(logical=True),
            "cpu_count_physical": psutil.cpu_count(logical=False),
            "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "ram_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
        })

    return info


def check_disk_space(path: str = "/") -> Dict[str, Any]:
    """Check available disk space"""
    if not HAS_PSUTIL:
        return {"error": "psutil not installed"}

    try:
        disk = psutil.disk_usage(path)
        return {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percent_used": disk.percent,
        }
    except Exception as e:
        return {"error": str(e)}


def check_system_compatibility() -> Dict[str, Any]:
    """
    Check system compatibility for local training

    Returns complete system report with all hardware info
    """
    return get_system_report()


def assess_training_feasibility(model_size: str = "7B") -> Dict[str, Any]:
    """
    Assess if local training is feasible based on system resources

    Args:
        model_size: Model size (7B, 13B, 70B, etc.)
    """
    gpu_info = check_gpu_availability()
    mlx_info = check_mlx_availability()
    system_info = check_system_resources()
    disk_info = check_disk_space()

    # Minimum requirements for different model sizes (in GB VRAM)
    min_requirements = {
        "7B": {
            "vram_4bit": 6,    # QLoRA 4-bit
            "vram_8bit": 10,   # QLoRA 8-bit
            "vram_full": 24,   # Full fine-tuning
            "ram": 16,
            "disk": 50,
        },
        "13B": {
            "vram_4bit": 10,
            "vram_8bit": 16,
            "vram_full": 40,
            "ram": 32,
            "disk": 80,
        },
        "70B": {
            "vram_4bit": 40,
            "vram_8bit": 80,
            "vram_full": 160,
            "ram": 64,
            "disk": 200,
        },
    }

    # Extract model size
    size = "7B"
    for key in min_requirements.keys():
        if key in model_size.upper():
            size = key
            break

    requirements = min_requirements.get(size, min_requirements["7B"])

    # Assessment
    assessment = {
        "feasible": False,
        "recommended_method": None,
        "warnings": [],
        "requirements": requirements,
        "system_meets_requirements": {
            "gpu": False,
            "ram": False,
            "disk": False,
        },
    }

    # Check MLX (Apple Silicon) first
    if mlx_info["available"]:
        unified_memory = mlx_info["unified_memory_gb"]

        if unified_memory and unified_memory >= requirements["vram_4bit"]:
            assessment["system_meets_requirements"]["gpu"] = True

            if unified_memory >= requirements["vram_full"]:
                assessment["recommended_method"] = "mlx_full"
            elif unified_memory >= requirements["vram_8bit"]:
                assessment["recommended_method"] = "mlx_8bit"
            else:
                assessment["recommended_method"] = "mlx_4bit"
        else:
            assessment["warnings"].append(
                f"Unified memory ({unified_memory}GB) is below minimum requirement ({requirements['vram_4bit']}GB for MLX training)"
            )
    # Check CUDA GPU if MLX not available
    elif gpu_info["available"] and gpu_info["count"] > 0:
        max_vram = max([gpu["total_memory_gb"] for gpu in gpu_info["devices"]])

        if max_vram >= requirements["vram_4bit"]:
            assessment["system_meets_requirements"]["gpu"] = True

            if max_vram >= requirements["vram_full"]:
                assessment["recommended_method"] = "full_finetuning"
            elif max_vram >= requirements["vram_8bit"]:
                assessment["recommended_method"] = "qlora_8bit"
            else:
                assessment["recommended_method"] = "qlora_4bit"
        else:
            assessment["warnings"].append(
                f"GPU VRAM ({max_vram}GB) is below minimum requirement ({requirements['vram_4bit']}GB for 4-bit QLoRA)"
            )
    # Apple Silicon detected but MLX not installed
    elif mlx_info["is_apple_silicon"]:
        assessment["warnings"].append("Apple Silicon detected but MLX not installed. Install with: pip install mlx mlx-lm")
    # No GPU at all
    else:
        assessment["warnings"].append("No CUDA-capable GPU or Apple Silicon with MLX detected")

    # Check RAM
    ram_total = system_info.get("ram_total_gb", 0)
    if ram_total >= requirements["ram"]:
        assessment["system_meets_requirements"]["ram"] = True
    else:
        assessment["warnings"].append(
            f"System RAM ({ram_total}GB) is below recommended ({requirements['ram']}GB)"
        )

    # Check Disk (warning only, not blocking)
    if disk_info.get("free_gb", 0) >= requirements["disk"]:
        assessment["system_meets_requirements"]["disk"] = True
    else:
        assessment["system_meets_requirements"]["disk"] = False
        assessment["warnings"].append(
            f"Free disk space ({disk_info.get('free_gb', 0)}GB) is below recommended ({requirements['disk']}GB). Training may run out of space during model checkpoints."
        )

    # Overall feasibility (disk space is a warning, not a blocker)
    assessment["feasible"] = (
        assessment["system_meets_requirements"]["gpu"] and
        assessment["system_meets_requirements"]["ram"]
    )

    # Cloud alternatives
    if not assessment["feasible"]:
        assessment["cloud_alternatives"] = [
            {
                "provider": "Calaxis GPU Cloud",
                "description": "Our managed GPU service with pay-as-you-go pricing",
                "estimated_cost_per_hour": "$5-25 depending on GPU type",
            },
            {
                "provider": "Google Colab Pro+",
                "description": "Jupyter notebooks with GPU access",
                "estimated_cost_per_month": "$50",
            },
            {
                "provider": "RunPod",
                "description": "Cloud GPU rental marketplace",
                "estimated_cost_per_hour": "$0.20-1.50 depending on GPU",
            },
            {
                "provider": "Lambda Labs",
                "description": "Cloud GPU instances for ML",
                "estimated_cost_per_hour": "$0.50-3.00 depending on GPU",
            },
        ]

    return {
        "gpu": gpu_info,
        "mlx": mlx_info,
        "system": system_info,
        "disk": disk_info,
        "assessment": assessment,
    }


def get_system_report() -> Dict[str, Any]:
    """Get a comprehensive system compatibility report"""
    report = {
        "gpu": check_gpu_availability(),
        "mlx": check_mlx_availability(),
        "system": check_system_resources(),
        "disk": check_disk_space(),
    }

    if HAS_TORCH:
        report["pytorch_version"] = torch.__version__
        report["cuda_available"] = torch.cuda.is_available()

    # Determine recommended training method
    mlx_info = report["mlx"]
    gpu_info = report["gpu"]

    if mlx_info["available"]:
        report["recommended_method"] = "mlx"
        report["training_capable"] = True
        report["message"] = f"✅ MLX available with {mlx_info['unified_memory_gb']}GB unified memory"
    elif gpu_info["available"]:
        report["recommended_method"] = "cuda"
        report["training_capable"] = True
        total_vram = sum([gpu["total_memory_gb"] for gpu in gpu_info["devices"]])
        report["message"] = f"✅ CUDA GPU available with {total_vram}GB VRAM"
    elif mlx_info["is_apple_silicon"]:
        report["recommended_method"] = None
        report["training_capable"] = False
        report["message"] = "⚠️ Apple Silicon detected but MLX not installed"
        report["installation_guide"] = {
            "mlx": "pip install mlx mlx-lm",
            "note": "MLX enables efficient training on Apple Silicon using unified memory"
        }
    else:
        report["recommended_method"] = "cloud"
        report["training_capable"] = False
        report["message"] = "❌ No GPU detected. Consider using cloud GPU services."

    return report
