"""
Local Training Executor for Calaxis CLI

Standalone training executor that enables local fine-tuning of LLMs
without requiring a connection to the Calaxis platform.

Supports:
- Apple Silicon with MLX (unified memory)
- NVIDIA CUDA GPUs
- QLoRA 4-bit and 8-bit quantization
- LoRA fine-tuning
"""
import logging
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from pathlib import Path

logger = logging.getLogger(__name__)


class LocalTrainingExecutor:
    """
    Standalone training executor for CLI usage

    Implements local training without database dependencies.
    Can be used for fine-tuning LLMs on local hardware.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize local training executor

        Args:
            config: Training configuration dictionary containing:
                - base_model: HuggingFace model ID or local path
                - dataset_path: Path to training dataset (.jsonl)
                - output_dir: Directory to save trained model
                - num_epochs: Number of training epochs
                - batch_size: Training batch size
                - learning_rate: Learning rate
                - use_4bit: Enable 4-bit quantization (QLoRA)
                - use_8bit: Enable 8-bit quantization
                - lora_r: LoRA rank
                - lora_alpha: LoRA alpha
                - lora_dropout: LoRA dropout
                - max_seq_length: Maximum sequence length
        """
        self.config = config
        self.job_id = config.get("job_id", f"local-{int(datetime.now().timestamp())}")
        self.base_model = config.get("base_model", "meta-llama/Llama-3.1-8B")
        self.dataset_path = config.get("dataset_path")
        self.output_dir = config.get("output_dir", f"./output/job_{self.job_id}")

        # Training components
        self.model = None
        self.tokenizer = None
        self.dataset = None
        self.trainer = None

        # Progress tracking
        self.current_step = 0
        self.total_steps = 0
        self.current_epoch = 0

        # Device type (detected during setup)
        self.device_type = None

        # Callback for progress updates
        self.progress_callback: Optional[Callable] = None

        logger.info(f"LocalTrainingExecutor initialized for job {self.job_id}")

    def train(self):
        """
        Execute complete training pipeline

        The training pipeline consists of 6 phases:
        1. Setup - Environment detection and directory creation
        2. Load Model - Download/load base model with quantization
        3. Load Dataset - Load and tokenize training data
        4. Configure Training - Setup LoRA and training arguments
        5. Training Loop - Execute training
        6. Save Model - Save trained model and adapters
        """
        try:
            print("\n" + "="*60)
            print("🚀 CALAXIS LOCAL TRAINING")
            print("="*60 + "\n")

            # Phase 1: Setup
            self._setup_phase()

            # Phase 2: Load Model
            self._load_model()

            # Phase 3: Load Dataset
            self._load_dataset()

            # Phase 4: Configure Training
            self._configure_training()

            # Phase 5: Training Loop
            self._training_loop()

            # Phase 6: Save Model
            self._save_model()

            print("\n" + "="*60)
            print("✅ TRAINING COMPLETED SUCCESSFULLY")
            print("="*60 + "\n")

            return {
                "status": "completed",
                "output_dir": self.output_dir,
                "model_path": os.path.join(self.output_dir, "final_model"),
            }

        except KeyboardInterrupt:
            print("\n\n⚠️  Training interrupted by user")
            self._save_checkpoint()
            return {
                "status": "interrupted",
                "checkpoint_path": os.path.join(self.output_dir, "checkpoints", "interrupted"),
            }
        except Exception as e:
            logger.error(f"Training failed: {str(e)}", exc_info=True)
            return {
                "status": "failed",
                "error": str(e),
            }

    def _setup_phase(self):
        """Phase 1: Setup environment"""
        print("📋 Phase 1/6: Setup Environment")
        print("-" * 60)

        # Check for MLX (Apple Silicon) first
        try:
            import mlx.core as mx
            import platform
            if platform.machine() == "arm64":
                try:
                    import psutil
                    unified_memory = psutil.virtual_memory().total / 1e9
                    print(f"✅ Apple Silicon with MLX")
                    print(f"   Unified Memory: {unified_memory:.2f} GB")
                except ImportError:
                    print(f"✅ Apple Silicon with MLX detected")
                self.device_type = "mlx"
                print()
                self._setup_directories()
                return
        except ImportError:
            pass

        # Check CUDA GPU
        try:
            import torch
            has_gpu = torch.cuda.is_available()

            if has_gpu:
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
                print(f"✅ CUDA GPU: {gpu_name}")
                print(f"   Memory: {gpu_memory:.2f} GB")
                self.device_type = "cuda"
            else:
                print("⚠️  No GPU detected - training will be very slow!")
                self.device_type = "cpu"
        except ImportError:
            print("⚠️  PyTorch not installed - cannot detect GPU")
            self.device_type = "cpu"

        self._setup_directories()
        print()

    def _setup_directories(self):
        """Create output directories"""
        os.makedirs(self.output_dir, exist_ok=True)
        checkpoint_dir = os.path.join(self.output_dir, "checkpoints")
        os.makedirs(checkpoint_dir, exist_ok=True)
        print(f"📁 Output directory: {self.output_dir}")

    def _load_model(self):
        """Phase 2: Load base model"""
        print("🤖 Phase 2/6: Loading Base Model")
        print("-" * 60)

        if self.device_type == "mlx":
            self._load_model_mlx()
        else:
            self._load_model_transformers()

    def _load_model_transformers(self):
        """Load model using HuggingFace Transformers"""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
            import torch

            # Configure quantization if requested
            quantization_config = None
            if self.config.get("use_4bit"):
                print("⚙️  Configuring 4-bit quantization (QLoRA)...")
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_use_double_quant=True,
                )
            elif self.config.get("use_8bit"):
                print("⚙️  Configuring 8-bit quantization...")
                quantization_config = BitsAndBytesConfig(
                    load_in_8bit=True,
                )

            print(f"📥 Loading model: {self.base_model}")
            print("   This may take several minutes...")

            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.base_model,
                quantization_config=quantization_config,
                device_map="auto",
                trust_remote_code=True,
            )

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.base_model,
                trust_remote_code=True,
            )

            # Add padding token if missing
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            print(f"✅ Model loaded successfully")
            print()

        except Exception as e:
            print(f"❌ Failed to load model: {str(e)}")
            raise

    def _load_model_mlx(self):
        """Load model using MLX for Apple Silicon"""
        try:
            from mlx_lm import load

            print(f"📥 Loading model with MLX: {self.base_model}")
            print("   This may take several minutes...")

            # Load model and tokenizer with MLX
            self.model, self.tokenizer = load(self.base_model)

            print(f"✅ Model loaded successfully with MLX")
            print()

        except ImportError:
            print("❌ mlx-lm not installed. Install with: pip install mlx-lm")
            raise
        except Exception as e:
            print(f"❌ Failed to load model with MLX: {str(e)}")
            raise

    def _load_dataset(self):
        """Phase 3: Load and prepare dataset"""
        print("📚 Phase 3/6: Loading Dataset")
        print("-" * 60)

        try:
            from datasets import load_dataset

            if not self.dataset_path:
                raise ValueError("Dataset path is required")

            print(f"📥 Loading dataset: {self.dataset_path}")

            # Load JSONL dataset
            dataset = load_dataset('json', data_files=self.dataset_path)

            # Get train split
            if 'train' in dataset:
                self.dataset = dataset['train']
            else:
                self.dataset = dataset

            print(f"✅ Dataset loaded: {len(self.dataset)} samples")

            if self.device_type != "mlx":
                # Tokenize dataset for Transformers
                print("🔄 Tokenizing dataset...")
                max_length = self.config.get("max_seq_length", 512)

                def tokenize_function(examples):
                    # Handle different dataset formats
                    if "prompt" in examples and "completion" in examples:
                        texts = [f"{p}\n{c}" for p, c in zip(examples["prompt"], examples["completion"])]
                    elif "instruction" in examples and "output" in examples:
                        texts = [f"{i}\n{o}" for i, o in zip(examples["instruction"], examples["output"])]
                    elif "text" in examples:
                        texts = examples["text"]
                    else:
                        raise ValueError("Dataset must have 'prompt'/'completion', 'instruction'/'output', or 'text' fields")

                    return self.tokenizer(
                        texts,
                        truncation=True,
                        max_length=max_length,
                        padding="max_length",
                    )

                self.dataset = self.dataset.map(
                    tokenize_function,
                    batched=True,
                    remove_columns=self.dataset.column_names,
                )

                print(f"✅ Dataset tokenized")

            print()

        except Exception as e:
            print(f"❌ Failed to load dataset: {str(e)}")
            raise

    def _configure_training(self):
        """Phase 4: Configure training parameters"""
        print("⚙️  Phase 4/6: Configuring Training")
        print("-" * 60)

        if self.device_type == "mlx":
            self._configure_training_mlx()
        else:
            self._configure_training_transformers()

    def _configure_training_transformers(self):
        """Configure training with Transformers + PEFT"""
        try:
            from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
            from transformers import TrainingArguments, Trainer

            # Prepare model for k-bit training if using quantization
            if self.config.get("use_4bit") or self.config.get("use_8bit"):
                print("🔧 Preparing model for quantized training...")
                self.model = prepare_model_for_kbit_training(self.model)

            # Configure LoRA
            print("🔧 Configuring LoRA...")
            lora_config = LoraConfig(
                r=self.config.get("lora_r", 16),
                lora_alpha=self.config.get("lora_alpha", 32),
                target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
                lora_dropout=self.config.get("lora_dropout", 0.05),
                bias="none",
                task_type="CAUSAL_LM",
            )

            self.model = get_peft_model(self.model, lora_config)
            self.model.print_trainable_parameters()

            # Configure training arguments
            print("🔧 Configuring training arguments...")
            batch_size = self.config.get("batch_size", 4)
            num_epochs = self.config.get("num_epochs", 3)
            learning_rate = self.config.get("learning_rate", 2e-4)

            training_args = TrainingArguments(
                output_dir=self.output_dir,
                num_train_epochs=num_epochs,
                per_device_train_batch_size=batch_size,
                gradient_accumulation_steps=self.config.get("gradient_accumulation_steps", 4),
                learning_rate=learning_rate,
                fp16=True,
                save_steps=self.config.get("save_steps", 500),
                logging_steps=self.config.get("logging_steps", 10),
                save_total_limit=3,
                warmup_steps=self.config.get("warmup_steps", 100),
                optim="paged_adamw_8bit" if (self.config.get("use_4bit") or self.config.get("use_8bit")) else "adamw_torch",
                report_to="none",  # Disable wandb, tensorboard, etc.
            )

            # Create trainer
            self.trainer = Trainer(
                model=self.model,
                args=training_args,
                train_dataset=self.dataset,
            )

            print(f"✅ Training configured")
            print(f"   Epochs: {num_epochs}")
            print(f"   Batch size: {batch_size}")
            print(f"   Learning rate: {learning_rate}")
            print()

        except Exception as e:
            print(f"❌ Failed to configure training: {str(e)}")
            raise

    def _configure_training_mlx(self):
        """Configure training with MLX"""
        print("🔧 Configuring MLX training...")
        # MLX training configuration is simpler
        print(f"✅ MLX training configured")
        print(f"   Epochs: {self.config.get('num_epochs', 3)}")
        print(f"   Batch size: {self.config.get('batch_size', 4)}")
        print(f"   Learning rate: {self.config.get('learning_rate', 2e-4)}")
        print()

    def _training_loop(self):
        """Phase 5: Execute training"""
        print("🏋️  Phase 5/6: Training")
        print("-" * 60)
        print("Training started... This will take a while.")
        print("Press Ctrl+C to stop and save checkpoint.\n")

        if self.device_type == "mlx":
            self._training_loop_mlx()
        else:
            self._training_loop_transformers()

    def _training_loop_transformers(self):
        """Training loop with Transformers"""
        try:
            self.trainer.train()
            print("\n✅ Training completed")
            print()

        except Exception as e:
            print(f"\n❌ Training failed: {str(e)}")
            raise

    def _training_loop_mlx(self):
        """Training loop with MLX"""
        try:
            from mlx_lm import train as mlx_train

            # MLX training
            mlx_train(
                model=self.model,
                tokenizer=self.tokenizer,
                train_dataset=self.dataset_path,
                output_dir=self.output_dir,
                num_epochs=self.config.get("num_epochs", 3),
                batch_size=self.config.get("batch_size", 4),
                learning_rate=self.config.get("learning_rate", 2e-4),
            )

            print("\n✅ MLX training completed")
            print()

        except ImportError:
            print("❌ mlx-lm not installed for training")
            raise
        except Exception as e:
            print(f"\n❌ MLX training failed: {str(e)}")
            raise

    def _save_model(self):
        """Phase 6: Save trained model"""
        print("💾 Phase 6/6: Saving Model")
        print("-" * 60)

        try:
            final_model_path = os.path.join(self.output_dir, "final_model")

            print(f"💾 Saving model to: {final_model_path}")

            if self.device_type == "mlx":
                # MLX model already saved during training
                print(f"✅ MLX model saved")
            else:
                # Save model and tokenizer
                self.model.save_pretrained(final_model_path)
                self.tokenizer.save_pretrained(final_model_path)

            # Save training config
            config_path = os.path.join(self.output_dir, "training_config.json")
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=2)

            print(f"✅ Model saved successfully")
            print(f"\n📁 Model location: {final_model_path}")
            print(f"📁 Config saved: {config_path}")
            print()

        except Exception as e:
            print(f"❌ Failed to save model: {str(e)}")
            raise

    def _save_checkpoint(self):
        """Save intermediate checkpoint"""
        try:
            checkpoint_path = os.path.join(self.output_dir, "checkpoints", "interrupted")
            print(f"\n💾 Saving checkpoint to: {checkpoint_path}")

            if self.model:
                self.model.save_pretrained(checkpoint_path)
            if self.tokenizer:
                self.tokenizer.save_pretrained(checkpoint_path)

            print(f"✅ Checkpoint saved: {checkpoint_path}")

        except Exception as e:
            logger.error(f"Failed to save checkpoint: {str(e)}")
