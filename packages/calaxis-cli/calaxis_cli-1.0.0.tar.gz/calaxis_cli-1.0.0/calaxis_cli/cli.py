#!/usr/bin/env python3
"""
Calaxis AI Platform - Local Training & Deployment CLI

Main entry point for the calaxis command-line tool.

Usage:
    calaxis --help                    # Show all commands
    calaxis login                     # Login to Calaxis Platform
    calaxis logout                    # Logout from platform
    calaxis whoami                    # Show current user
    calaxis system check              # Check system compatibility
    calaxis train --config config.yaml # Start local training
    calaxis train --watch JOB_ID      # Watch remote job progress
    calaxis deploy --model ./model    # Deploy model locally
    calaxis upload --model ./model    # Upload trained model to Calaxis Platform
"""
import argparse
import asyncio
import getpass
import json
import sys
from pathlib import Path


def print_banner():
    """Print Calaxis CLI banner"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║           CALAXIS AI PLATFORM - LOCAL CLI                ║
║                                                           ║
║   Local fine-tuning and deployment for LLMs               ║
║   Supports: Apple Silicon (MLX) | NVIDIA CUDA             ║
╚═══════════════════════════════════════════════════════════╝
"""
    print(banner)


def cmd_system_check(args):
    """Check system compatibility"""
    from .utils.system_check import get_system_report, assess_training_feasibility

    print_banner()
    print("🔍 Checking system compatibility...\n")

    report = get_system_report()

    # Display system info
    print("=" * 60)
    print("SYSTEM INFORMATION")
    print("=" * 60)
    system = report.get("system", {})
    print(f"Platform:       {system.get('platform', 'Unknown')} {system.get('platform_release', '')}")
    print(f"Python:         {system.get('python_version', 'Unknown')}")
    print(f"CPU Cores:      {system.get('cpu_count', 'Unknown')} (Physical: {system.get('cpu_count_physical', 'Unknown')})")
    print(f"RAM:            {system.get('ram_total_gb', 'Unknown')} GB (Available: {system.get('ram_available_gb', 'Unknown')} GB)")
    print()

    # Display GPU/MLX info
    print("=" * 60)
    print("GPU / ACCELERATION")
    print("=" * 60)

    mlx = report.get("mlx", {})
    gpu = report.get("gpu", {})

    if mlx.get("available"):
        print(f"✅ Apple Silicon MLX")
        print(f"   MLX Version:    {mlx.get('mlx_version', 'Unknown')}")
        print(f"   Unified Memory: {mlx.get('unified_memory_gb', 'Unknown')} GB")
    elif mlx.get("is_apple_silicon"):
        print("⚠️  Apple Silicon detected but MLX not installed")
        print("   Install with: pip install mlx mlx-lm")
    elif gpu.get("available"):
        print(f"✅ CUDA GPU")
        print(f"   CUDA Version:   {gpu.get('cuda_version', 'Unknown')}")
        print(f"   Driver Version: {gpu.get('driver_version', 'Unknown')}")
        print(f"   GPU Count:      {gpu.get('count', 0)}")
        for device in gpu.get("devices", []):
            print(f"   - {device.get('name')}: {device.get('total_memory_gb')} GB (Compute {device.get('compute_capability')})")
    else:
        print("❌ No GPU detected")
    print()

    # Display disk info
    print("=" * 60)
    print("DISK SPACE")
    print("=" * 60)
    disk = report.get("disk", {})
    print(f"Total:     {disk.get('total_gb', 'Unknown')} GB")
    print(f"Free:      {disk.get('free_gb', 'Unknown')} GB")
    print(f"Used:      {disk.get('percent_used', 'Unknown')}%")
    print()

    # Training capability
    print("=" * 60)
    print("TRAINING CAPABILITY")
    print("=" * 60)
    print(report.get("message", "Unknown"))

    if args.model_size:
        print(f"\n📊 Assessment for {args.model_size} model:")
        assessment = assess_training_feasibility(args.model_size)
        assessment_data = assessment.get("assessment", {})

        if assessment_data.get("feasible"):
            print(f"✅ Training is FEASIBLE")
            print(f"   Recommended method: {assessment_data.get('recommended_method')}")
        else:
            print(f"❌ Training is NOT feasible on this system")
            print(f"   Warnings:")
            for warning in assessment_data.get("warnings", []):
                print(f"   - {warning}")

            if "cloud_alternatives" in assessment_data:
                print(f"\n   Cloud alternatives:")
                for alt in assessment_data.get("cloud_alternatives", []):
                    print(f"   - {alt.get('provider')}: {alt.get('description')}")

    print()
    return 0


