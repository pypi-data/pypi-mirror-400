"""Instance management commands for RAG Memory multi-instance support.

This module provides CLI commands for managing multiple RAG Memory instances.
Each instance has its own PostgreSQL, Neo4j, MCP server, and backup service
with isolated volumes and ports.

Commands:
    rag instance start <name>   - Create/start an instance
    rag instance stop <name>    - Stop an instance (preserve data)
    rag instance delete <name>  - Delete instance and all data
    rag instance list           - List all instances with status
    rag instance status <name>  - Detailed status of an instance
    rag instance logs <name>    - View logs for an instance
"""

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Tuple

import click
import platformdirs
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from src.core.instance_registry import InstanceRegistry, get_instance_registry
from src.core.instance_init import (
    get_docker_compose_command,
    run_command,
    wait_for_databases,
    run_initialization,
)

console = Console()


def get_config_dir() -> Path:
    """Get the RAG Memory system config directory.

    Uses OS-standard location, respects RAG_CONFIG_PATH if set.
    Always skips repo-local ./config/ directory.
    """
    from src.core.config_loader import get_system_config_dir
    return get_system_config_dir()


def get_compose_file() -> Path:
    """Get path to the instance compose template.

    Returns:
        Path to docker-compose.instance.yml

    Raises:
        FileNotFoundError: If compose template not found
    """
    config_dir = get_config_dir()

    # Check system config directory (deployed by setup.py)
    system_compose = config_dir / 'docker-compose.instance.yml'
    if system_compose.exists():
        return system_compose

    # Fall back to repository location (for development)
    repo_compose = (
        Path(__file__).parent.parent.parent
        / 'deploy' / 'docker' / 'compose' / 'docker-compose.instance.yml'
    )
    if repo_compose.exists():
        return repo_compose

    raise FileNotFoundError(
        "docker-compose.instance.yml not found. Please run setup.py first.\n"
        f"  Expected locations:\n"
        f"    System: {system_compose}\n"
        f"    Repo: {repo_compose}"
    )


def check_docker_available() -> Tuple[bool, str]:
    """Check if Docker is installed and running.

    Returns:
        Tuple of (available: bool, error_message: str)
    """
    code, _, _ = run_command(["docker", "--version"])
    if code != 0:
        return False, "Docker is not installed. Install Docker Desktop from https://docker.com"

    code, _, _ = run_command(["docker", "ps"])
    if code != 0:
        return False, "Docker daemon is not running. Start Docker Desktop and try again."

    return True, ""


def get_instance_env(instance: dict, config_dir: Path) -> dict:
    """Build environment variables for docker-compose.

    Args:
        instance: Instance dict from registry
        config_dir: Path to config directory

    Returns:
        Environment dict for docker-compose
    """
    from src.core.config_loader import get_instance_config

    ports = instance['ports']
    instance_name = instance['name']

    # Load instance configuration from config.yaml
    config_path = get_config_dir() / 'config.yaml'
    import yaml
    with open(config_path) as f:
        config_data = yaml.safe_load(f)

    instance_config = config_data.get('instances', {}).get(instance_name, {})

    # Start with current environment
    env = os.environ.copy()

    # Add instance-specific variables
    env.update({
        'INSTANCE_NAME': instance_name,
        'POSTGRES_PORT': str(ports['postgres']),
        'NEO4J_BOLT_PORT': str(ports['neo4j_bolt']),
        'NEO4J_HTTP_PORT': str(ports['neo4j_http']),
        'MCP_PORT': str(ports['mcp']),
        'RAG_CONFIG_DIR': str(config_dir),
        'BACKUP_ARCHIVE_PATH': str(config_dir / 'backups' / instance_name),
        # Add Neo4j credentials from config
        'NEO4J_USER': instance_config.get('neo4j_user', 'neo4j'),
        'NEO4J_PASSWORD': instance_config.get('neo4j_password', 'graphiti-password'),
        # Add PostgreSQL credentials from config
        'POSTGRES_USER': 'raguser',
        'POSTGRES_PASSWORD': 'ragpassword',
        'POSTGRES_DB': 'rag_memory',
    })

    # Apply any config overrides
    for key, value in instance.get('config_overrides', {}).items():
        env[key] = str(value)

    return env


