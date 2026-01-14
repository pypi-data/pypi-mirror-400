"""
Calaxis CLI WebSocket Client

Real-time training progress and log streaming via WebSocket.
Provides Rich-based terminal UI for progress display.
"""

import asyncio
import json
import logging
from typing import Optional, Callable, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import websockets
try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False

# Try to import Rich for terminal UI
try:
    from rich.console import Console
    from rich.live import Live
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.layout import Layout
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


class CLIWebSocketClient:
    """
    WebSocket client for real-time training updates.

    Features:
    - Real-time progress display with Rich UI
    - Log streaming with color coding
    - Automatic reconnection
    - Heartbeat keep-alive
    """

    def __init__(
        self,
        api_url: str,
        token: str,
        on_progress: Optional[Callable[[Dict], None]] = None,
        on_log: Optional[Callable[[Dict], None]] = None,
        on_status: Optional[Callable[[Dict], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ):
        """
        Initialize WebSocket client.

        Args:
            api_url: Calaxis API URL (http/https will be converted to ws/wss)
            token: JWT access token for authentication
            on_progress: Callback for progress updates
            on_log: Callback for log entries
            on_status: Callback for status changes
            on_error: Callback for errors
        """
        if not HAS_WEBSOCKETS:
            raise ImportError("websockets library required. Install with: pip install websockets")

        # Convert HTTP URL to WebSocket URL
        self.ws_url = api_url.replace("https://", "wss://").replace("http://", "ws://")
        self.token = token

        # Callbacks
        self.on_progress = on_progress
        self.on_log = on_log
        self.on_status = on_status
        self.on_error = on_error

        # State
        self._running = False
        self._websocket = None
        self._console = Console() if HAS_RICH else None

    async def connect(self, job_id: str) -> bool:
        """
        Connect to WebSocket for job updates.

        Args:
            job_id: Training job ID to monitor

        Returns:
            bool: True if connected successfully
        """
        uri = f"{self.ws_url}/ws/cli/jobs/{job_id}?token={self.token}"

        try:
            self._websocket = await websockets.connect(
                uri,
                ping_interval=20,
                ping_timeout=10,
                close_timeout=5,
            )
            self._running = True
            logger.info(f"Connected to job {job_id}")
            return True

        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            if self.on_error:
                self.on_error(f"Connection failed: {e}")
            return False

    async def disconnect(self):
        """Gracefully disconnect from WebSocket."""
        self._running = False

        if self._websocket:
            try:
                await self._websocket.send(json.dumps({"type": "unsubscribe"}))
                await self._websocket.close()
            except:
                pass
            finally:
                self._websocket = None

    async def listen(self):
        """
        Listen for messages from WebSocket.

        Dispatches messages to appropriate callbacks based on type.
        """
        if not self._websocket:
            raise RuntimeError("Not connected")

        try:
            async for message in self._websocket:
                if not self._running:
                    break

                try:
                    data = json.loads(message)
                    msg_type = data.get("type", "unknown")

                    if msg_type == "progress" and self.on_progress:
                        self.on_progress(data)
                    elif msg_type == "log" and self.on_log:
                        self.on_log(data)
                    elif msg_type == "status" and self.on_status:
                        self.on_status(data)
                    elif msg_type == "error" and self.on_error:
                        self.on_error(data.get("message", "Unknown error"))
                    elif msg_type == "heartbeat":
                        # Keep-alive, no action needed
                        pass
                    elif msg_type == "connected":
                        logger.info("WebSocket connected, waiting for updates...")

                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON message: {e}")

        except websockets.ConnectionClosed as e:
            logger.info(f"WebSocket closed: {e}")
            if self.on_error:
                self.on_error(f"Connection closed: {e}")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            if self.on_error:
                self.on_error(str(e))

    async def send_ping(self):
        """Send ping to keep connection alive."""
        if self._websocket:
            try:
                await self._websocket.send(json.dumps({"type": "ping"}))
            except:
                pass

    async def request_status(self):
        """Request current job status."""
        if self._websocket:
            try:
                await self._websocket.send(json.dumps({"type": "get_status"}))
            except:
                pass


class TrainingProgressDisplay:
    """
    Rich-based terminal display for training progress.

    Shows:
    - Progress bar with percentage
    - Current epoch/step
    - Loss and learning rate
    - Recent log entries
    - Status indicators
    """

    def __init__(self, job_id: str, job_name: str = None):
        """
        Initialize progress display.

        Args:
            job_id: Training job ID
            job_name: Optional human-readable job name
        """
        if not HAS_RICH:
            raise ImportError("rich library required. Install with: pip install rich")

        self.job_id = job_id
        self.job_name = job_name or job_id[:8]
        self.console = Console()

        # State
        self.current_epoch = 0
        self.total_epochs = 0
        self.current_step = 0
        self.total_steps = 0
        self.loss = 0.0
        self.learning_rate = 0.0
        self.status = "connecting"
        self.logs = []  # Recent log entries
        self.max_logs = 5

        # Progress
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40),
            TaskProgressColumn(),
            console=self.console,
        )
        self.task_id = None

    def update_progress(self, data: Dict):
        """Update progress from WebSocket message."""
        self.current_epoch = data.get("epoch", self.current_epoch)
        self.total_epochs = data.get("total_epochs", self.total_epochs)
        self.current_step = data.get("step", self.current_step)
        self.total_steps = data.get("total_steps", self.total_steps)
        self.loss = data.get("loss", self.loss)
        self.learning_rate = data.get("learning_rate", self.learning_rate)

        # Calculate overall progress
        if self.total_epochs > 0 and self.total_steps > 0:
            epoch_progress = self.current_epoch / self.total_epochs
            step_progress = self.current_step / self.total_steps
            overall = (epoch_progress + step_progress / self.total_epochs) * 100
        elif self.total_epochs > 0:
            overall = (self.current_epoch / self.total_epochs) * 100
        else:
            overall = 0

        if self.task_id is not None:
            self.progress.update(
                self.task_id,
                completed=overall,
                description=self._get_description()
            )

    def update_status(self, data: Dict):
        """Update status from WebSocket message."""
        self.status = data.get("status", self.status)

        if data.get("current_epoch"):
            self.current_epoch = data["current_epoch"]
        if data.get("total_epochs"):
            self.total_epochs = data["total_epochs"]
        if data.get("loss"):
            self.loss = data["loss"]

    def add_log(self, data: Dict):
        """Add log entry."""
        level = data.get("level", "INFO")
        message = data.get("message", "")
        timestamp = data.get("timestamp", datetime.utcnow().isoformat())

        # Color code by level
        if level == "ERROR":
            color = "red"
        elif level == "WARNING":
            color = "yellow"
        elif level == "DEBUG":
            color = "dim"
        else:
            color = "white"

        log_entry = {
            "level": level,
            "message": message,
            "timestamp": timestamp,
            "color": color
        }

        self.logs.append(log_entry)
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)

    def _get_description(self) -> str:
        """Build progress description string."""
        parts = [f"[bold cyan]{self.job_name}[/]"]

        if self.total_epochs > 0:
            parts.append(f"Epoch {self.current_epoch}/{self.total_epochs}")

        if self.loss > 0:
            parts.append(f"Loss: {self.loss:.4f}")

        if self.learning_rate > 0:
            parts.append(f"LR: {self.learning_rate:.2e}")

        return " | ".join(parts)

    def render(self) -> Panel:
        """Render current state as Rich Panel."""
        # Build content table
        table = Table.grid(expand=True)
        table.add_column()

        # Status line
        status_colors = {
            "connecting": "yellow",
            "pending": "yellow",
            "running": "green",
            "completed": "blue",
            "failed": "red",
        }
        status_color = status_colors.get(self.status, "white")
        status_text = Text()
        status_text.append("Status: ", style="bold")
        status_text.append(self.status.upper(), style=status_color)
        table.add_row(status_text)

        # Progress line
        if self.total_epochs > 0:
            progress_text = Text()
            progress_text.append(f"Progress: ", style="bold")
            progress_text.append(f"Epoch {self.current_epoch}/{self.total_epochs}")
            if self.total_steps > 0:
                progress_text.append(f" | Step {self.current_step}/{self.total_steps}")
            table.add_row(progress_text)

        # Metrics
        if self.loss > 0:
            metrics_text = Text()
            metrics_text.append("Metrics: ", style="bold")
            metrics_text.append(f"Loss={self.loss:.4f}")
            if self.learning_rate > 0:
                metrics_text.append(f" | LR={self.learning_rate:.2e}")
            table.add_row(metrics_text)

        # Recent logs
        if self.logs:
            table.add_row("")
            table.add_row(Text("Recent Logs:", style="bold"))
            for log in self.logs[-3:]:
                log_text = Text()
                log_text.append(f"[{log['level']}] ", style=log['color'])
                log_text.append(log['message'])
                table.add_row(log_text)

        return Panel(
            table,
            title=f"Training Job: {self.job_name}",
            border_style="cyan"
        )