def cmd_train(args):
    """Start local training"""
    from .utils.config import load_config, validate_config
    from .training.executor import LocalTrainingExecutor

    print_banner()

    # Load configuration
    if args.config:
        print(f"📄 Loading configuration: {args.config}")
        config = load_config(args.config)
    else:
        # Use command-line arguments
        config = {
            "base_model": args.model or "meta-llama/Llama-3.1-8B",
            "dataset_path": args.dataset,
            "output_dir": args.output or "./output",
            "num_epochs": args.epochs or 3,
            "batch_size": args.batch_size or 4,
            "learning_rate": args.learning_rate or 2e-4,
            "use_4bit": args.quantization == "4bit",
            "use_8bit": args.quantization == "8bit",
            "lora_r": args.lora_r or 16,
            "lora_alpha": args.lora_alpha or 32,
            "max_seq_length": args.max_length or 512,
        }

    # Validate configuration
    validation = validate_config(config, "training")
    if not validation["valid"]:
        print("❌ Configuration validation failed:")
        for error in validation["errors"]:
            print(f"   - {error}")
        return 1

    if validation["warnings"]:
        print("⚠️  Configuration warnings:")
        for warning in validation["warnings"]:
            print(f"   - {warning}")

    # Start training
    executor = LocalTrainingExecutor(config)
    result = executor.train()

    if result.get("status") == "completed":
        print(f"\n✅ Training completed!")
        print(f"   Model saved to: {result.get('model_path')}")
        return 0
    elif result.get("status") == "interrupted":
        print(f"\n⚠️  Training interrupted")
        print(f"   Checkpoint saved to: {result.get('checkpoint_path')}")
        return 130
    else:
        print(f"\n❌ Training failed: {result.get('error')}")
        return 1


def cmd_deploy(args):
    """Deploy model locally"""
    from .deployment.fastapi_executor import FastAPIModelServer
    from .deployment.torchserve_executor import TorchServeModelServer

    print_banner()
    print(f"🚀 Deploying model: {args.model}")
    print(f"   Server type: {args.server}")
    print(f"   Port: {args.port}")
    print()

    if args.server == "fastapi":
        server = FastAPIModelServer(
            model_path=args.model,
            model_type=args.model_type or "huggingface",
            host=args.host or "0.0.0.0",
            port=args.port or 8080,
        )

        if args.generate_only:
            # Generate deployment bundle
            output_dir = args.output or "./deployment"
            files = server.generate_deployment_bundle(output_dir)
            print(f"✅ Deployment bundle generated:")
            for name, path in files.items():
                print(f"   - {name}: {path}")
            return 0
        else:
            # Start server
            print("Starting FastAPI server...")
            process = server.start_server(reload=args.reload)
            print(f"✅ Server started on http://{args.host or '0.0.0.0'}:{args.port or 8080}")
            print("   Press Ctrl+C to stop")

            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n⚠️  Stopping server...")
                process.terminate()

            return 0

    elif args.server == "torchserve":
        server = TorchServeModelServer(
            model_store_dir=args.model_store or "/tmp/calaxis/torchserve/model-store",
            host=args.host or "localhost",
            inference_port=args.port or 8080,
        )

        if args.generate_only:
            # Create model archive
            mar_file = server.create_huggingface_archive(
                model_name=Path(args.model).name,
                model_path=args.model,
            )
            print(f"✅ Model archive created: {mar_file}")
            return 0
        else:
            # Start TorchServe
            print("Starting TorchServe server...")
            process = server.start_server()
            print(f"✅ TorchServe started")
            print(f"   Inference: http://{args.host or 'localhost'}:{args.port or 8080}")
            print("   Press Ctrl+C to stop")

            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n⚠️  Stopping TorchServe...")
                server.stop_server()

            return 0

    else:
        print(f"❌ Unknown server type: {args.server}")
        return 1


