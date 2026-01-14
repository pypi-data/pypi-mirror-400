"""CLI for vmux - run any command in the cloud."""

import sys
from pathlib import Path
import click

from .client import TupClient
from .ui import console, success, error, warning
from .config import load_config, save_config
from .core import run_command


def detect_framework_port() -> int:
    """Auto-detect the default port based on framework files in current directory.

    Returns:
        Port number based on detected framework, or 8000 as fallback.
    """
    cwd = Path.cwd()

    # Check for Vite (port 5173)
    if any(cwd.glob("vite.config.*")):
        return 5173

    # Check for Next.js (port 3000)
    if any(cwd.glob("next.config.*")):
        return 3000

    # Check package.json for hints
    package_json = cwd / "package.json"
    if package_json.exists():
        try:
            import json
            pkg = json.loads(package_json.read_text())
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}

            # Vite-based frameworks
            if "vite" in deps:
                return 5173
            # Next.js
            if "next" in deps:
                return 3000
            # Create React App / generic React
            if "react-scripts" in deps:
                return 3000
            # Express / generic Node
            if "express" in deps:
                return 3000
            # Bun default
            if any(cwd.glob("bun.lockb")) or any(cwd.glob("bunfig.toml")):
                return 3000
        except Exception:
            pass

    # Python frameworks default to 8000
    if any(cwd.glob("*.py")) or any(cwd.glob("requirements*.txt")) or any(cwd.glob("pyproject.toml")):
        return 8000

    # Default fallback
    return 8000


@click.group()
def cli() -> None:
    """Run any command in the cloud."""
    pass


@cli.command()
@click.option("--detach", "-d", is_flag=True, help="Return job ID without streaming logs")
@click.option("--port", "-p", multiple=True, type=int, help="Port to expose for preview URL (can be used multiple times)")
@click.option("--preview", is_flag=True, help="Expose port for preview URL (auto-detects port from framework)")
@click.option("--env", "-e", multiple=True, help="Environment variable (KEY=VALUE)")
@click.option("--runtime", "-r", type=click.Choice(["python", "bun", "node"]), help="Force runtime (auto-detected if not specified)")
@click.argument("command", nargs=-1, required=True)
def run(detach: bool, port: tuple[int, ...], preview: bool, env: tuple[str, ...], runtime: str | None, command: tuple[str, ...]) -> None:
    """Run a command in the cloud.

    \b
    Examples:
        vmux run python train.py              # ML job, no preview
        vmux run -d python long_job.py        # Background job
        vmux run --preview python server.py   # Web server on :8000
        vmux run -p 8000 python server.py     # Same as above
        vmux run -p 3000 -p 8000 npm run dev  # Multiple ports
        vmux run --preview bun run server.ts  # Bun web server
        vmux run -r bun npm run dev           # Force Bun runtime
    """
    env_vars = {}
    for e in env:
        if "=" not in e:
            raise click.BadParameter(f"Invalid format: {e}. Use KEY=VALUE")
        key, value = e.split("=", 1)
        env_vars[key] = value

    # Auto-detect leading KEY=VALUE args
    command = list(command)
    while command and "=" in command[0] and not command[0].startswith("-"):
        key, value = command.pop(0).split("=", 1)
        if key.isupper() or "_" in key:
            env_vars[key] = value
        else:
            command.insert(0, f"{key}={value}")
            break

    # Combine --preview with explicit -p ports
    # If --preview is used without -p, auto-detect port from framework
    ports = list(port)
    if preview and not ports:
        detected_port = detect_framework_port()
        ports.append(detected_port)

    try:
        run_command(" ".join(command), env_vars=env_vars or None, detach=detach, ports=ports, runtime=runtime)
    except Exception as e:
        error(str(e))
        sys.exit(1)