async def watch_training_job(
    api_url: str,
    token: str,
    job_id: str,
    job_name: str = None,
    show_logs: bool = True,
):
    """
    Watch a training job with real-time progress display.

    This is the main entry point for CLI --watch functionality.

    Args:
        api_url: Calaxis API URL
        token: JWT access token
        job_id: Training job ID
        job_name: Optional human-readable name
        show_logs: Whether to show log entries
    """
    if not HAS_RICH:
        # Fallback to simple output
        await _watch_simple(api_url, token, job_id)
        return

    console = Console()
    display = TrainingProgressDisplay(job_id, job_name)

    # Setup callbacks
    def on_progress(data):
        display.update_progress(data)

    def on_status(data):
        display.update_status(data)

        # Check for completion
        status = data.get("status")
        if status in ("completed", "failed", "cancelled"):
            console.print(f"\n[bold]Training {status}![/]")
            if status == "completed":
                model_path = data.get("model_path")
                if model_path:
                    console.print(f"Model saved to: {model_path}")

    def on_log(data):
        if show_logs:
            display.add_log(data)

    def on_error(message):
        console.print(f"[red]Error: {message}[/]")

    # Create client
    client = CLIWebSocketClient(
        api_url=api_url,
        token=token,
        on_progress=on_progress,
        on_status=on_status,
        on_log=on_log,
        on_error=on_error,
    )

    # Connect
    console.print(f"Connecting to job [cyan]{job_id[:8]}...[/]")

    if not await client.connect(job_id):
        console.print("[red]Failed to connect. Check your token and job ID.[/]")
        return

    console.print("[green]Connected! Watching for updates...[/]\n")

    # Display with Live refresh
    try:
        with Live(display.render(), refresh_per_second=4, console=console) as live:
            # Initial status request
            await client.request_status()

            # Listen for updates
            listen_task = asyncio.create_task(client.listen())

            while display.status not in ("completed", "failed", "cancelled"):
                live.update(display.render())
                await asyncio.sleep(0.25)

                if listen_task.done():
                    break

            # Final update
            live.update(display.render())

    except KeyboardInterrupt:
        console.print("\n[yellow]Stopped watching.[/]")
    finally:
        await client.disconnect()