def cmd_upload(args):
    """Upload model to Calaxis Platform"""
    from .utils.api_client import CalaxisAPIClient

    print_banner()
    print(f"📤 Uploading model: {args.model}")
    print()

    # Check if model exists
    model_path = Path(args.model)
    if not model_path.exists():
        print(f"❌ Model path not found: {args.model}")
        return 1

    # Initialize API client
    try:
        client = CalaxisAPIClient(
            api_url=args.api_url,
            api_key=args.api_key,
        )
    except ImportError as e:
        print(f"❌ {e}")
        return 1

    # Validate API key
    if not client.api_key:
        print("❌ API key required. Set CALAXIS_API_KEY environment variable or use --api-key")
        return 1

    print("🔐 Validating API key...")
    if not client.validate_api_key():
        print("❌ Invalid API key")
        return 1

    print("✅ API key valid")

    # Upload model
    try:
        print("📤 Uploading model (this may take a while for large models)...")
        result = client.upload_model(
            model_path=str(model_path),
            model_name=args.name or model_path.name,
            description=args.description or "",
            tags=args.tags.split(",") if args.tags else None,
        )

        print(f"\n✅ Model uploaded successfully!")
        print(f"   Model ID: {result.get('model_id')}")
        print(f"   Name: {result.get('name')}")
        return 0

    except Exception as e:
        print(f"\n❌ Upload failed: {e}")
        return 1


def cmd_init(args):
    """Initialize a new training project"""
    from .utils.config import create_sample_config

    print_banner()
    print(f"📁 Initializing Calaxis project in: {args.directory or '.'}")
    print()

    output_dir = args.directory or "."

    # Create sample config
    config_path = create_sample_config(output_dir, "training")
    print(f"✅ Created training config: {config_path}")

    # Create sample dataset
    sample_dataset = [
        {"prompt": "What is machine learning?", "completion": "Machine learning is a subset of artificial intelligence that enables systems to learn from data."},
        {"prompt": "Explain neural networks.", "completion": "Neural networks are computing systems inspired by biological neural networks in the brain."},
    ]

    dataset_path = Path(output_dir) / "sample_dataset.jsonl"
    with open(dataset_path, "w") as f:
        for item in sample_dataset:
            f.write(json.dumps(item) + "\n")
    print(f"✅ Created sample dataset: {dataset_path}")

    print(f"\n🎉 Project initialized!")
    print(f"\nNext steps:")
    print(f"  1. Edit {config_path} to configure your training")
    print(f"  2. Replace {dataset_path} with your training data")
    print(f"  3. Run: calaxis train --config {config_path}")
    print()

    return 0


def cmd_login(args):
    """Login to Calaxis Platform"""
    from .auth import get_auth_manager

    print_banner()
    print("🔐 Login to Calaxis Platform\n")

    auth = get_auth_manager(api_url=args.api_url)

    # Check if already logged in
    if auth.is_authenticated():
        user_info = auth.get_user_info()
        print(f"Already logged in as: {user_info.get('email')}")
        if not args.force:
            print("Use --force to re-login")
            return 0

    # Get credentials
    if args.api_key:
        # API key authentication
        try:
            result = auth.login(email=None, password=None, api_key=args.api_key)
            print(f"\n✅ Logged in successfully!")
            print(f"   User: {result.get('email')}")
            print(f"   Tier: {result.get('tier')}")
            return 0
        except Exception as e:
            print(f"\n❌ Login failed: {e}")
            return 1
    else:
        # Interactive login
        email = args.email or input("Email: ")
        password = args.password or getpass.getpass("Password: ")

        try:
            result = auth.login(email=email, password=password)
            print(f"\n✅ Logged in successfully!")
            print(f"   User: {result.get('email')}")
            print(f"   Tier: {result.get('tier')}")
            return 0
        except ValueError as e:
            print(f"\n❌ Login failed: {e}")
            return 1
        except Exception as e:
            print(f"\n❌ Connection error: {e}")
            return 1


