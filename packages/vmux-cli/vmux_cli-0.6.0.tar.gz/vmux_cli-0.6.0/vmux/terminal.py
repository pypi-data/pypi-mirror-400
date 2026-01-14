"""Terminal handling for vmux attach command.

Implements raw terminal mode and WebSocket proxying for interactive PTY sessions.
"""

import asyncio
import json
import os
import signal
import sys
import termios
import tty
from typing import TYPE_CHECKING

import websockets
from websockets.exceptions import ConnectionClosed

if TYPE_CHECKING:
    from .config import VmuxConfig


# ANSI color codes for xmux-style output
class Colors:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Colors
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    MAGENTA = "\033[35m"
    BLUE = "\033[34m"

    # Background
    BG_DARK = "\033[48;5;235m"


def print_attach_header(job_id: str) -> None:
    """Print a colorful xmux-style header when attaching."""
    c = Colors
    width = 60

    print(f"\033[2J\033[H", end="")  # Clear screen
    print(f"{c.CYAN}{c.BOLD}{'=' * width}{c.RESET}")
    print(f"{c.CYAN}{c.BOLD}  VMUX ATTACH: {c.GREEN}{job_id}{c.RESET}")
    print(f"{c.CYAN}{c.BOLD}{'=' * width}{c.RESET}")
    print()
    print(f"{c.DIM}  Connecting to cloud container...{c.RESET}", end="", flush=True)


def print_attach_connected(job_id: str) -> None:
    """Print connected message with instructions."""
    c = Colors
    width = 60

    print(f"\033[2J\033[H", end="")  # Clear screen
    print(f"{c.GREEN}{c.BOLD}{'=' * width}{c.RESET}")
    print(f"{c.GREEN}{c.BOLD}  ✓ Connected to {job_id}{c.RESET}")
    print(f"{c.GREEN}{c.BOLD}{'=' * width}{c.RESET}")
    print()
    print(f"{c.CYAN}  Keyboard shortcuts:{c.RESET}")
    print(f"{c.DIM}  • Ctrl+B, D    - Detach (job keeps running){c.RESET}")
    print(f"{c.DIM}  • Ctrl+B, 0-9  - Switch tmux windows{c.RESET}")
    print(f"{c.DIM}  • exit         - Exit container shell{c.RESET}")
    print()
    print(f"{c.DIM}{'─' * width}{c.RESET}")
    print()


def print_attach_disconnected(job_id: str) -> None:
    """Print disconnected message."""
    c = Colors
    print()
    print(f"{c.YELLOW}{'─' * 60}{c.RESET}")
    print(f"{c.YELLOW}  Detached from {job_id}{c.RESET}")
    print(f"{c.DIM}  Job continues running. Re-attach with: vmux attach {job_id}{c.RESET}")
    print(f"{c.YELLOW}{'─' * 60}{c.RESET}")
    print()


def get_terminal_size() -> tuple[int, int]:
    """Get terminal size as (cols, rows)."""
    try:
        size = os.get_terminal_size()
        return size.columns, size.lines
    except OSError:
        return 80, 24