def _list_jobs(limit: int, all_jobs: bool = False) -> None:
    """Shared implementation for ps/ls."""
    from datetime import datetime

    config = load_config()
    with TupClient(config) as client:
        jobs = client.list_jobs(limit=limit)

        # Filter out completed/failed unless --all
        if not all_jobs:
            jobs = [j for j in jobs if j.get("status") in ("running", "pending")]

        if not jobs:
            warning("No running jobs." if not all_jobs else "No jobs found.")
            return

        # Sort by created_at ascending (oldest first, newest at bottom)
        jobs.sort(key=lambda j: j.get("created_at", ""))

        console.print()
        console.print(f"  {'ID':<12} {'STARTED':<12} {'COMMAND':<26} {'STATUS':<10}")
        console.print(f"  {'-'*12} {'-'*12} {'-'*26} {'-'*10}")

        for job in jobs:
            styles = {"running": "cyan", "completed": "green", "failed": "red", "pending": "yellow"}
            style = styles.get(job.get("status", ""), "white")
            cmd = (job.get("command", "")[:24] + "..") if len(job.get("command", "")) > 26 else job.get("command", "")

            # Format timestamp
            created = job.get("created_at", "")
            if created:
                try:
                    dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    age = datetime.now(dt.tzinfo) - dt
                    if age.days > 0:
                        time_str = f"{age.days}d ago"
                    elif age.seconds >= 3600:
                        time_str = f"{age.seconds // 3600}h ago"
                    elif age.seconds >= 60:
                        time_str = f"{age.seconds // 60}m ago"
                    else:
                        time_str = "just now"
                except Exception:
                    time_str = created[:10]
            else:
                time_str = "-"

            console.print(f"  {job['job_id']:<12} {time_str:<12} {cmd:<26} [{style}]{job.get('status', ''):<10}[/{style}]")

            # Show preview URLs for running jobs
            preview_urls = job.get("preview_urls", {})
            if preview_urls and job.get("status") == "running":
                for port, url in preview_urls.items():
                    console.print(f"  [dim]└─ :{port} → [link={url}]{url}[/link][/dim]")

        console.print()
        console.print(f"[dim]  Use 'vmux logs -f <id>' to follow, 'vmux stop <id>' to kill[/dim]")
        console.print()


@cli.command(name="ps")
@click.option("--limit", "-l", default=20, help="Number of jobs to show")
@click.option("--all", "-a", "all_jobs", is_flag=True, help="Show all jobs including completed/failed")
def ps_cmd(limit: int, all_jobs: bool) -> None:
    """List running jobs."""
    _list_jobs(limit, all_jobs)


# Hidden alias for ps
@cli.command(name="ls", hidden=True)
@click.option("--limit", "-l", default=20, help="Number of jobs to show")
@click.option("--all", "-a", "all_jobs", is_flag=True, help="Show all jobs including completed/failed")
def ls_cmd(limit: int, all_jobs: bool) -> None:
    """List running jobs."""
    _list_jobs(limit, all_jobs)


@cli.command()
@click.argument("job_ids", nargs=-1)
@click.option("--all", "-a", "stop_all", is_flag=True, help="Stop all running jobs")
def stop(job_ids: tuple[str, ...], stop_all: bool) -> None:
    """Stop one or more jobs.

    \b
    Examples:
        vmux stop abc123              # Stop one job
        vmux stop abc123 def456       # Stop multiple jobs
        vmux stop -a                  # Stop all running jobs
    """
    config = load_config()
    with TupClient(config) as client:
        if stop_all:
            jobs = client.list_jobs(limit=100)
            running = [j for j in jobs if j.get("status") == "running"]
            if not running:
                warning("No running jobs to stop.")
                return
            job_ids = tuple(j["job_id"] for j in running)
            console.print(f"Stopping {len(job_ids)} running jobs...")
        elif not job_ids:
            error("Specify job ID(s) or use --all")
            sys.exit(1)

        stopped = 0
        for job_id in job_ids:
            try:
                if client.stop_job(job_id):
                    console.print(f"  [green]✓[/green] {job_id}")
                    stopped += 1
                else:
                    console.print(f"  [red]✗[/red] {job_id} (failed)")
            except Exception as e:
                console.print(f"  [red]✗[/red] {job_id} ({e})")

        if stopped > 0:
            success(f"Stopped {stopped} job(s)")
        else:
            error("No jobs stopped")
            sys.exit(1)


@cli.command()
@click.argument("job_id")
def attach(job_id: str) -> None:
    """Attach to a running job's tmux session.

    Opens an interactive terminal connection to the job's tmux session.
    Use Ctrl+B,D to detach (job keeps running).

    \b
    Examples:
        vmux attach abc123        # Attach to job abc123
    """
    import asyncio
    from .terminal import run_attach

    config = load_config()
    if not config.auth_token:
        error("Not logged in. Run: vmux login")
        sys.exit(1)

    try:
        asyncio.run(run_attach(job_id, config))
    except KeyboardInterrupt:
        pass  # Disconnect message handled in terminal.py
    except Exception as e:
        error(f"Attach failed: {e}")
        sys.exit(1)