def cmd_logout(args):
    """Logout from Calaxis Platform"""
    from .auth import get_auth_manager

    print_banner()

    auth = get_auth_manager()

    if auth.logout():
        print("✅ Logged out successfully")
        return 0
    else:
        print("❌ Logout failed")
        return 1


def cmd_whoami(args):
    """Show current user"""
    from .auth import get_auth_manager

    auth = get_auth_manager()

    if not auth.is_authenticated():
        print("Not logged in. Use 'calaxis login' to authenticate.")
        return 1

    user_info = auth.get_user_info()

    print(f"Logged in as: {user_info.get('email')}")
    print(f"User ID:      {user_info.get('user_id')}")
    print(f"Tier:         {user_info.get('tier')}")
    print(f"Expires:      {user_info.get('expires_at')}")
    print(f"API URL:      {auth.get_api_url()}")

    return 0


def cmd_jobs(args):
    """List or manage training jobs"""
    from .auth import get_auth_manager

    auth = get_auth_manager()

    if not auth.is_authenticated():
        print("Not logged in. Use 'calaxis login' first.")
        return 1

    import requests

    headers = auth.get_auth_headers()
    api_url = auth.get_api_url()

    if args.jobs_command == "list":
        # List jobs
        try:
            response = requests.get(
                f"{api_url}/api/cli/v1/training/jobs",
                headers=headers,
                params={"status": args.status, "limit": args.limit or 20}
            )
            response.raise_for_status()
            data = response.json()

            jobs = data.get("jobs", [])
            if not jobs:
                print("No training jobs found.")
                return 0

            print(f"{'ID':<36} {'Name':<20} {'Status':<12} {'Progress':<10}")
            print("-" * 80)

            for job in jobs:
                job_id = job.get("id", "")[:36]
                name = job.get("name", "")[:20]
                status = job.get("status", "")[:12]
                progress = f"{job.get('progress', 0):.1f}%"
                print(f"{job_id} {name:<20} {status:<12} {progress:<10}")

            return 0

        except Exception as e:
            print(f"Error fetching jobs: {e}")
            return 1

    elif args.jobs_command == "status":
        # Get job status
        if not args.job_id:
            print("Job ID required. Use: calaxis jobs status JOB_ID")
            return 1

        try:
            response = requests.get(
                f"{api_url}/api/cli/v1/training/jobs/{args.job_id}",
                headers=headers
            )
            response.raise_for_status()
            job = response.json()

            print(f"Job ID:       {job.get('id')}")
            print(f"Name:         {job.get('name')}")
            print(f"Status:       {job.get('status')}")
            print(f"Progress:     {job.get('progress', 0):.1f}%")
            print(f"Epoch:        {job.get('current_epoch', 0)}/{job.get('total_epochs', 0)}")
            print(f"Step:         {job.get('current_step', 0)}/{job.get('total_steps', 'N/A')}")
            print(f"Loss:         {job.get('loss', 'N/A')}")
            print(f"Created:      {job.get('created_at')}")
            print(f"Started:      {job.get('started_at', 'Not started')}")

            if job.get("error_message"):
                print(f"Error:        {job.get('error_message')}")

            return 0

        except Exception as e:
            print(f"Error fetching job: {e}")
            return 1

    elif args.jobs_command == "watch":
        # Watch job progress in real-time
        if not args.job_id:
            print("Job ID required. Use: calaxis jobs watch JOB_ID")
            return 1

        print_banner()
        print(f"📺 Watching job: {args.job_id}\n")

        try:
            from .websocket_client import watch_training_job

            asyncio.run(watch_training_job(
                api_url=api_url,
                token=auth.get_token(),
                job_id=args.job_id,
                show_logs=not args.no_logs
            ))
            return 0

        except ImportError as e:
            print(f"WebSocket support not available: {e}")
            print("Install with: pip install websockets rich")
            return 1
        except Exception as e:
            print(f"Error watching job: {e}")
            return 1

    elif args.jobs_command == "logs":
        # Stream job logs
        if not args.job_id:
            print("Job ID required. Use: calaxis jobs logs JOB_ID")
            return 1

        print(f"📜 Streaming logs for job: {args.job_id}\n")

        try:
            from .websocket_client import stream_training_logs

            asyncio.run(stream_training_logs(
                api_url=api_url,
                token=auth.get_token(),
                job_id=args.job_id,
                tail=args.tail or 100
            ))
            return 0

        except ImportError as e:
            print(f"WebSocket support not available: {e}")
            return 1
        except Exception as e:
            print(f"Error streaming logs: {e}")
            return 1

    elif args.jobs_command == "cancel":
        # Cancel job
        if not args.job_id:
            print("Job ID required. Use: calaxis jobs cancel JOB_ID")
            return 1

        try:
            response = requests.post(
                f"{api_url}/api/cli/v1/training/jobs/{args.job_id}/cancel",
                headers=headers
            )
            response.raise_for_status()
            print(f"✅ Job {args.job_id} cancelled")
            return 0

        except Exception as e:
            print(f"Error cancelling job: {e}")
            return 1

    else:
        print("Unknown jobs command. Use: calaxis jobs --help")
        return 1


