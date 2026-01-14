# Calaxis AI Platform - Local Training & Deployment CLI

Local fine-tuning and deployment CLI for the Calaxis AI Platform. Train and deploy LLMs on your local hardware using Apple Silicon (MLX) or NVIDIA CUDA GPUs.

## Features

- **Local Fine-Tuning**: Train LLMs on your own hardware
- **Apple Silicon Support**: Native MLX support for M1/M2/M3 Macs
- **NVIDIA CUDA Support**: Full GPU acceleration for NVIDIA GPUs
- **QLoRA/LoRA**: Memory-efficient fine-tuning with 4-bit and 8-bit quantization
- **Easy Deployment**: Deploy models locally with FastAPI or TorchServe
- **Platform Integration**: Upload trained models to Calaxis Platform

## Installation

### Quick Install (Recommended)

```bash
# Basic installation
pip install calaxis-cli

# With training dependencies
pip install calaxis-cli[training]

# Full installation (training + deployment)
pip install calaxis-cli[full]
```

### From Source

```bash
# Clone the repository
git clone https://github.com/calaxis/calaxis-cli.git
cd calaxis-cli

# Install in development mode
pip install -e .

# Install with all dependencies
pip install -e ".[full]"
```

### Platform-Specific Installation

**For Apple Silicon (M1/M2/M3 Macs):**
```bash
pip install calaxis-cli[training]
pip install mlx mlx-lm
```

**For NVIDIA GPUs:**
```bash
pip install calaxis-cli[training,cuda]
```

## Quick Start

### 1. Check System Compatibility

```bash
# Check your system
calaxis system check

# Check for specific model size
calaxis system check --model-size 7B
```

### 2. Initialize a Project

```bash
# Create a new project with sample files
calaxis init my-project
cd my-project
```

### 3. Prepare Your Dataset

Create a JSONL file with your training data:

```jsonl
{"prompt": "What is machine learning?", "completion": "Machine learning is..."}
{"prompt": "Explain neural networks.", "completion": "Neural networks are..."}
```

Or use instruction format:

```jsonl
{"instruction": "Summarize this text", "input": "Long text...", "output": "Summary..."}
```

### 4. Train Your Model

**Using a config file:**

```bash
calaxis train --config training_config.yaml
```

**Using command-line arguments:**

```bash
calaxis train \
  --model meta-llama/Llama-3.1-8B \
  --dataset ./data.jsonl \
  --output ./output \
  --epochs 3 \
  --batch-size 4 \
  --quantization 4bit
```

### 5. Deploy Your Model

**Deploy with FastAPI (recommended for prototyping):**

```bash
calaxis deploy --model ./output/final_model --server fastapi --port 8080
```

**Deploy with TorchServe (recommended for production):**

```bash
calaxis deploy --model ./output/final_model --server torchserve
```

**Generate deployment files only:**

```bash
calaxis deploy --model ./output/final_model --generate-only --output ./deployment
```

### 6. Upload to Calaxis Platform

```bash
# Set your API key
export CALAXIS_API_KEY=your_api_key

# Upload the model
calaxis upload --model ./output/final_model --name my-fine-tuned-model
```

## Configuration

### Training Configuration (YAML)

```yaml
# training_config.yaml
base_model: meta-llama/Llama-3.1-8B
dataset_path: ./dataset.jsonl
output_dir: ./output

# Training parameters
num_epochs: 3
batch_size: 4
learning_rate: 0.0002
max_seq_length: 512

# Quantization (for memory efficiency)
use_4bit: true
use_8bit: false

# LoRA parameters
lora_r: 16
lora_alpha: 32
lora_dropout: 0.05

# Advanced settings
gradient_accumulation_steps: 4
warmup_steps: 100
save_steps: 500
logging_steps: 10
```

### Deployment Configuration

```yaml
# deployment_config.yaml
model_path: ./output/final_model
model_type: huggingface
host: 0.0.0.0
port: 8080
max_batch_size: 4
timeout: 120
```

## Commands Reference

### System Commands

```bash
# Check system compatibility
calaxis system check

# Check compatibility for specific model size
calaxis system check --model-size 13B
```

### Training Commands

```bash
# Train with config file
calaxis train --config config.yaml

# Train with arguments
calaxis train \
  --model <model_name_or_path> \
  --dataset <dataset_path> \
  --output <output_directory> \
  --epochs <num_epochs> \
  --batch-size <batch_size> \
  --learning-rate <lr> \
  --quantization <4bit|8bit|none> \
  --lora-r <rank> \
  --lora-alpha <alpha> \
  --max-length <max_seq_length>
```