async def _watch_simple(api_url: str, token: str, job_id: str):
    """Simple text-based progress for terminals without Rich."""

    last_progress = {}

    def on_progress(data):
        nonlocal last_progress
        if data != last_progress:
            epoch = data.get("epoch", 0)
            step = data.get("step", 0)
            loss = data.get("loss", 0)
            print(f"Progress: Epoch {epoch} | Step {step} | Loss: {loss:.4f}")
            last_progress = data

    def on_status(data):
        status = data.get("status")
        print(f"Status: {status}")
        if status in ("completed", "failed"):
            print(f"Training {status}!")

    def on_log(data):
        level = data.get("level", "INFO")
        message = data.get("message", "")
        print(f"[{level}] {message}")

    def on_error(message):
        print(f"ERROR: {message}")

    client = CLIWebSocketClient(
        api_url=api_url,
        token=token,
        on_progress=on_progress,
        on_status=on_status,
        on_log=on_log,
        on_error=on_error,
    )

    if not await client.connect(job_id):
        print("Failed to connect")
        return

    print(f"Connected to job {job_id}")

    try:
        await client.listen()
    except KeyboardInterrupt:
        print("\nStopped watching.")
    finally:
        await client.disconnect()


async def stream_training_logs(
    api_url: str,
    token: str,
    job_id: str,
    tail: int = 100,
):
    """
    Stream training logs in real-time.

    Args:
        api_url: Calaxis API URL
        token: JWT access token
        job_id: Training job ID
        tail: Number of recent logs to fetch initially
    """
    if not HAS_WEBSOCKETS:
        raise ImportError("websockets library required")

    console = Console() if HAS_RICH else None
    ws_url = api_url.replace("https://", "wss://").replace("http://", "ws://")
    uri = f"{ws_url}/ws/cli/logs/{job_id}?token={token}&tail={tail}"

    try:
        async with websockets.connect(uri) as websocket:
            if console:
                console.print(f"[green]Streaming logs for job {job_id[:8]}...[/]\n")
            else:
                print(f"Streaming logs for job {job_id[:8]}...")

            async for message in websocket:
                data = json.loads(message)
                msg_type = data.get("type")

                if msg_type == "log_batch":
                    # Historical logs
                    for log in data.get("logs", []):
                        _print_log_entry(log, console)

                elif msg_type == "log":
                    _print_log_entry(data, console)

    except KeyboardInterrupt:
        if console:
            console.print("\n[yellow]Stopped streaming.[/]")
        else:
            print("\nStopped streaming.")


def _print_log_entry(log: Dict, console=None):
    """Print a single log entry."""
    level = log.get("level", "INFO")
    message = log.get("message", "")
    timestamp = log.get("timestamp", "")

    # Format timestamp
    if timestamp:
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            timestamp = dt.strftime("%H:%M:%S")
        except:
            timestamp = timestamp[:8]

    if console:
        # Rich output with colors
        level_colors = {
            "ERROR": "red",
            "WARNING": "yellow",
            "DEBUG": "dim",
            "INFO": "white",
        }
        color = level_colors.get(level, "white")
        console.print(f"[dim]{timestamp}[/] [{color}]{level:7}[/] {message}")
    else:
        # Plain text
        print(f"{timestamp} {level:7} {message}")