def cmd_remote_train(args):
    """Create and start a remote training job"""
    from .auth import get_auth_manager

    auth = get_auth_manager()

    if not auth.is_authenticated():
        print("Not logged in. Use 'calaxis login' first.")
        return 1

    import requests

    print_banner()
    print("🚀 Creating remote training job\n")

    headers = auth.get_auth_headers()
    api_url = auth.get_api_url()

    # Build job config
    config = {
        "name": args.name or f"cli-job-{args.model.split('/')[-1]}",
        "base_model": args.model,
        "num_epochs": args.epochs or 3,
        "batch_size": args.batch_size or 4,
        "learning_rate": args.learning_rate or 2e-4,
        "use_lora": True,
        "lora_r": args.lora_r or 16,
        "lora_alpha": args.lora_alpha or 32,
        "quantization": args.quantization or "4bit",
    }

    if args.dataset_id:
        config["dataset_id"] = args.dataset_id

    try:
        # Create job
        print("Creating job...")
        response = requests.post(
            f"{api_url}/api/cli/v1/training/jobs",
            headers=headers,
            json={"config": config}
        )
        response.raise_for_status()
        job = response.json()
        job_id = job.get("id")

        print(f"✅ Job created: {job_id}")

        if args.start:
            # Start job
            print("Starting job...")
            start_response = requests.post(
                f"{api_url}/api/cli/v1/training/jobs/{job_id}/start",
                headers=headers
            )
            start_response.raise_for_status()
            print("✅ Job started")

            if args.watch:
                # Watch progress
                print("\n📺 Watching job progress...\n")

                try:
                    from .websocket_client import watch_training_job

                    asyncio.run(watch_training_job(
                        api_url=api_url,
                        token=auth.get_token(),
                        job_id=job_id,
                        job_name=config["name"]
                    ))
                except ImportError:
                    print("WebSocket not available. Check status with: calaxis jobs status " + job_id)
        else:
            print(f"\nTo start the job, run:")
            print(f"  calaxis jobs start {job_id}")
            print(f"\nTo watch progress, run:")
            print(f"  calaxis jobs watch {job_id}")

        return 0

    except Exception as e:
        print(f"Error creating job: {e}")
        return 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Calaxis AI Platform - Local Training & Deployment CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  calaxis login                         # Login to Calaxis Platform
  calaxis logout                        # Logout from platform
  calaxis whoami                        # Show current user
  calaxis system check                  # Check system compatibility
  calaxis system check --model-size 7B  # Check for specific model
  calaxis train --config config.yaml    # Train locally with config file
  calaxis remote-train --model llama-3 --start --watch  # Train on platform
  calaxis jobs list                     # List training jobs
  calaxis jobs watch JOB_ID             # Watch job progress
  calaxis deploy --model ./model        # Deploy model locally
  calaxis upload --model ./model        # Upload to platform
  calaxis init                          # Initialize new project