### Deployment Commands

```bash
# Deploy with FastAPI
calaxis deploy --model ./model --server fastapi --port 8080

# Deploy with TorchServe
calaxis deploy --model ./model --server torchserve

# Generate deployment bundle
calaxis deploy --model ./model --generate-only --output ./deploy

# Options:
#   --model, -m       Path to model (required)
#   --server, -s      Server type: fastapi, torchserve
#   --model-type, -t  Model type: huggingface, pytorch, onnx
#   --host            Server host (default: 0.0.0.0)
#   --port, -p        Server port (default: 8080)
#   --generate-only   Generate files without starting server
#   --output, -o      Output directory for generated files
#   --reload          Enable auto-reload (development)
```

### Upload Commands

```bash
# Upload model to Calaxis Platform
calaxis upload \
  --model ./model \
  --name my-model \
  --description "My fine-tuned model" \
  --tags llm,custom

# Options:
#   --model, -m       Path to model (required)
#   --name, -n        Model name
#   --description, -d Model description
#   --tags            Comma-separated tags
#   --api-url         Calaxis API URL
#   --api-key         Calaxis API key (or set CALAXIS_API_KEY env)
```

### Initialize Command

```bash
# Create new project with sample files
calaxis init [directory]
```

## Hardware Requirements

### Minimum Requirements

| Model Size | RAM | GPU VRAM (4-bit) | GPU VRAM (8-bit) | Disk |
|------------|-----|------------------|------------------|------|
| 7B         | 16GB | 6GB             | 10GB             | 50GB |
| 13B        | 32GB | 10GB            | 16GB             | 80GB |
| 70B        | 64GB | 40GB            | 80GB             | 200GB |

### Recommended Hardware

**Apple Silicon:**
- Mac Mini M2 Pro (32GB) - Good for 7B models
- MacBook Pro M3 Max (64GB) - Good for 13B models
- Mac Studio M2 Ultra (192GB) - Good for 70B models

**NVIDIA GPUs:**
- RTX 3090 (24GB) - Good for 7B models
- RTX 4090 (24GB) - Good for 7B-13B models
- A100 (40GB/80GB) - Good for all sizes
- H100 (80GB) - Best for large models

## Dataset Formats

### Prompt-Completion Format
```jsonl
{"prompt": "Question or input", "completion": "Expected output"}
```

### Instruction Format
```jsonl
{"instruction": "Task instruction", "input": "Optional input", "output": "Expected output"}
```

### Text Format
```jsonl
{"text": "Complete text for language modeling"}
```

## API Reference

### Python API

```python
from calaxis_cli import LocalTrainingExecutor, FastAPIModelServer
from calaxis_cli.utils import check_system_compatibility, assess_training_feasibility

# Check system
report = check_system_compatibility()
print(report["message"])

# Assess feasibility
assessment = assess_training_feasibility("7B")
print(f"Feasible: {assessment['assessment']['feasible']}")

# Train model
config = {
    "base_model": "meta-llama/Llama-3.1-8B",
    "dataset_path": "./data.jsonl",
    "output_dir": "./output",
    "num_epochs": 3,
    "use_4bit": True,
}
executor = LocalTrainingExecutor(config)
result = executor.train()

# Deploy model
server = FastAPIModelServer(
    model_path="./output/final_model",
    model_type="huggingface",
    port=8080,
)
server.generate_deployment_bundle("./deployment")
```

## Troubleshooting

### Common Issues

**Out of Memory (OOM):**
- Enable 4-bit quantization: `--quantization 4bit`
- Reduce batch size: `--batch-size 1`
- Reduce sequence length: `--max-length 256`

**MLX not found on Apple Silicon:**
```bash
pip install mlx mlx-lm
```

**CUDA not available:**
```bash
# Check CUDA installation
python -c "import torch; print(torch.cuda.is_available())"

# Install CUDA toolkit if needed
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

**Model download fails:**
- Check internet connection
- Try using a smaller model first
- Set HuggingFace cache: `export HF_HOME=/path/to/cache`

## License

Apache License 2.0

## Support

- Documentation: https://docs.calaxis.ai/cli
- Issues: https://github.com/calaxis/calaxis-cli/issues
- Email: support@calaxis.ai