def run_compose_command(
    compose_file: Path,
    instance_name: str,
    args: list,
    env: dict
) -> Tuple[int, str, str]:
    """Run a docker-compose command for an instance.

    Args:
        compose_file: Path to docker-compose.instance.yml
        instance_name: Instance name (for project name)
        args: Additional docker-compose arguments
        env: Environment variables

    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    docker_compose = get_docker_compose_command()
    cmd = docker_compose + [
        "-p", f"rag-memory-{instance_name}",
        "-f", str(compose_file),
    ] + args

    return run_command(cmd, env=env)


def get_container_status(container_name: str) -> str:
    """Get status of a container.

    Args:
        container_name: Full container name

    Returns:
        Status string or "Not running"
    """
    code, stdout, _ = run_command([
        "docker", "ps", "-a",
        "--filter", f"name=^{container_name}$",
        "--format", "{{.Status}}"
    ])

    if code == 0 and stdout.strip():
        return stdout.strip()
    return "Not running"


def format_status_display(status: str) -> str:
    """Format container status for display.

    Args:
        status: Raw status string from docker

    Returns:
        Rich-formatted status string
    """
    if status == "Not running":
        return "[red]✗ Not running[/red]"
    elif "Up" in status:
        if "healthy" in status.lower():
            return f"[green]✓ {status}[/green]"
        elif "unhealthy" in status.lower():
            return f"[red]✗ {status}[/red]"
        else:
            return f"[yellow]⚠ {status}[/yellow]"
    elif "Exited" in status:
        return f"[red]✗ {status}[/red]"
    else:
        return f"[dim]{status}[/dim]"


@click.group(name='instance')
def instance_group():
    """Manage RAG Memory instances.

    Each instance is a complete stack with isolated databases and ports.
    """
    pass


@instance_group.command(name='start')
@click.argument('name', required=False)
@click.option('--all', 'start_all', is_flag=True, help='Start all instances')
@click.option('--wait/--no-wait', default=True, help='Wait for services to be healthy')
@click.option('--timeout', default=300, help='Timeout in seconds when waiting')
def start_command(name: str, start_all: bool, wait: bool, timeout: int):
    """Start or create a RAG Memory instance.

    If the instance doesn't exist in the registry, it will be created with
    auto-assigned ports. However, the instance MUST have configuration in
    config.yaml (created by setup.py) to start successfully.

    NAME is the unique instance identifier (e.g., "primary", "research").
    Use --all to start all configured instances.
    """
    if not name and not start_all:
        console.print("[bold red]✗ Either provide an instance NAME or use --all[/bold red]")
        sys.exit(1)

    if name and start_all:
        console.print("[bold red]✗ Cannot use both NAME and --all[/bold red]")
        sys.exit(1)

    if start_all:
        from src.core.config_loader import list_configured_instances
        instances = list_configured_instances(use_system_config=True)
        if not instances:
            console.print("[bold yellow]No instances configured[/bold yellow]")
            sys.exit(0)

        console.print(f"[bold blue]Starting {len(instances)} instance(s)...[/bold blue]\n")
        failed = []
        for instance_name in instances:
            console.print(f"[dim]{'='*60}[/dim]")
            console.print(f"[bold]Instance: {instance_name}[/bold]\n")
            try:
                _start_instance(instance_name, wait, timeout)
            except SystemExit:
                failed.append(instance_name)
                continue

        console.print(f"\n[dim]{'='*60}[/dim]")
        if failed:
            console.print(f"\n[bold red]✗ Failed to start {len(failed)} instance(s): {', '.join(failed)}[/bold red]")
            sys.exit(1)
        else:
            console.print(f"\n[bold green]✓ All {len(instances)} instance(s) started successfully[/bold green]")
        return

    _start_instance(name, wait, timeout)


def _start_instance(name: str, wait: bool, timeout: int):
    """Internal function to start a single instance."""
    from src.core.config_loader import get_instance_config, list_configured_instances

    # Check if instance is already running
    mcp_container = f"rag-memory-mcp-{name}"
    postgres_container = f"rag-memory-postgres-{name}"
    neo4j_container = f"rag-memory-neo4j-{name}"

    mcp_status = get_container_status(mcp_container)
    postgres_status = get_container_status(postgres_container)
    neo4j_status = get_container_status(neo4j_container)

    # Check if all containers are healthy/running
    if ("healthy" in mcp_status.lower() or "Up" in mcp_status) and \
       ("healthy" in postgres_status.lower() or "Up" in postgres_status) and \
       ("healthy" in neo4j_status.lower() or "Up" in neo4j_status):
        console.print(f"[bold yellow]Instance '{name}' is already running[/bold yellow]")
        console.print("[dim]Use 'rag instance restart' to restart it[/dim]")
        return

    # Check Docker
    available, error = check_docker_available()
    if not available:
        console.print(f"[bold red]✗ {error}[/bold red]")
        sys.exit(1)

    # Get compose file
    try:
        compose_file = get_compose_file()
    except FileNotFoundError as e:
        console.print(f"[bold red]✗ {e}[/bold red]")
        sys.exit(1)

    # Check if instance has configuration in config.yaml
    configured_instances = list_configured_instances(use_system_config=True)
    if name not in configured_instances:
        console.print(f"[bold red]✗ Instance '{name}' not found in config.yaml[/bold red]")
        console.print()
        if configured_instances:
            console.print("[yellow]Available instances:[/yellow]")
            for inst in configured_instances:
                console.print(f"  - {inst}")
            console.print()
        console.print("[yellow]To create a new instance, run:[/yellow]")
        console.print("[cyan]  python scripts/setup.py[/cyan]")
        console.print()
        console.print("[dim]The setup script will guide you through configuring[/dim]")
        console.print("[dim]API keys, mounts, and other instance settings.[/dim]")
        sys.exit(1)

    registry = get_instance_registry()
    config_dir = get_config_dir()
    is_new = False

    # Check if instance exists in registry (has port allocations)
    instance = registry.get_instance(name)

    if instance is None:
        # Instance has config but no registry entry - register it
        console.print(f"[bold blue]Registering instance '{name}'...[/bold blue]\n")
        try:
            instance = registry.register(name)
            is_new = True
        except ValueError as e:
            console.print(f"[bold red]✗ {e}[/bold red]")
            sys.exit(1)

        # Create backup directory
        backup_dir = config_dir / 'backups' / name
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Display port allocation
        ports = instance['ports']
        console.print("[dim]Port allocation:[/dim]")
        console.print(f"  PostgreSQL: {ports['postgres']}")
        console.print(f"  Neo4j Bolt: {ports['neo4j_bolt']}")
        console.print(f"  Neo4j HTTP: {ports['neo4j_http']}")
        console.print(f"  MCP Server: {ports['mcp']}")
        console.print()
    else:
        console.print(f"[bold blue]Starting instance '{name}'...[/bold blue]\n")

    # Build environment
    env = get_instance_env(instance, config_dir)

    # Start containers
    console.print("[dim]Starting containers...[/dim]")
    code, stdout, stderr = run_compose_command(
        compose_file, name, ["up", "-d"], env
    )

    if code != 0:
        console.print("[bold red]✗ Failed to start containers[/bold red]")
        console.print(f"[red]{stderr}[/red]")
        # Rollback registration if new instance
        if is_new:
            registry.unregister(name)
        sys.exit(1)

    console.print("[green]✓ Containers started[/green]")

    if not wait:
        console.print("\n[dim]Run 'rag instance status {name}' to check when services are ready[/dim]")
        return

    # Wait for databases to be healthy
    console.print("\n[dim]Waiting for databases to become healthy...[/dim]")

    ports = instance['ports']

    def progress_callback(status):
        elapsed = status['elapsed']
        pg = "✓" if status['postgres']['connectable'] else "..."
        neo4j = "✓" if status['neo4j']['connectable'] else "..."
        console.print(f"[dim]  [{elapsed}s] PostgreSQL: {pg}  Neo4j: {neo4j}[/dim]", end="\r")

    ready = wait_for_databases(
        instance_name=name,
        ports=ports,
        timeout_seconds=timeout,
        check_interval=5,
        callback=progress_callback
    )

    console.print()  # Clear the progress line

    if not ready:
        console.print("[bold red]✗ Timeout waiting for databases[/bold red]")
        console.print("[yellow]Containers are running but databases may not be ready.[/yellow]")
        console.print("[yellow]Check logs with: rag instance logs {name}[/yellow]")
        sys.exit(1)

    console.print("[green]✓ Databases healthy[/green]")

    # Initialize Neo4j indices if new instance
    if is_new or not registry.is_initialized(name):
        console.print("\n[dim]Initializing Neo4j indices...[/dim]")

        # Get OpenAI API key from environment or config
        openai_key = os.environ.get('OPENAI_API_KEY')
        if not openai_key:
            # Try to load from config
            config_file = config_dir / 'config.yaml'
            if config_file.exists():
                import yaml
                with open(config_file) as f:
                    config = yaml.safe_load(f)
                    openai_key = config.get('openai', {}).get('api_key')

        if not openai_key:
            console.print("[bold yellow]⚠ OPENAI_API_KEY not found[/bold yellow]")
            console.print("[yellow]Neo4j indices not initialized. Set OPENAI_API_KEY and run:[/yellow]")
            console.print(f"[yellow]  rag instance init {name}[/yellow]")
        else:
            success, message = run_initialization(
                instance_name=name,
                ports=ports,
                openai_api_key=openai_key,
                wait_timeout=60,  # Shorter timeout since DBs already healthy
                progress_callback=lambda msg: console.print(f"[dim]  {msg}[/dim]")
            )

            if success:
                registry.mark_initialized(name)
                console.print("[green]✓ Neo4j indices initialized[/green]")
            else:
                console.print(f"[bold yellow]⚠ {message}[/bold yellow]")
                console.print("[yellow]Instance started but indices may need manual initialization.[/yellow]")

    # Print success message with connection info
    console.print()
    console.print(Panel(
        f"[bold green]Instance '{name}' is running[/bold green]\n\n"
        f"[cyan]PostgreSQL:[/cyan] localhost:{ports['postgres']}\n"
        f"[cyan]Neo4j Bolt:[/cyan] localhost:{ports['neo4j_bolt']}\n"
        f"[cyan]Neo4j Browser:[/cyan] http://localhost:{ports['neo4j_http']}\n"
        f"[cyan]MCP Server:[/cyan] http://localhost:{ports['mcp']}",
        title="RAG Memory Instance",
        border_style="green"
    ))


@instance_group.command(name='stop')
@click.argument('name', required=False)
@click.option('--all', 'stop_all', is_flag=True, help='Stop all instances')
def stop_command(name: str, stop_all: bool):
    """Stop a RAG Memory instance (preserves data).

    NAME is the instance to stop.
    Use --all to stop all running instances.
    """
    if not name and not stop_all:
        console.print("[bold red]✗ Either provide an instance NAME or use --all[/bold red]")
        sys.exit(1)

    if name and stop_all:
        console.print("[bold red]✗ Cannot use both NAME and --all[/bold red]")
        sys.exit(1)

    if stop_all:
        registry = get_instance_registry()
        instances = registry.list_instances()
        if not instances:
            console.print("[bold yellow]No instances registered[/bold yellow]")
            sys.exit(0)

        console.print(f"[bold blue]Stopping {len(instances)} instance(s)...[/bold blue]\n")
        failed = []
        for instance in instances:
            instance_name = instance['name']
            console.print(f"[dim]{'='*60}[/dim]")
            console.print(f"[bold]Instance: {instance_name}[/bold]\n")
            try:
                _stop_instance(instance_name)
            except SystemExit:
                failed.append(instance_name)
                continue

        console.print(f"\n[dim]{'='*60}[/dim]")
        if failed:
            console.print(f"\n[bold red]✗ Failed to stop {len(failed)} instance(s): {', '.join(failed)}[/bold red]")
            sys.exit(1)
        else:
            console.print(f"\n[bold green]✓ All {len(instances)} instance(s) stopped successfully[/bold green]")
        return

    _stop_instance(name)


def _stop_instance(name: str):
    """Internal function to stop a single instance."""
    registry = get_instance_registry()
    instance = registry.get_instance(name)

    if instance is None:
        console.print(f"[bold red]✗ Instance '{name}' not found[/bold red]")
        console.print("[dim]Run 'rag instance list' to see available instances[/dim]")
        sys.exit(1)

    # Check if instance is already stopped
    mcp_container = f"rag-memory-mcp-{name}"
    postgres_container = f"rag-memory-postgres-{name}"
    neo4j_container = f"rag-memory-neo4j-{name}"

    mcp_status = get_container_status(mcp_container)
    postgres_status = get_container_status(postgres_container)
    neo4j_status = get_container_status(neo4j_container)

    # Check if all containers are already stopped
    if mcp_status == "Not running" and \
       postgres_status == "Not running" and \
       neo4j_status == "Not running":
        console.print(f"[bold yellow]Instance '{name}' is already stopped[/bold yellow]")
        return

    # Check Docker
    available, error = check_docker_available()
    if not available:
        console.print(f"[bold red]✗ {error}[/bold red]")
        sys.exit(1)

    # Get compose file
    try:
        compose_file = get_compose_file()
    except FileNotFoundError as e:
        console.print(f"[bold red]✗ {e}[/bold red]")
        sys.exit(1)

    console.print(f"[bold blue]Stopping instance '{name}'...[/bold blue]\n")

    # Build environment
    env = get_instance_env(instance, get_config_dir())

    # Stop containers (down without -v to preserve volumes)
    code, stdout, stderr = run_compose_command(
        compose_file, name, ["down"], env
    )

    if code != 0:
        console.print("[bold red]✗ Failed to stop instance[/bold red]")
        console.print(f"[red]{stderr}[/red]")
        sys.exit(1)

    console.print(f"[bold green]✓ Instance '{name}' stopped[/bold green]")
    console.print("[dim]Data volumes preserved. Run 'rag instance start {name}' to restart.[/dim]")


@instance_group.command(name='restart')
@click.argument('name', required=False)
@click.option('--all', 'restart_all', is_flag=True, help='Restart all instances')
@click.option('--wait/--no-wait', default=True, help='Wait for services to be healthy')
@click.option('--timeout', default=300, help='Timeout in seconds when waiting')
def restart_command(name: str, restart_all: bool, wait: bool, timeout: int):
    """Restart a RAG Memory instance.

    Stops and then starts the instance, preserving all data.

    NAME is the instance to restart.
    Use --all to restart all instances.
    """
    if not name and not restart_all:
        console.print("[bold red]✗ Either provide an instance NAME or use --all[/bold red]")
        sys.exit(1)

    if name and restart_all:
        console.print("[bold red]✗ Cannot use both NAME and --all[/bold red]")
        sys.exit(1)

    if restart_all:
        registry = get_instance_registry()
        instances = registry.list_instances()
        if not instances:
            console.print("[bold yellow]No instances registered[/bold yellow]")
            sys.exit(0)

        console.print(f"[bold blue]Restarting {len(instances)} instance(s)...[/bold blue]\n")
        failed = []
        for instance in instances:
            instance_name = instance['name']
            console.print(f"[dim]{'='*60}[/dim]")
            console.print(f"[bold]Instance: {instance_name}[/bold]\n")
            try:
                _restart_instance(instance_name, wait, timeout)
            except SystemExit:
                failed.append(instance_name)
                continue

        console.print(f"\n[dim]{'='*60}[/dim]")
        if failed:
            console.print(f"\n[bold red]✗ Failed to restart {len(failed)} instance(s): {', '.join(failed)}[/bold red]")
            sys.exit(1)
        else:
            console.print(f"\n[bold green]✓ All {len(instances)} instance(s) restarted successfully[/bold green]")
        return

    _restart_instance(name, wait, timeout)


def _restart_instance(name: str, wait: bool, timeout: int):
    """Internal function to restart a single instance."""
    # Stop the instance first
    try:
        _stop_instance(name)
    except SystemExit as e:
        # If stop failed, re-raise
        raise

    console.print()  # Blank line between stop and start

    # Start the instance
    try:
        _start_instance(name, wait, timeout)
    except SystemExit as e:
        # If start failed, re-raise
        raise


@instance_group.command(name='delete')
@click.argument('name')
@click.option('--force', '-f', is_flag=True, help='Skip confirmation prompt')
def delete_command(name: str, force: bool):
    """Delete a RAG Memory instance and all its data.

    This permanently removes:
    - All containers
    - All data volumes (PostgreSQL, Neo4j)
    - Backup files
    - Instance registration

    NAME is the instance to delete.
    """
    registry = get_instance_registry()
    instance = registry.get_instance(name)

    if instance is None:
        console.print(f"[bold red]✗ Instance '{name}' not found[/bold red]")
        console.print("[dim]Run 'rag instance list' to see available instances[/dim]")
        sys.exit(1)

    # Confirmation
    if not force:
        console.print(f"[bold yellow]⚠ This will permanently delete instance '{name}'[/bold yellow]")
        console.print("[yellow]Including all databases, knowledge, and backups.[/yellow]")
        console.print()

        if not click.confirm("Are you sure you want to continue?"):
            console.print("[dim]Cancelled[/dim]")
            return

    # Check Docker
    available, error = check_docker_available()
    if not available:
        console.print(f"[bold red]✗ {error}[/bold red]")
        sys.exit(1)

    # Get compose file
    try:
        compose_file = get_compose_file()
    except FileNotFoundError as e:
        console.print(f"[bold red]✗ {e}[/bold red]")
        sys.exit(1)

    config_dir = get_config_dir()
    env = get_instance_env(instance, config_dir)

    console.print(f"[bold blue]Deleting instance '{name}'...[/bold blue]\n")

    # Stop and remove containers AND volumes
    console.print("[dim]Removing containers and volumes...[/dim]")
    code, stdout, stderr = run_compose_command(
        compose_file, name, ["down", "-v", "--remove-orphans"], env
    )

    if code != 0:
        console.print("[bold yellow]⚠ Some resources may not have been removed[/bold yellow]")
        console.print(f"[dim]{stderr}[/dim]")

    # Remove backup directory
    backup_dir = config_dir / 'backups' / name
    if backup_dir.exists():
        console.print("[dim]Removing backups...[/dim]")
        import shutil
        try:
            shutil.rmtree(backup_dir)
        except Exception as e:
            console.print(f"[yellow]⚠ Failed to remove backups: {e}[/yellow]")

    # Remove from registry
    console.print("[dim]Unregistering instance...[/dim]")
    registry.unregister(name)

    # Remove from config.yaml
    console.print("[dim]Removing instance configuration...[/dim]")
    from src.core.config_loader import remove_instance_config
    try:
        remove_instance_config(name)
    except Exception as e:
        console.print(f"[yellow]⚠ Failed to remove from config.yaml: {e}[/yellow]")

    console.print(f"[bold green]✓ Instance '{name}' deleted[/bold green]")


@instance_group.command(name='list')
def list_command():
    """List all RAG Memory instances."""
    registry = get_instance_registry()
    instances = registry.list_instances()

    if not instances:
        console.print("[dim]No instances found.[/dim]")
        console.print("[dim]Create one with: rag instance start <name>[/dim]")
        return

    console.print("[bold blue]RAG Memory Instances[/bold blue]\n")

    table = Table()
    table.add_column("Name", style="cyan")
    table.add_column("PostgreSQL", style="white")
    table.add_column("Neo4j Bolt", style="white")
    table.add_column("MCP", style="white")
    table.add_column("Status", style="bold")
    table.add_column("Initialized", style="white")

    for instance in instances:
        name = instance['name']
        ports = instance['ports']

        # Check container status (just check MCP as indicator)
        mcp_container = f"rag-memory-mcp-{name}"
        status = get_container_status(mcp_container)
        status_display = format_status_display(status)

        initialized = "✓" if instance.get('initialized', False) else "✗"
        init_style = "green" if instance.get('initialized', False) else "red"

        table.add_row(
            name,
            str(ports['postgres']),
            str(ports['neo4j_bolt']),
            str(ports['mcp']),
            status_display,
            f"[{init_style}]{initialized}[/{init_style}]"
        )

    console.print(table)


@instance_group.command(name='status')
@click.argument('name', required=False)
@click.option('--all', 'status_all', is_flag=True, help='Show status of all instances')
def status_command(name: str, status_all: bool):
    """Show detailed status of a RAG Memory instance.

    NAME is the instance to check.
    Use --all to show status of all instances.
    """
    if not name and not status_all:
        console.print("[bold red]✗ Either provide an instance NAME or use --all[/bold red]")
        sys.exit(1)

    if name and status_all:
        console.print("[bold red]✗ Cannot use both NAME and --all[/bold red]")
        sys.exit(1)

    # Check Docker
    available, error = check_docker_available()
    if not available:
        console.print(f"[bold red]✗ {error}[/bold red]")
        sys.exit(1)

    if status_all:
        registry = get_instance_registry()
        instances = registry.list_instances()
        if not instances:
            console.print("[bold yellow]No instances registered[/bold yellow]")
            sys.exit(0)

        console.print(f"[bold blue]Status of {len(instances)} instance(s)[/bold blue]\n")
        for i, instance in enumerate(instances):
            if i > 0:
                console.print(f"\n[dim]{'='*60}[/dim]\n")
            _show_instance_status(instance)
        return

    registry = get_instance_registry()
    instance = registry.get_instance(name)

    if instance is None:
        console.print(f"[bold red]✗ Instance '{name}' not found[/bold red]")
        console.print("[dim]Run 'rag instance list' to see available instances[/dim]")
        sys.exit(1)

    _show_instance_status(instance)


def _show_instance_status(instance: dict):
    """Internal function to show status of a single instance."""
    name = instance['name']
    console.print(f"[bold blue]Instance '{name}' Status[/bold blue]\n")

    ports = instance['ports']

    # Define services to check
    services = [
        ("PostgreSQL", f"rag-memory-postgres-{name}", ports['postgres']),
        ("Neo4j", f"rag-memory-neo4j-{name}", ports['neo4j_bolt']),
        ("MCP Server", f"rag-memory-mcp-{name}", ports['mcp']),
        ("Backup", f"rag-memory-backup-{name}", None),
    ]

    # Create status table
    table = Table(title="Service Status")
    table.add_column("Service", style="cyan")
    table.add_column("Container", style="white")
    table.add_column("Port", style="white")
    table.add_column("Status", style="bold")

    all_healthy = True

    for service_name, container_name, port in services:
        status = get_container_status(container_name)
        status_display = format_status_display(status)

        if "healthy" not in status.lower() and "Up" not in status:
            all_healthy = False

        port_str = str(port) if port else "-"
        table.add_row(service_name, container_name, port_str, status_display)

    console.print(table)
    console.print()

    # Instance info
    console.print("[bold]Instance Info:[/bold]")
    console.print(f"  Created: {instance.get('created_at', 'Unknown')}")
    console.print(f"  Initialized: {'Yes' if instance.get('initialized') else 'No'}")
    console.print()

    # Connection info
    console.print("[bold]Connection URLs:[/bold]")
    console.print(f"  PostgreSQL: postgresql://raguser:ragpassword@localhost:{ports['postgres']}/rag_memory")
    console.print(f"  Neo4j Bolt: bolt://localhost:{ports['neo4j_bolt']}")
    console.print(f"  Neo4j Browser: http://localhost:{ports['neo4j_http']}")
    console.print(f"  MCP Server: http://localhost:{ports['mcp']}")
    console.print()

    if all_healthy:
        console.print("[bold green]✓ All services are healthy[/bold green]")
    else:
        console.print("[bold yellow]⚠ Some services are not healthy[/bold yellow]")
        console.print(f"[dim]Check logs with: rag instance logs {name}[/dim]")


@instance_group.command(name='logs')
@click.argument('name')
@click.option('--service', '-s', type=click.Choice(['postgres', 'neo4j', 'mcp', 'backup']),
              help='Show logs for specific service only')
@click.option('--follow', '-f', is_flag=True, help='Follow log output')
@click.option('--tail', '-n', default=100, help='Number of lines to show')
def logs_command(name: str, service: str, follow: bool, tail: int):
    """View logs for a RAG Memory instance.

    NAME is the instance to view logs for.
    """
    registry = get_instance_registry()
    instance = registry.get_instance(name)

    if instance is None:
        console.print(f"[bold red]✗ Instance '{name}' not found[/bold red]")
        console.print("[dim]Run 'rag instance list' to see available instances[/dim]")
        sys.exit(1)

    # Check Docker
    available, error = check_docker_available()
    if not available:
        console.print(f"[bold red]✗ {error}[/bold red]")
        sys.exit(1)

    # Get compose file
    try:
        compose_file = get_compose_file()
    except FileNotFoundError as e:
        console.print(f"[bold red]✗ {e}[/bold red]")
        sys.exit(1)

    config_dir = get_config_dir()
    env = get_instance_env(instance, config_dir)

    # Build logs command
    docker_compose = get_docker_compose_command()
    cmd = docker_compose + [
        "-p", f"rag-memory-{name}",
        "-f", str(compose_file),
        "logs",
        f"--tail={tail}"
    ]

    if follow:
        cmd.append("-f")

    if service:
        cmd.append(service)

    # Run interactively (not capturing output)
    try:
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        pass  # User cancelled with Ctrl+C


@instance_group.command(name='init')
@click.argument('name')
def init_command(name: str):
    """Initialize Neo4j indices for an instance.

    This is normally done automatically during 'rag instance start',
    but can be run manually if initialization failed or was skipped.

    NAME is the instance to initialize.
    """
    registry = get_instance_registry()
    instance = registry.get_instance(name)

    if instance is None:
        console.print(f"[bold red]✗ Instance '{name}' not found[/bold red]")
        sys.exit(1)

    if registry.is_initialized(name):
        console.print(f"[yellow]Instance '{name}' is already initialized[/yellow]")
        if not click.confirm("Re-initialize anyway?"):
            return

    # Get OpenAI API key
    openai_key = os.environ.get('OPENAI_API_KEY')
    if not openai_key:
        config_dir = get_config_dir()
        config_file = config_dir / 'config.yaml'
        if config_file.exists():
            import yaml
            with open(config_file) as f:
                config = yaml.safe_load(f)
                openai_key = config.get('openai', {}).get('api_key')

    if not openai_key:
        console.print("[bold red]✗ OPENAI_API_KEY not found[/bold red]")
        console.print("[dim]Set OPENAI_API_KEY environment variable and try again[/dim]")
        sys.exit(1)

    ports = instance['ports']

    console.print(f"[bold blue]Initializing Neo4j indices for '{name}'...[/bold blue]\n")

    success, message = run_initialization(
        instance_name=name,
        ports=ports,
        openai_api_key=openai_key,
        wait_timeout=120,
        progress_callback=lambda msg: console.print(f"[dim]  {msg}[/dim]")
    )

    if success:
        registry.mark_initialized(name)
        console.print(f"\n[bold green]✓ Instance '{name}' initialized successfully[/bold green]")
    else:
        console.print(f"\n[bold red]✗ Initialization failed: {message}[/bold red]")
        sys.exit(1)