For more info, visit: https://docs.calaxis.ai/cli
"""
    )

    parser.add_argument("--version", action="version", version="calaxis-cli 1.0.0")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # =========================================================================
    # Authentication Commands
    # =========================================================================

    # Login command
    login_parser = subparsers.add_parser("login", help="Login to Calaxis Platform")
    login_parser.add_argument("--email", "-e", help="Email address")
    login_parser.add_argument("--password", "-p", help="Password (or use interactive prompt)")
    login_parser.add_argument("--api-key", "-k", help="API key for automated login")
    login_parser.add_argument("--api-url", help="API URL (default: https://api.calaxis.ai)")
    login_parser.add_argument("--force", "-f", action="store_true", help="Force re-login")

    # Logout command
    subparsers.add_parser("logout", help="Logout from Calaxis Platform")

    # Whoami command
    subparsers.add_parser("whoami", help="Show current authenticated user")

    # =========================================================================
    # System Commands
    # =========================================================================

    system_parser = subparsers.add_parser("system", help="System commands")
    system_subparsers = system_parser.add_subparsers(dest="system_command")

    check_parser = system_subparsers.add_parser("check", help="Check system compatibility")
    check_parser.add_argument("--model-size", "-m", help="Model size to assess (7B, 13B, 70B)")

    # =========================================================================
    # Training Commands
    # =========================================================================

    # Local train command
    train_parser = subparsers.add_parser("train", help="Start local training")
    train_parser.add_argument("--config", "-c", help="Path to training config file (YAML or JSON)")
    train_parser.add_argument("--model", "-m", help="Base model name or path")
    train_parser.add_argument("--dataset", "-d", help="Path to training dataset")
    train_parser.add_argument("--output", "-o", help="Output directory")
    train_parser.add_argument("--epochs", "-e", type=int, help="Number of epochs")
    train_parser.add_argument("--batch-size", "-b", type=int, help="Batch size")
    train_parser.add_argument("--learning-rate", "-lr", type=float, help="Learning rate")
    train_parser.add_argument("--quantization", "-q", choices=["4bit", "8bit", "none"], default="4bit", help="Quantization (default: 4bit)")
    train_parser.add_argument("--lora-r", type=int, help="LoRA rank")
    train_parser.add_argument("--lora-alpha", type=int, help="LoRA alpha")
    train_parser.add_argument("--max-length", type=int, help="Max sequence length")

    # Remote train command
    remote_train_parser = subparsers.add_parser("remote-train", help="Create remote training job on platform")
    remote_train_parser.add_argument("--model", "-m", required=True, help="Base model name")
    remote_train_parser.add_argument("--dataset-id", help="Dataset UUID from platform")
    remote_train_parser.add_argument("--name", "-n", help="Job name")
    remote_train_parser.add_argument("--epochs", "-e", type=int, help="Number of epochs")
    remote_train_parser.add_argument("--batch-size", "-b", type=int, help="Batch size")
    remote_train_parser.add_argument("--learning-rate", "-lr", type=float, help="Learning rate")
    remote_train_parser.add_argument("--quantization", "-q", choices=["4bit", "8bit", "none"], default="4bit", help="Quantization")
    remote_train_parser.add_argument("--lora-r", type=int, help="LoRA rank")
    remote_train_parser.add_argument("--lora-alpha", type=int, help="LoRA alpha")
    remote_train_parser.add_argument("--start", "-s", action="store_true", help="Start job immediately")
    remote_train_parser.add_argument("--watch", "-w", action="store_true", help="Watch job progress after starting")

    # =========================================================================
    # Jobs Commands
    # =========================================================================

    jobs_parser = subparsers.add_parser("jobs", help="Manage training jobs")
    jobs_subparsers = jobs_parser.add_subparsers(dest="jobs_command")

    # jobs list
    jobs_list_parser = jobs_subparsers.add_parser("list", help="List training jobs")
    jobs_list_parser.add_argument("--status", choices=["pending", "running", "completed", "failed"], help="Filter by status")
    jobs_list_parser.add_argument("--limit", "-l", type=int, help="Limit results")

    # jobs status
    jobs_status_parser = jobs_subparsers.add_parser("status", help="Get job status")
    jobs_status_parser.add_argument("job_id", help="Job UUID")

    # jobs watch
    jobs_watch_parser = jobs_subparsers.add_parser("watch", help="Watch job progress in real-time")
    jobs_watch_parser.add_argument("job_id", help="Job UUID")
    jobs_watch_parser.add_argument("--no-logs", action="store_true", help="Hide log entries")

    # jobs logs
    jobs_logs_parser = jobs_subparsers.add_parser("logs", help="Stream job logs")
    jobs_logs_parser.add_argument("job_id", help="Job UUID")
    jobs_logs_parser.add_argument("--tail", "-t", type=int, help="Number of recent logs to fetch")

    # jobs cancel
    jobs_cancel_parser = jobs_subparsers.add_parser("cancel", help="Cancel a running job")
    jobs_cancel_parser.add_argument("job_id", help="Job UUID")

    # =========================================================================
    # Deployment Commands
    # =========================================================================

    deploy_parser = subparsers.add_parser("deploy", help="Deploy model locally")
    deploy_parser.add_argument("--model", "-m", required=True, help="Path to model")
    deploy_parser.add_argument("--server", "-s", choices=["fastapi", "torchserve"], default="fastapi", help="Server type")
    deploy_parser.add_argument("--model-type", "-t", choices=["huggingface", "pytorch", "onnx"], default="huggingface", help="Model type")
    deploy_parser.add_argument("--host", help="Server host")
    deploy_parser.add_argument("--port", "-p", type=int, help="Server port")
    deploy_parser.add_argument("--model-store", help="TorchServe model store directory")
    deploy_parser.add_argument("--generate-only", "-g", action="store_true", help="Generate deployment files only")
    deploy_parser.add_argument("--output", "-o", help="Output directory for generated files")
    deploy_parser.add_argument("--reload", action="store_true", help="Enable auto-reload (development)")

    # =========================================================================
    # Upload Command
    # =========================================================================

    upload_parser = subparsers.add_parser("upload", help="Upload model to Calaxis Platform")
    upload_parser.add_argument("--model", "-m", required=True, help="Path to model")
    upload_parser.add_argument("--name", "-n", help="Model name")
    upload_parser.add_argument("--description", "-d", help="Model description")
    upload_parser.add_argument("--tags", help="Comma-separated tags")
    upload_parser.add_argument("--api-url", help="Calaxis API URL")
    upload_parser.add_argument("--api-key", help="Calaxis API key")

    # =========================================================================
    # Init Command
    # =========================================================================

    init_parser = subparsers.add_parser("init", help="Initialize a new training project")
    init_parser.add_argument("directory", nargs="?", help="Project directory")

    # =========================================================================
    # Parse and Execute
    # =========================================================================

    args = parser.parse_args()

    if args.command == "login":
        return cmd_login(args)
    elif args.command == "logout":
        return cmd_logout(args)
    elif args.command == "whoami":
        return cmd_whoami(args)
    elif args.command == "system":
        if args.system_command == "check":
            return cmd_system_check(args)
        else:
            system_parser.print_help()
            return 1
    elif args.command == "train":
        return cmd_train(args)
    elif args.command == "remote-train":
        return cmd_remote_train(args)
    elif args.command == "jobs":
        if args.jobs_command:
            return cmd_jobs(args)
        else:
            jobs_parser.print_help()
            return 1
    elif args.command == "deploy":
        return cmd_deploy(args)
    elif args.command == "upload":
        return cmd_upload(args)
    elif args.command == "init":
        return cmd_init(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