async def run_attach(job_id: str, config: "VmuxConfig") -> None:
    """Attach to a job's tmux session via WebSocket PTY.

    This function:
    1. Unsets TMUX env var so container tmux sessions work
    2. Puts terminal in raw mode (no echo, no line buffering)
    3. Opens WebSocket to worker's /jobs/<id>/attach endpoint
    4. Forwards stdin → WebSocket → PTY and PTY → WebSocket → stdout
    5. Handles terminal resize (SIGWINCH)
    """
    if not config.auth_token:
        raise ValueError("Not authenticated")

    # CRITICAL: Unset TMUX so container tmux sessions work
    # When user runs vmux from inside a local tmux (like xmux), the $TMUX
    # env var propagates through the PTY, causing "sessions should be nested"
    # errors when trying to attach to container tmux sessions
    old_tmux = os.environ.pop("TMUX", None)

    # Build WebSocket URL from API URL
    api_url = config.api_url
    if api_url.startswith("https://"):
        ws_url = "wss://" + api_url[8:]
    elif api_url.startswith("http://"):
        ws_url = "ws://" + api_url[7:]
    else:
        ws_url = "wss://" + api_url

    cols, rows = get_terminal_size()
    ws_url = f"{ws_url}/jobs/{job_id}/attach?cols={cols}&rows={rows}"

    # Save terminal settings to restore later
    old_settings = termios.tcgetattr(sys.stdin.fileno())

    # Print colorful header
    print_attach_header(job_id)

    try:
        async with websockets.connect(
            ws_url,
            additional_headers={"Authorization": f"Bearer {config.auth_token}"},
        ) as ws:
            # Wait for connected message with spinner
            spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
            frame_idx = 0

            async def show_spinner() -> None:
                nonlocal frame_idx
                while True:
                    print(f"\r{Colors.DIM}  Connecting to cloud container... {spinner_frames[frame_idx]}{Colors.RESET}", end="", flush=True)
                    frame_idx = (frame_idx + 1) % len(spinner_frames)
                    await asyncio.sleep(0.1)

            spinner_task = asyncio.create_task(show_spinner())
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=30.0)  # Increased timeout for cold containers
            finally:
                spinner_task.cancel()
                try:
                    await spinner_task
                except asyncio.CancelledError:
                    pass
                print("\r" + " " * 50 + "\r", end="")  # Clear spinner line

            data = json.loads(msg)

            if data.get("type") == "error":
                raise Exception(data.get("message", "Connection failed"))

            if data.get("type") != "connected":
                raise Exception(f"Unexpected response: {data}")

            # Print connected message with shortcuts
            print_attach_connected(job_id)

            # Put terminal in raw mode
            tty.setraw(sys.stdin.fileno())

            # Setup resize handler
            resize_event = asyncio.Event()

            def handle_resize(signum: int, frame: object) -> None:
                resize_event.set()

            old_handler = signal.signal(signal.SIGWINCH, handle_resize)

            try:
                await _run_pty_loop(ws, resize_event)
            finally:
                signal.signal(signal.SIGWINCH, old_handler)

    except ConnectionClosed:
        pass  # Normal disconnection
    except asyncio.TimeoutError:
        raise Exception("Connection timeout")
    finally:
        # Restore terminal settings
        try:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_settings)
        except (OSError, ValueError):
            pass  # Terminal may be in bad state

        # Print disconnect message - stdout may be closed after PTY loop
        try:
            # Reopen stdout if it was closed by the PTY loop
            if sys.stdout.closed:
                sys.stdout = open("/dev/tty", "w")
            print_attach_disconnected(job_id)
        except (OSError, ValueError):
            pass  # Can't print, terminal is gone

        # Restore TMUX env var if it was set
        if old_tmux is not None:
            os.environ["TMUX"] = old_tmux


async def _run_pty_loop(
    ws: websockets.WebSocketClientProtocol,
    resize_event: asyncio.Event,
) -> None:
    """Run the PTY I/O loop.

    Concurrently handles:
    - Reading from stdin and sending to WebSocket
    - Receiving from WebSocket and writing to stdout
    - Terminal resize events

    Uses asyncio StreamWriter for proper flow-controlled stdout writes,
    avoiding BlockingIOError when terminal can't keep up with rapid output.
    """
    loop = asyncio.get_event_loop()

    # Setup async stdout writer with proper flow control
    # This prevents BlockingIOError by using drain() to wait when buffer is full
    write_transport, write_protocol = await loop.connect_write_pipe(
        lambda: asyncio.streams.FlowControlMixin(loop),
        sys.stdout.buffer,
    )
    stdout_writer = asyncio.StreamWriter(write_transport, write_protocol, None, loop)

    async def read_stdin() -> None:
        """Read from stdin and send to WebSocket."""
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)

        try:
            while True:
                # Read available data (non-blocking)
                data = await reader.read(1024)
                if not data:
                    break

                await ws.send(json.dumps({
                    "type": "input",
                    "data": data.decode("utf-8", errors="replace"),
                }))
        except (ConnectionClosed, asyncio.CancelledError):
            pass

    async def write_stdout() -> None:
        """Receive from WebSocket and write to stdout with flow control."""
        try:
            async for msg in ws:
                data = json.loads(msg)

                if data.get("type") == "output":
                    # Write PTY output to stdout using flow-controlled writer
                    output = data.get("data", "")
                    stdout_writer.write(output.encode("utf-8"))
                    # drain() waits if buffer is full - never blocks or drops data
                    await stdout_writer.drain()

                elif data.get("type") == "exit":
                    # PTY exited
                    break

                elif data.get("type") == "error":
                    # Server error
                    raise Exception(data.get("message", "Server error"))

        except (ConnectionClosed, asyncio.CancelledError):
            pass

    async def handle_resize() -> None:
        """Handle terminal resize events."""
        try:
            while True:
                await resize_event.wait()
                resize_event.clear()

                cols, rows = get_terminal_size()
                await ws.send(json.dumps({
                    "type": "resize",
                    "cols": cols,
                    "rows": rows,
                }))
        except (ConnectionClosed, asyncio.CancelledError):
            pass

    # Run all tasks concurrently
    stdin_task = asyncio.create_task(read_stdin())
    stdout_task = asyncio.create_task(write_stdout())
    resize_task = asyncio.create_task(handle_resize())

    try:
        # Wait for any task to complete
        # This happens when server closes connection, PTY exits, or stdin closes
        done, pending = await asyncio.wait(
            [stdin_task, stdout_task, resize_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        # Cancel remaining tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    except asyncio.CancelledError:
        for task in [stdin_task, stdout_task, resize_task]:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    finally:
        # Clean up stdout writer
        stdout_writer.close()
        try:
            await stdout_writer.wait_closed()
        except Exception:
            pass