@cli.command()
@click.argument("job_id")
@click.option("--follow", "-f", is_flag=True, help="Follow log output in real-time")
def logs(job_id: str, follow: bool) -> None:
    """View logs for a job.

    \b
    Examples:
        vmux logs abc123        # Get current logs
        vmux logs -f abc123     # Follow logs (Ctrl+C to stop)
    """
    import time

    config = load_config()
    with TupClient(config) as client:
        try:
            if follow:
                console.print(f"[cyan]Following logs for {job_id}...[/cyan]")
                console.print("[dim]Ctrl+C to stop (job keeps running)[/dim]\n")
                last_len = 0
                while True:
                    try:
                        output = client.get_logs(job_id)
                        if len(output) > last_len:
                            console.print(output[last_len:], end="")
                            last_len = len(output)
                        time.sleep(0.5)
                    except KeyboardInterrupt:
                        console.print("\n[dim]Stopped following. Job continues running.[/dim]")
                        break
            else:
                output = client.get_logs(job_id)
                console.print(output)
        except Exception as e:
            error(f"Failed to get logs: {e}")
            sys.exit(1)


@cli.command()
def login() -> None:
    """Login with GitHub."""
    from .auth import device_flow_login

    try:
        result = device_flow_login()
        cfg = load_config()
        cfg.auth_token = result["access_token"]
        save_config(cfg)
        success("Logged in!")
    except Exception as e:
        error(str(e))
        sys.exit(1)


@cli.command()
def logout() -> None:
    """Logout."""
    cfg = load_config()
    cfg.auth_token = None
    save_config(cfg)
    success("Logged out.")


@cli.command()
def status() -> None:
    """Show global capacity status."""
    config = load_config()
    if not config.auth_token:
        error("Not logged in. Run: vmux login")
        sys.exit(1)

    with TupClient(config) as client:
        try:
            data = client.get_status()
            current = data.get("current_jobs", 0)
            max_jobs = data.get("max_jobs", 90)
            percent = data.get("capacity_percent", 0)

            # Color based on capacity
            if percent < 50:
                color = "green"
            elif percent < 80:
                color = "yellow"
            else:
                color = "red"

            console.print()
            console.print(f"  [dim]Capacity:[/dim]  [{color}]{current}[/{color}] / {max_jobs} jobs ({percent}%)")
            console.print()
        except Exception as e:
            error(f"Failed to get status: {e}")
            sys.exit(1)


@cli.command()
@click.argument("job_id")
def debug(job_id: str) -> None:
    """Debug a job - show tmux status, processes, and recent logs."""
    config = load_config()
    if not config.auth_token:
        error("Not logged in. Run: vmux login")
        sys.exit(1)

    with TupClient(config) as client:
        try:
            data = client.debug_job(job_id)
            console.print()
            for cmd, output in data.items():
                console.print(f"[cyan]$ {cmd}[/cyan]")
                console.print(output)
                console.print()
        except Exception as e:
            error(f"Debug failed: {e}")
            sys.exit(1)


@cli.command()
@click.option("--force", "-f", is_flag=True, help="Skip confirmation")
def prune(force: bool) -> None:
    """Remove completed/failed jobs from history.

    \b
    Examples:
        vmux prune           # Remove old jobs (asks for confirmation)
        vmux prune -f        # Remove without confirmation
    """
    config = load_config()
    with TupClient(config) as client:
        jobs = client.list_jobs(limit=200)
        stale = [j for j in jobs if j.get("status") in ("completed", "failed")]

        if not stale:
            warning("No completed/failed jobs to prune.")
            return

        console.print(f"Found {len(stale)} completed/failed jobs.")
        if not force:
            if not click.confirm("Remove from history?"):
                console.print("Cancelled.")
                return

        removed = 0
        for job in stale:
            try:
                # Stop will mark as failed and clean up
                client.stop_job(job["job_id"])
                removed += 1
            except Exception:
                pass  # Already gone or can't remove

        success(f"Pruned {removed} jobs")


@cli.command()
def whoami() -> None:
    """Show current user."""
    import httpx

    cfg = load_config()
    if not cfg.auth_token:
        warning("Not logged in.")
        return

    try:
        resp = httpx.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {cfg.auth_token}"},
        )
        if resp.status_code == 401:
            warning("Session expired. Run: vmux login")
            return
        console.print(f"Logged in as [green]{resp.json()['login']}[/green]")
    except Exception as e:
        error(str(e))


