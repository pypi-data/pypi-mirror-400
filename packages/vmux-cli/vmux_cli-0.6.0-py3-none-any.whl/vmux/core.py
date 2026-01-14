"""Core functionality for vmux."""

import os
import re
import signal
import sys
import time
from pathlib import Path

import keyring

from .client import TupClient, INLINE_THRESHOLD
from .config import load_config
from .packager import package
from .ui import console, success, error

# Enable verbose timing with VMUX_DEBUG=1
DEBUG = os.environ.get("VMUX_DEBUG", "").lower() in ("1", "true", "yes")


def _debug(msg: str) -> None:
    """Print debug message with timestamp."""
    if DEBUG:
        console.print(f"[dim][{time.time():.3f}] {msg}[/dim]")


def _format_duration(seconds: float) -> str:
    """Format duration as human-readable string."""
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"{mins}m {secs:.0f}s"


def _format_bytes(size: int) -> str:
    """Format bytes as human-readable string."""
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    else:
        return f"{size / (1024 * 1024):.1f} MB"


def get_secrets() -> dict[str, str]:
    """Load secrets from system keychain."""
    config = load_config()
    secrets = {}
    for key in config.env.keys():
        value = keyring.get_password("vmux", key)
        if value:
            secrets[key] = value
    return secrets


def run_command(
    command: str,
    *,
    env_vars: dict[str, str] | None = None,
    detach: bool = False,
    ports: list[int] | None = None,
    directory: Path | str | None = None,
    runtime: str | None = None,
) -> str:
    """Run a command in the cloud.

    Args:
        command: Command to run
        env_vars: Environment variables to set
        detach: Return immediately after job starts (don't stream logs)
        ports: Ports to expose for preview URLs (empty = no preview)
        directory: Working directory (default: current directory)
        runtime: Force runtime ("python", "bun", "node") - auto-detected if None

    Returns:
        job_id
    """
    ports = ports or []
    t_start = time.time()
    directory = Path(directory) if directory else Path.cwd()
    env_vars = env_vars or {}

    # Auto-inject PORT env var for JS runtimes (Bun, Node)
    # This matches Vercel/Render behavior where PORT is set automatically
    if ports and "PORT" not in env_vars:
        from .deps import is_bun_project
        parts = command.split() if command and command.strip() else []
        first_word = parts[0] if parts else ""
        js_commands = ("node", "bun", "npm", "npx", "yarn", "pnpm", "deno")
        is_js_runtime = (
            runtime in ("bun", "node")
            or first_word in js_commands
            or is_bun_project(directory)
        )
        if is_js_runtime:
            env_vars["PORT"] = str(ports[0])
            _debug(f"Injected PORT={ports[0]} for JS runtime")

    # Package project (detects editables automatically)
    _debug("Starting package()")
    bundle = package(directory, command)
    _debug(f"package() done: {len(bundle.data)} bytes, {len(bundle.editables)} editables")

    t_bundled = time.time()
    bundle_size = len(bundle.data)

    # Show upload method in debug
    if bundle_size <= INLINE_THRESHOLD:
        _debug(f"Bundle size {_format_bytes(bundle_size)} <= {_format_bytes(INLINE_THRESHOLD)}, using inline upload")
    else:
        _debug(f"Bundle size {_format_bytes(bundle_size)} > {_format_bytes(INLINE_THRESHOLD)}, using R2 upload")

    config = load_config()

    # Merge secrets from keychain with env vars (env_vars takes precedence)
    _debug("Loading secrets")
    secrets = get_secrets()
    merged_env = {**secrets, **env_vars}  # env_vars overrides secrets
    _debug(f"Secrets loaded: {len(secrets)} keys")

    _debug(f"Total prep time: {time.time() - t_start:.2f}s")
    _debug("Connecting to API...")

    with TupClient(config) as client:
        job_id = None
        t_running = None  # When job reaches "running" status

        def handle_interrupt(sig: int, frame: object) -> None:
            """Handle Ctrl+C gracefully."""
            console.print()
            if job_id:
                console.print(f"\n[yellow]Detached from job {job_id}[/yellow]")
                console.print(f"[dim]Job is still running in the cloud.[/dim]\n")
                console.print(f"  [blue]vmux logs -f {job_id}[/blue]  - follow logs")
                console.print(f"  [blue]vmux ps[/blue]               - list jobs")
                console.print(f"  [blue]vmux stop {job_id}[/blue]     - stop job")
                console.print()
            sys.exit(0)

        signal.signal(signal.SIGINT, handle_interrupt)

        def on_upload_start(size: int, is_r2: bool) -> None:
            if is_r2:
                console.print(f"[dim]→ uploading to R2...[/dim]")
            else:
                console.print(f"[dim]→ uploading...[/dim]")

        try:
            for event in client.run(
                command=command,
                bundle_data=bundle.data,
                env_vars=merged_env or None,
                editables=bundle.editables,
                ports=ports,
                runtime=runtime,
                on_upload_start=on_upload_start,
            ):
                if "job_id" in event:
                    job_id = event["job_id"]
                    # Don't return early - wait for "running" status so setup completes

                # Preview URLs arrive early (before "running") - show them immediately
                if "preview_urls" in event:
                    preview_urls = event["preview_urls"]
                    if preview_urls:
                        total_time = time.time() - t_start
                        console.print()
                        for port, url in preview_urls.items():
                            console.print(f"[bold green]✓[/bold green] [link={url}]{url}[/link]")
                        console.print(f"[dim]  {_format_bytes(bundle_size)} deployed in {_format_duration(total_time)}[/dim]")
                        console.print()
                        # In detach mode with ports, we can return once we have the URLs
                        if detach and job_id:
                            console.print(f"[dim]vmux logs -f {job_id}[/dim]")
                            console.print(f"[dim]vmux attach {job_id}[/dim]")
                            console.print(f"[dim]vmux stop {job_id}[/dim]")
                            return job_id

                if "status" in event:
                    status = event["status"]

                    if status == "running":
                        t_running = time.time()
                        deploy_time = t_running - t_bundled
                        stats = f"[dim]({_format_bytes(bundle_size)} • {_format_duration(deploy_time)})[/dim]"

                        if detach:
                            # Detach mode - return now (URLs already shown if any)
                            success(f"Job started: {job_id} {stats}")
                            console.print(f"[blue]Follow: vmux logs -f {job_id}[/blue]")
                            return job_id

                        # Interactive mode - show stats when job starts running
                        console.print(f"\n[cyan]Job {job_id} running[/cyan] {stats}")
                        console.print()

                    elif status in ("provisioning", "initializing", "extracting", "installing", "starting"):
                        console.print(f"[dim]→ {status}...[/dim]")

                    elif status == "completed":
                        console.print()
                        total_time = time.time() - t_start
                        success(f"Done. [dim]({_format_duration(total_time)} total)[/dim]")

                    elif status == "failed":
                        console.print()
                        error(f"Failed (exit {event.get('exit_code', '?')})")
                        sys.exit(1)

                elif "log" in event:
                    # Filter out terminal focus escape sequences (^[[I, ^[[O)
                    log_text = re.sub(r'\x1b\[[IO]', '', event["log"])
                    if log_text:
                        console.print(log_text, end="")

                elif "error" in event:
                    error(event["error"])
                    sys.exit(1)
        finally:
            signal.signal(signal.SIGINT, signal.SIG_DFL)

        return job_id or ""
