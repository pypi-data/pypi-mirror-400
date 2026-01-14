"""
FastAPI Model Server for Calaxis CLI

Generates standalone FastAPI applications for model serving.
Supports HuggingFace, PyTorch, and ONNX models.

Use Cases:
- Prototyping and testing
- Low-latency single-model serving
- Custom inference logic
- Simple REST API endpoints
"""
import logging
import os
from typing import Optional
from pathlib import Path
import subprocess
import tempfile

logger = logging.getLogger(__name__)


class FastAPIModelServer:
    """
    FastAPI-based model server generator

    Generates complete FastAPI applications for serving ML models
    with minimal configuration.
    """

    def __init__(
        self,
        model_path: str,
        model_type: str = "huggingface",
        host: str = "0.0.0.0",
        port: int = 8080,
    ):
        """
        Initialize FastAPI model server

        Args:
            model_path: Path to model directory or file
            model_type: Type of model ("huggingface", "pytorch", "onnx")
            host: Server host
            port: Server port
        """
        self.model_path = model_path
        self.model_type = model_type
        self.host = host
        self.port = port

        logger.info(f"Initialized FastAPI server for {model_type} model: {model_path}")

    def generate_app(self, output_file: Optional[str] = None) -> str:
        """
        Generate FastAPI application code

        Args:
            output_file: Path to save app.py (optional)

        Returns:
            str: Path to generated app.py
        """
        logger.info("Generating FastAPI application...")

        if self.model_type == "huggingface":
            app_code = self._generate_huggingface_app()
        elif self.model_type == "pytorch":
            app_code = self._generate_pytorch_app()
        elif self.model_type == "onnx":
            app_code = self._generate_onnx_app()
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")

        # Save to file
        if output_file is None:
            output_file = os.path.join(tempfile.gettempdir(), "calaxis_model_app.py")

        with open(output_file, "w") as f:
            f.write(app_code)

        logger.info(f"FastAPI app generated: {output_file}")
        return output_file

    def _generate_huggingface_app(self) -> str:
        """Generate FastAPI app for HuggingFace models"""
        return f'''"""
Calaxis Model Inference API
Auto-generated FastAPI application for HuggingFace model serving
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Calaxis Model Inference API",
    description="HuggingFace Model Serving powered by Calaxis",
    version="1.0.0"
)

# Global model and tokenizer
model = None
tokenizer = None

class InferenceRequest(BaseModel):
    """Inference request schema"""
    prompt: str
    max_new_tokens: int = 100
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50
    do_sample: bool = True

class InferenceResponse(BaseModel):
    """Inference response schema"""
    generated_text: str
    prompt: str
    model_name: str

@app.on_event("startup")
async def load_model():
    """Load model and tokenizer on startup"""
    global model, tokenizer

    logger.info("Loading model...")
    model_path = "{self.model_path}"

    try:
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_path)

        # Load model
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            device_map="auto",
            low_cpu_mem_usage=True
        )
        model.eval()

        logger.info("Model loaded successfully!")

    except Exception as e:
        logger.error(f"Failed to load model: {{e}}")
        raise

@app.get("/")
async def root():
    """Root endpoint"""
    return {{
        "message": "Calaxis Model Inference API",
        "model_path": "{self.model_path}",
        "status": "ready" if model is not None else "loading"
    }}

@app.get("/health")
async def health():
    """Health check endpoint"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    return {{
        "status": "healthy",
        "model_loaded": True,
        "cuda_available": torch.cuda.is_available(),
        "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0
    }}

@app.post("/predict", response_model=InferenceResponse)
async def predict(request: InferenceRequest):
    """Run inference on the model"""
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Tokenize input
        inputs = tokenizer(request.prompt, return_tensors="pt").to(model.device)

        # Generate
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=request.max_new_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
                top_k=request.top_k,
                do_sample=request.do_sample,
                pad_token_id=tokenizer.eos_token_id
            )

        # Decode
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        return InferenceResponse(
            generated_text=generated_text,
            prompt=request.prompt,
            model_name="{self.model_path}"
        )

    except Exception as e:
        logger.error(f"Inference failed: {{e}}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/info")
async def model_info():
    """Get model information"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    return {{
        "model_path": "{self.model_path}",
        "model_type": "huggingface",
        "num_parameters": sum(p.numel() for p in model.parameters()),
        "device": str(model.device),
        "dtype": str(model.dtype)
    }}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="{self.host}", port={self.port})
'''

    def _generate_pytorch_app(self) -> str:
        """Generate FastAPI app for PyTorch models"""
        return f'''"""
Calaxis Model Inference API
Auto-generated FastAPI application for PyTorch model serving
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import torch
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Calaxis PyTorch Model API",
    description="PyTorch Model Serving powered by Calaxis",
    version="1.0.0"
)

# Global model
model = None

class InferenceRequest(BaseModel):
    """Inference request schema"""
    inputs: List[float]

class InferenceResponse(BaseModel):
    """Inference response schema"""
    outputs: List[float]

@app.on_event("startup")
async def load_model():
    """Load model on startup"""
    global model

    logger.info("Loading PyTorch model...")
    model_path = "{self.model_path}"

    try:
        model = torch.load(model_path)
        model.eval()
        logger.info("Model loaded successfully!")

    except Exception as e:
        logger.error(f"Failed to load model: {{e}}")
        raise

@app.get("/health")
async def health():
    """Health check endpoint"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {{"status": "healthy"}}

@app.post("/predict", response_model=InferenceResponse)
async def predict(request: InferenceRequest):
    """Run inference"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Convert to tensor
        inputs = torch.tensor(request.inputs, dtype=torch.float32)

        # Run inference
        with torch.no_grad():
            outputs = model(inputs)

        # Convert back to list
        result = outputs.cpu().numpy().tolist()

        return InferenceResponse(outputs=result)

    except Exception as e:
        logger.error(f"Inference failed: {{e}}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="{self.host}", port={self.port})
'''

    def _generate_onnx_app(self) -> str:
        """Generate FastAPI app for ONNX models"""
        return f'''"""
Calaxis Model Inference API
Auto-generated FastAPI application for ONNX model serving
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import onnxruntime as ort
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Calaxis ONNX Model API",
    description="ONNX Model Serving powered by Calaxis",
    version="1.0.0"
)

# Global session
session = None

class InferenceRequest(BaseModel):
    """Inference request schema"""
    inputs: List[List[float]]

class InferenceResponse(BaseModel):
    """Inference response schema"""
    outputs: List[List[float]]

@app.on_event("startup")
async def load_model():
    """Load ONNX model on startup"""
    global session

    logger.info("Loading ONNX model...")
    model_path = "{self.model_path}"

    try:
        # Create inference session
        session = ort.InferenceSession(
            model_path,
            providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
        )
        logger.info("ONNX model loaded successfully!")

    except Exception as e:
        logger.error(f"Failed to load model: {{e}}")
        raise

@app.get("/health")
async def health():
    """Health check endpoint"""
    if session is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {{"status": "healthy"}}

@app.post("/predict", response_model=InferenceResponse)
async def predict(request: InferenceRequest):
    """Run ONNX inference"""
    if session is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Convert to numpy array
        inputs = np.array(request.inputs, dtype=np.float32)

        # Get input name
        input_name = session.get_inputs()[0].name

        # Run inference
        outputs = session.run(None, {{input_name: inputs}})

        # Convert to list
        result = [output.tolist() for output in outputs]

        return InferenceResponse(outputs=result)

    except Exception as e:
        logger.error(f"Inference failed: {{e}}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="{self.host}", port={self.port})
'''

    def start_server(self, app_file: Optional[str] = None, reload: bool = False) -> subprocess.Popen:
        """
        Start FastAPI server

        Args:
            app_file: Path to app.py (optional, will generate if not provided)
            reload: Enable auto-reload

        Returns:
            subprocess.Popen: Server process
        """
        logger.info("Starting FastAPI server...")

        # Generate app if not provided
        if app_file is None:
            app_file = self.generate_app()

        # Start uvicorn
        cmd = [
            "uvicorn",
            f"{Path(app_file).stem}:app",
            "--host", self.host,
            "--port", str(self.port),
        ]

        if reload:
            cmd.append("--reload")

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(Path(app_file).parent)
            )

            logger.info(f"FastAPI server started on {self.host}:{self.port}")
            return process

        except Exception as e:
            logger.error(f"Failed to start FastAPI server: {e}")
            raise

    def generate_requirements(self, output_file: str = "requirements.txt") -> str:
        """
        Generate requirements.txt for the FastAPI app

        Args:
            output_file: Path to save requirements.txt

        Returns:
            str: Path to requirements file
        """
        requirements = [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "pydantic>=2.4.0",
        ]

        if self.model_type == "huggingface":
            requirements.extend([
                "torch>=2.1.0",
                "transformers>=4.35.0",
                "accelerate>=0.24.0",
            ])
        elif self.model_type == "pytorch":
            requirements.append("torch>=2.1.0")
        elif self.model_type == "onnx":
            requirements.extend([
                "onnxruntime-gpu>=1.16.0",
                "numpy>=1.24.0",
            ])

        with open(output_file, "w") as f:
            f.write("\n".join(requirements))

        logger.info(f"Requirements file generated: {output_file}")
        return output_file

    def generate_dockerfile(self, output_file: str = "Dockerfile") -> str:
        """
        Generate Dockerfile for containerization

        Args:
            output_file: Path to save Dockerfile

        Returns:
            str: Path to Dockerfile
        """
        dockerfile_content = f'''FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app.py .

# Copy model
COPY model /app/model

# Expose port
EXPOSE {self.port}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:{self.port}/health || exit 1

# Run application
CMD ["python", "app.py"]
'''

        with open(output_file, "w") as f:
            f.write(dockerfile_content)

        logger.info(f"Dockerfile generated: {output_file}")
        return output_file

    def generate_deployment_bundle(self, output_dir: str = ".") -> dict:
        """
        Generate complete deployment bundle

        Creates:
        - app.py: FastAPI application
        - requirements.txt: Python dependencies
        - Dockerfile: Container definition
        - docker-compose.yml: Compose configuration

        Args:
            output_dir: Directory to save files

        Returns:
            dict: Paths to generated files
        """
        os.makedirs(output_dir, exist_ok=True)

        files = {
            "app": self.generate_app(os.path.join(output_dir, "app.py")),
            "requirements": self.generate_requirements(os.path.join(output_dir, "requirements.txt")),
            "dockerfile": self.generate_dockerfile(os.path.join(output_dir, "Dockerfile")),
        }

        # Generate docker-compose.yml
        compose_content = f'''version: '3.8'

services:
  model-server:
    build: .
    ports:
      - "{self.port}:{self.port}"
    volumes:
      - ./model:/app/model
    environment:
      - CUDA_VISIBLE_DEVICES=0
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:{self.port}/health"]
      interval: 30s
      timeout: 10s
      retries: 3
'''

        compose_path = os.path.join(output_dir, "docker-compose.yml")
        with open(compose_path, "w") as f:
            f.write(compose_content)
        files["docker_compose"] = compose_path

        logger.info(f"Deployment bundle generated in: {output_dir}")
        return files