@cli.command()
def usage() -> None:
    """Show current month's usage."""
    config = load_config()
    if not config.auth_token:
        error("Not logged in. Run: vmux login")
        sys.exit(1)

    with TupClient(config) as client:
        try:
            data = client.get_usage()

            hours_used = data.get('hours_used', 0)
            hours_included = data.get('hours_included', 100)
            hours_remaining = data.get('hours_remaining', 100)
            percent = data.get('percent_used', 0)
            job_count = data.get('job_count', 0)
            plan_name = data.get('plan_name', 'Base')
            is_beta = data.get('beta', True)

            # Progress bar
            bar_width = 20
            filled = int(bar_width * percent / 100)
            empty = bar_width - filled

            if percent < 50:
                bar_color = "green"
            elif percent < 80:
                bar_color = "yellow"
            else:
                bar_color = "red"

            bar = f"[{bar_color}]{'█' * filled}[/{bar_color}][dim]{'░' * empty}[/dim]"

            console.print()

            # Holiday header
            if is_beta:
                console.print("[bold magenta]  ✨ vmux holiday beta - free through 2025! ✨[/bold magenta]")
                console.print()

            # Plan info
            console.print(f"  [dim]Plan:[/dim]  [bold]{plan_name}[/bold] [dim]({hours_included} hrs/mo)[/dim]")
            console.print()

            # The one metric
            console.print(f"  [dim]Hours used:[/dim]  [bold]{hours_used:.1f}[/bold] / {hours_included}")
            console.print(f"  {bar} {percent:.0f}%")
            console.print()

            # Remaining
            if hours_remaining > 0:
                console.print(f"  [green]🎁 {hours_remaining:.1f} hours remaining[/green]")
            else:
                console.print(f"  [red]⚠️  Limit reached - upgrade for more![/red]")
            console.print()

            # Job count
            console.print(f"  [dim]Jobs this month:[/dim] {job_count}")
            console.print()

            # Holiday footer
            if is_beta:
                console.print("  [dim]Happy holidays from the vmux team! 🎄[/dim]")
                console.print()

        except Exception as e:
            error(f"Failed to get usage: {e}")
            sys.exit(1)


@cli.group()
def secret() -> None:
    """Manage secrets for jobs."""
    pass


@secret.command(name="set")
@click.argument("key")
def secret_set(key: str) -> None:
    """Set a secret (prompts for value)."""
    import keyring

    value = click.prompt(f"Enter value for {key}", hide_input=True)
    keyring.set_password("vmux", key, value)

    # Track key name in config (values stay in keychain)
    cfg = load_config()
    cfg.env[key] = "(keychain)"
    save_config(cfg)
    success(f"Saved {key} to system keychain")


@secret.command(name="ls")
def secret_ls() -> None:
    """List stored secrets."""
    cfg = load_config()
    keys = list(cfg.env.keys())

    if not keys:
        warning("No secrets stored. Use: vmux secret set <KEY>")
        return

    console.print()
    for key in keys:
        console.print(f"  {key}")
    console.print()


@secret.command(name="rm")
@click.argument("key")
def secret_rm(key: str) -> None:
    """Remove a secret."""
    import keyring

    try:
        keyring.delete_password("vmux", key)
    except keyring.errors.PasswordDeleteError:
        pass  # May not exist in keyring if legacy

    # Remove from config tracking
    cfg = load_config()
    if key in cfg.env:
        del cfg.env[key]
        save_config(cfg)
        success(f"Removed {key}")
    else:
        error(f"Secret '{key}' not found")


@cli.group()
def claude() -> None:
    """Claude Code integration."""
    pass


@claude.command(name="install")
def claude_install() -> None:
    """Install vmux skill for Claude Code.

    Copies the vmux skill to ~/.claude/skills/vmux/ so Claude Code
    can use vmux commands via /vmux or natural language.
    """
    import shutil

    # Find the skill file bundled with vmux
    skill_source = Path(__file__).parent.parent / "claude" / "skills" / "vmux" / "SKILL.md"

    # Fallback: check if installed as package
    if not skill_source.exists():
        import importlib.resources
        try:
            # Python 3.9+
            files = importlib.resources.files("vmux")
            skill_source = Path(str(files / "claude" / "skills" / "vmux" / "SKILL.md"))
        except Exception:
            pass

    if not skill_source.exists():
        error("Skill file not found. Try reinstalling vmux.")
        sys.exit(1)

    # Install to ~/.claude/skills/vmux/
    skill_dest = Path.home() / ".claude" / "skills" / "vmux"
    skill_dest.mkdir(parents=True, exist_ok=True)

    dest_file = skill_dest / "SKILL.md"
    shutil.copy(skill_source, dest_file)

    success(f"Installed vmux skill to {dest_file}")
    console.print()
    console.print("[dim]Claude Code will now understand vmux commands.[/dim]")
    console.print("[dim]Try: 'deploy this with vmux' or '/vmux'[/dim]")


@claude.command(name="uninstall")
def claude_uninstall() -> None:
    """Remove vmux skill from Claude Code."""
    import shutil

    skill_dir = Path.home() / ".claude" / "skills" / "vmux"

    if skill_dir.exists():
        shutil.rmtree(skill_dir)
        success("Removed vmux skill from Claude Code")
    else:
        warning("vmux skill not installed")


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
