# RAG Memory Multi-Instance Support Implementation Plan

**Version:** 1.0
**Date:** December 14, 2025
**Branch:** `feature/multi-instance-support`

---

## Executive Summary

This document provides a complete implementation plan for adding multi-instance support to RAG Memory. The goal is to allow users to run **N** completely independent RAG Memory stacks (PostgreSQL + Neo4j + MCP Server + Backup) on the same host, each with:
- Unique, meaningful names (e.g., "primary", "research", "production")
- Automatically assigned, collision-free ports
- Isolated data volumes
- Instance-specific backup directories
- Full lifecycle management (start, stop, delete, status)

The solution uses a **single parameterized docker-compose.yml** template combined with an **instance registry** (`instances.json`) to track port assignments. This approach scales to unlimited instances without creating multiple compose files.

**Critical Requirement:** After setup, users must be able to delete the source repository and still manage their instances from the system config directory (`~/.config/rag-memory/` or platform equivalent).

---

## Table of Contents

1. [Goals & Requirements](#1-goals--requirements)
2. [Architecture Overview](#2-architecture-overview)
3. [File Changes Summary](#3-file-changes-summary)
4. [Implementation Details](#4-implementation-details)
   - 4.1 [New Instance Registry Module](#41-new-instance-registry-module)
   - 4.2 [New Instance CLI Commands](#42-new-instance-cli-commands)
   - 4.3 [Parameterized Docker Compose Template](#43-parameterized-docker-compose-template)
   - 4.4 [Setup Script Modifications](#44-setup-script-modifications)
   - 4.5 [Service.py Deprecation/Migration](#45-servicepy-deprecationmigration)
   - 4.6 [Update Scripts Migration](#46-update-scripts-migration)
   - 4.7 [CLI Registration](#47-cli-registration)
5. [Migration Strategy](#5-migration-strategy)
6. [Testing Plan](#6-testing-plan)
7. [Documentation Updates](#7-documentation-updates)
8. [Implementation Checklist](#8-implementation-checklist)

---

## 1. Goals & Requirements

### Primary Goals

1. **Unlimited Instances:** Support N independent RAG Memory stacks without code changes
2. **Name-Based Management:** Users identify instances by meaningful names, not port numbers
3. **Port Persistence:** Once assigned, ports remain consistent for an instance across restarts
4. **Isolated Backups:** Each instance backs up to its own directory
5. **Repo-Independent:** System works after source repository is deleted
6. **Backwards Compatible:** Existing single-instance users can migrate seamlessly

### Non-Goals

- Cloud deployment (handled separately by `deploy_to_cloud.py`)
- Automatic load balancing between instances
- Instance-to-instance communication

### Constraints

- Must work on macOS, Linux, and Windows
- Must use existing Docker Compose (no Kubernetes)
- Must maintain existing CLI command patterns where possible

---

## 2. Architecture Overview

### Current Architecture (Single Instance)

```
~/.config/rag-memory/
├── config.yaml              # API keys, DB URLs
├── docker-compose.yml       # Static compose file
├── .env                     # Port assignments
├── init.sql                 # PostgreSQL init
└── backups/                 # All backups in one dir

Containers:
├── rag-memory-postgres-local
├── rag-memory-neo4j-local
├── rag-memory-mcp-local
└── rag-memory-backup-local
```

### New Architecture (Multi-Instance)

```
~/.config/rag-memory/
├── config.yaml                    # Shared API keys (OpenAI)
├── docker-compose.instance.yml    # Parameterized template
├── instances.json                 # Instance registry with port assignments
├── init.sql                       # PostgreSQL init
└── backups/
    ├── primary/                   # Instance-specific backups
    ├── research/
    └── production/

Containers (per instance "primary"):
├── rag-memory-postgres-primary
├── rag-memory-neo4j-primary
├── rag-memory-mcp-primary
└── rag-memory-backup-primary

Docker Volumes (per instance "primary"):
├── rag-memory-primary_postgres-data
├── rag-memory-primary_neo4j-data
└── rag-memory-primary_neo4j-logs

Docker Networks (per instance "primary"):
└── rag-memory-primary_default
```

### Instance Registry Format (`instances.json`)

```json
{
  "version": 1,
  "instances": [
    {
      "name": "primary",
      "created_at": "2025-12-14T10:30:00Z",
      "ports": {
        "postgres": 54320,
        "neo4j_bolt": 7687,
        "neo4j_http": 7474,
        "mcp": 8000
      },
      "config_overrides": {}
    },
    {
      "name": "research",
      "created_at": "2025-12-14T11:00:00Z",
      "ports": {
        "postgres": 54330,
        "neo4j_bolt": 7688,
        "neo4j_http": 7475,
        "mcp": 8001
      },
      "config_overrides": {}
    }
  ]
}
```

---

## 3. File Changes Summary

### New Files to Create

| File | Purpose |
|------|---------|
| `src/core/instance_registry.py` | Instance registry management (CRUD, port allocation) |
| `src/cli_commands/instance.py` | CLI commands for instance management |
| `deploy/docker/compose/docker-compose.instance.yml` | Parameterized compose template |

### Files to Modify

| File | Changes |
|------|---------|
| `src/cli.py` | Register new `instance` command group |
| `src/cli_commands/service.py` | Deprecate with redirect to `instance` commands |
| `scripts/setup.py` | Support multi-instance initialization |
| `scripts/update_mcp.py` | Add `--instance` parameter |
| `scripts/update_databases.py` | Add `--instance` parameter |
| `pyproject.toml` | Add `tabulate` dependency |

### Files to Deprecate (Keep but Mark Deprecated)

| File | Replacement |
|------|-------------|
| `deploy/docker/compose/docker-compose.yml` | `docker-compose.instance.yml` |
| `deploy/docker/compose/docker-compose.template.yml` | `docker-compose.instance.yml` |

### Documentation to Update

| File | Updates |
|------|---------|
| `README.md` | Add multi-instance section |
| `.reference/CLI_GUIDE.md` | Document `rag instance` commands |
| `.reference/INSTALLATION.md` | Update installation instructions |
| `CLAUDE.md` | Update architecture section |

---

## 4. Implementation Details

### 4.1 New Instance Registry Module

**File:** `src/core/instance_registry.py`

```python
"""Instance registry for managing multiple RAG Memory stacks.

This module provides persistent storage and management for multiple
RAG Memory instances, including automatic port allocation and
collision prevention.

The registry is stored at ~/.config/rag-memory/instances.json
(or platform equivalent via platformdirs).
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import platformdirs


class InstanceRegistry:
    """Manage RAG Memory instance configurations and port assignments.

    The registry persists instance metadata to instances.json in the
    system config directory. Port assignments are permanent once
    allocated - they survive instance stop/start cycles.

    Port Allocation Strategy:
    - Base ports: PostgreSQL=54320, Neo4j Bolt=7687, Neo4j HTTP=7474, MCP=8000
    - Each new instance gets offset +10 for PostgreSQL, +1 for others
    - Example: Instance 1 = (54320, 7687, 7474, 8000)
    - Example: Instance 2 = (54330, 7688, 7475, 8001)
    - Example: Instance 3 = (54340, 7689, 7476, 8002)

    Attributes:
        config_dir: Path to system config directory
        registry_file: Path to instances.json
    """

    # Base port assignments
    POSTGRES_BASE = 54320
    NEO4J_BOLT_BASE = 7687
    NEO4J_HTTP_BASE = 7474
    MCP_BASE = 8000

    # Port offset between instances
    POSTGRES_OFFSET = 10  # PostgreSQL: 54320, 54330, 54340, ...
    OTHER_OFFSET = 1      # Others: 7687, 7688, 7689, ...

    def __init__(self, config_dir: Path = None):
        """Initialize registry.

        Args:
            config_dir: Override config directory (for testing).
                       Defaults to platformdirs location.
        """
        if config_dir is None:
            self.config_dir = Path(platformdirs.user_config_dir('rag-memory', appauthor=False))
        else:
            self.config_dir = Path(config_dir)

        self.registry_file = self.config_dir / 'instances.json'
        self._ensure_registry_exists()

    def _ensure_registry_exists(self) -> None:
        """Create registry file if it doesn't exist."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

        if not self.registry_file.exists():
            self._save({'version': 1, 'instances': []})

    def _load(self) -> dict:
        """Load registry from disk."""
        try:
            return json.loads(self.registry_file.read_text())
        except (json.JSONDecodeError, FileNotFoundError):
            return {'version': 1, 'instances': []}

    def _save(self, data: dict) -> None:
        """Save registry to disk."""
        self.registry_file.write_text(json.dumps(data, indent=2, default=str))

    def get_instance(self, name: str) -> Optional[dict]:
        """Get instance by name.

        Args:
            name: Instance name (e.g., "primary", "research")

        Returns:
            Instance dict with name, created_at, ports, config_overrides
            or None if not found.
        """
        data = self._load()
        for instance in data.get('instances', []):
            if instance['name'] == name:
                return instance
        return None

    def instance_exists(self, name: str) -> bool:
        """Check if instance exists in registry."""
        return self.get_instance(name) is not None

    def list_instances(self) -> list:
        """List all registered instances.

        Returns:
            List of instance dicts sorted by creation time.
        """
        data = self._load()
        return data.get('instances', [])

    def get_next_port_offset(self) -> int:
        """Calculate next available port offset.

        Returns:
            Integer offset for port calculation (0, 1, 2, ...).
            Returns max(existing offsets) + 1, or 0 if no instances.
        """
        instances = self.list_instances()

        if not instances:
            return 0

        # Find highest offset currently in use
        max_offset = 0
        for inst in instances:
            ports = inst.get('ports', {})
            # Calculate offset from PostgreSQL port
            pg_port = ports.get('postgres', self.POSTGRES_BASE)
            offset = (pg_port - self.POSTGRES_BASE) // self.POSTGRES_OFFSET
            max_offset = max(max_offset, offset)

        return max_offset + 1

    def calculate_ports(self, offset: int) -> dict:
        """Calculate port assignments for given offset.

        Args:
            offset: Instance offset (0, 1, 2, ...)

        Returns:
            Dict with postgres, neo4j_bolt, neo4j_http, mcp port numbers.
        """
        return {
            'postgres': self.POSTGRES_BASE + (offset * self.POSTGRES_OFFSET),
            'neo4j_bolt': self.NEO4J_BOLT_BASE + (offset * self.OTHER_OFFSET),
            'neo4j_http': self.NEO4J_HTTP_BASE + (offset * self.OTHER_OFFSET),
            'mcp': self.MCP_BASE + (offset * self.OTHER_OFFSET),
        }

    def register(self, name: str, config_overrides: dict = None) -> dict:
        """Register a new instance with auto-assigned ports.

        Args:
            name: Unique instance name (alphanumeric, hyphens, underscores)
            config_overrides: Optional config values specific to this instance

        Returns:
            Created instance dict with assigned ports.

        Raises:
            ValueError: If instance name already exists or is invalid.
        """
        # Validate name
        if not name:
            raise ValueError("Instance name cannot be empty")

        if not all(c.isalnum() or c in '-_' for c in name):
            raise ValueError("Instance name must contain only alphanumeric characters, hyphens, and underscores")

        if self.instance_exists(name):
            raise ValueError(f"Instance '{name}' already exists")

        # Allocate ports
        offset = self.get_next_port_offset()
        ports = self.calculate_ports(offset)

        # Create instance record
        instance = {
            'name': name,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'ports': ports,
            'config_overrides': config_overrides or {},
        }

        # Save to registry
        data = self._load()
        data['instances'].append(instance)
        self._save(data)

        return instance

    def unregister(self, name: str) -> bool:
        """Remove instance from registry.

        Note: This does NOT stop containers or delete volumes.
        Use InstanceManager.delete() for full cleanup.

        Args:
            name: Instance name to remove.

        Returns:
            True if removed, False if not found.
        """
        data = self._load()
        original_count = len(data['instances'])
        data['instances'] = [i for i in data['instances'] if i['name'] != name]

        if len(data['instances']) < original_count:
            self._save(data)
            return True
        return False

    def get_compose_file(self) -> Path:
        """Get path to parameterized compose template.

        Returns:
            Path to docker-compose.instance.yml in config directory.

        Raises:
            FileNotFoundError: If compose file doesn't exist.
        """
        compose_file = self.config_dir / 'docker-compose.instance.yml'

        if not compose_file.exists():
            raise FileNotFoundError(
                f"Compose template not found: {compose_file}\n"
                "Please run setup.py first to initialize the system."
            )

        return compose_file

    def get_backup_dir(self, instance_name: str) -> Path:
        """Get backup directory for an instance.

        Args:
            instance_name: Name of the instance.

        Returns:
            Path to instance-specific backup directory.
        """
        return self.config_dir / 'backups' / instance_name


def get_instance_registry(config_dir: Path = None) -> InstanceRegistry:
    """Factory function to get instance registry.

    Args:
        config_dir: Override config directory (for testing).

    Returns:
        InstanceRegistry instance.
    """
    return InstanceRegistry(config_dir)
```

---

### 4.2 New Instance CLI Commands

**File:** `src/cli_commands/instance.py`

```python
"""Instance management commands for RAG Memory.

Provides CLI commands to manage multiple RAG Memory stack instances:
- start: Start a new or existing instance
- stop: Stop a running instance (preserves data)
- delete: Delete an instance and its data
- list: List all instances with status
- status: Show detailed status of an instance
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from src.core.instance_registry import get_instance_registry, InstanceRegistry

console = Console()


def get_container_status(container_name: str) -> str:
    """Check if a Docker container is running.

    Args:
        container_name: Full container name (e.g., rag-memory-postgres-primary)

    Returns:
        One of: "running", "stopped", "not_found", "unknown"
    """
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--filter", f"name=^{container_name}$",
             "--format", "{{.State}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        state = result.stdout.strip()

        if not state:
            return "not_found"
        elif state == "running":
            return "running"
        elif state in ("exited", "created", "paused"):
            return "stopped"
        else:
            return state
    except subprocess.TimeoutExpired:
        return "unknown"
    except Exception:
        return "unknown"


def get_instance_health(instance: dict) -> str:
    """Get overall health status of an instance.

    Args:
        instance: Instance dict from registry

    Returns:
        One of: "running", "partial", "stopped", "not_found"
    """
    name = instance['name']
    containers = [
        f"rag-memory-postgres-{name}",
        f"rag-memory-neo4j-{name}",
        f"rag-memory-mcp-{name}",
    ]

    statuses = [get_container_status(c) for c in containers]

    if all(s == "running" for s in statuses):
        return "running"
    elif all(s in ("stopped", "not_found") for s in statuses):
        if all(s == "not_found" for s in statuses):
            return "not_found"
        return "stopped"
    else:
        return "partial"


def build_compose_env(instance: dict, registry: InstanceRegistry) -> dict:
    """Build environment variables for docker compose.

    Args:
        instance: Instance dict from registry
        registry: InstanceRegistry for paths

    Returns:
        Dict of environment variables for subprocess.
    """
    ports = instance['ports']
    name = instance['name']
    backup_dir = registry.get_backup_dir(name)

    # Start with current environment
    env = os.environ.copy()

    # Add instance-specific variables
    env.update({
        'INSTANCE_NAME': name,
        'POSTGRES_PORT': str(ports['postgres']),
        'NEO4J_BOLT_PORT': str(ports['neo4j_bolt']),
        'NEO4J_HTTP_PORT': str(ports['neo4j_http']),
        'MCP_PORT': str(ports['mcp']),
        'BACKUP_ARCHIVE_PATH': str(backup_dir),
        'RAG_CONFIG_DIR': str(registry.config_dir),
        # Default credentials (can be overridden by config.yaml)
        'POSTGRES_USER': 'raguser',
        'POSTGRES_PASSWORD': 'ragpassword',
        'POSTGRES_DB': 'rag_memory',
        'NEO4J_USER': 'neo4j',
        'NEO4J_PASSWORD': 'graphiti-password',
    })

    return env


def run_compose_command(
    registry: InstanceRegistry,
    instance: dict,
    compose_args: list,
    capture_output: bool = True
) -> tuple:
    """Run docker compose command for an instance.

    Args:
        registry: InstanceRegistry for paths
        instance: Instance dict
        compose_args: Arguments after 'docker compose -p <project> -f <file>'
        capture_output: Whether to capture stdout/stderr

    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    compose_file = registry.get_compose_file()
    project_name = f"rag-memory-{instance['name']}"
    env = build_compose_env(instance, registry)

    cmd = [
        "docker", "compose",
        "-p", project_name,
        "-f", str(compose_file),
    ] + compose_args

    try:
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=capture_output,
            text=True,
            timeout=300  # 5 minute timeout for operations
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Operation timed out"
    except Exception as e:
        return 1, "", str(e)


@click.group(name='instance')
def instance_group():
    """Manage RAG Memory stack instances.

    Each instance is a complete, isolated RAG Memory stack with its own
    PostgreSQL, Neo4j, MCP server, and backup service.

    Examples:

        # Start a new instance
        rag instance start primary

        # Start another instance
        rag instance start research

        # List all instances
        rag instance list

        # Stop an instance (preserves data)
        rag instance stop research

        # Delete an instance (removes all data)
        rag instance delete research --confirm
    """
    pass


@instance_group.command(name='start')
@click.argument('name')
@click.option('--build', is_flag=True, help='Force rebuild of MCP container image')
def start_command(name: str, build: bool):
    """Start a new instance or restart an existing one.

    If the instance doesn't exist in the registry, it will be created
    with automatically assigned ports. If it exists, it will be restarted
    using the same ports.

    Args:
        name: Instance name (alphanumeric, hyphens, underscores allowed)
    """
    registry = get_instance_registry()

    # Check if instance exists, create if not
    instance = registry.get_instance(name)

    if instance is None:
        try:
            instance = registry.register(name)
            console.print(f"[green]Created new instance:[/green] {name}")
        except ValueError as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            sys.exit(1)
    else:
        console.print(f"[blue]Restarting existing instance:[/blue] {name}")

    # Ensure backup directory exists
    backup_dir = registry.get_backup_dir(name)
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Build arguments
    compose_args = ["up", "-d"]
    if build:
        compose_args.insert(0, "--build")

    console.print("[dim]Starting containers...[/dim]")

    code, stdout, stderr = run_compose_command(registry, instance, compose_args, capture_output=True)

    if code != 0:
        console.print(f"[bold red]Failed to start instance:[/bold red]")
        console.print(f"[red]{stderr}[/red]")
        sys.exit(1)

    # Print success with connection info
    ports = instance['ports']
    console.print()
    console.print(f"[bold green]Instance '{name}' started successfully[/bold green]")
    console.print()
    console.print("[bold]Connection Details:[/bold]")
    console.print(f"  PostgreSQL:    localhost:{ports['postgres']}")
    console.print(f"  Neo4j Browser: http://localhost:{ports['neo4j_http']}")
    console.print(f"  Neo4j Bolt:    bolt://localhost:{ports['neo4j_bolt']}")
    console.print(f"  MCP Server:    http://localhost:{ports['mcp']}/sse")
    console.print(f"  Backups:       {backup_dir}")
    console.print()
    console.print("[dim]Run 'rag instance status {name}' to check container health[/dim]")


@instance_group.command(name='stop')
@click.argument('name')
def stop_command(name: str):
    """Stop a running instance.

    Stops all containers but preserves the instance in the registry
    and all data volumes. Use 'rag instance start <name>' to restart.

    Args:
        name: Instance name to stop
    """
    registry = get_instance_registry()
    instance = registry.get_instance(name)

    if instance is None:
        console.print(f"[bold red]Instance '{name}' not found[/bold red]")
        console.print("[dim]Run 'rag instance list' to see available instances[/dim]")
        sys.exit(1)

    console.print(f"[blue]Stopping instance:[/blue] {name}")

    code, stdout, stderr = run_compose_command(registry, instance, ["down"])

    if code != 0:
        console.print(f"[bold red]Failed to stop instance:[/bold red]")
        console.print(f"[red]{stderr}[/red]")
        sys.exit(1)

    console.print(f"[bold green]Instance '{name}' stopped[/bold green]")
    console.print("[dim]Data volumes preserved. Run 'rag instance start {name}' to restart.[/dim]")


@instance_group.command(name='delete')
@click.argument('name')
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
@click.option('--keep-volumes', is_flag=True, help='Keep data volumes (only remove containers)')
def delete_command(name: str, confirm: bool, keep_volumes: bool):
    """Delete an instance and optionally its data.

    By default, removes all containers AND data volumes.
    Use --keep-volumes to preserve data for later recovery.

    Args:
        name: Instance name to delete
    """
    registry = get_instance_registry()
    instance = registry.get_instance(name)

    if instance is None:
        console.print(f"[bold red]Instance '{name}' not found[/bold red]")
        sys.exit(1)

    # Confirmation
    if not confirm:
        console.print(f"[bold yellow]WARNING:[/bold yellow] This will delete instance '{name}'")
        if not keep_volumes:
            console.print("[bold red]All data in PostgreSQL and Neo4j will be permanently deleted![/bold red]")
        else:
            console.print("[yellow]Containers will be removed but data volumes will be preserved.[/yellow]")

        if not click.confirm("Are you sure you want to continue?"):
            console.print("[dim]Cancelled[/dim]")
            return

    # Stop and remove containers
    compose_args = ["down"]
    if not keep_volumes:
        compose_args.append("-v")  # Also remove volumes

    console.print(f"[blue]Deleting instance:[/blue] {name}")

    code, stdout, stderr = run_compose_command(registry, instance, compose_args)

    if code != 0:
        console.print(f"[bold yellow]Warning: Failed to stop containers:[/bold yellow]")
        console.print(f"[yellow]{stderr}[/yellow]")
        # Continue with registry removal anyway

    # Remove from registry
    registry.unregister(name)

    console.print(f"[bold green]Instance '{name}' deleted[/bold green]")

    if not keep_volumes:
        console.print("[dim]All data has been permanently removed[/dim]")
    else:
        console.print("[dim]Data volumes preserved - can be recovered manually[/dim]")


@instance_group.command(name='list')
def list_command():
    """List all instances with their status and ports.

    Shows a table of all registered instances including:
    - Instance name
    - Current status (running/stopped/partial)
    - Port assignments
    """
    registry = get_instance_registry()
    instances = registry.list_instances()

    if not instances:
        console.print("[yellow]No instances registered[/yellow]")
        console.print("[dim]Run 'rag instance start <name>' to create one[/dim]")
        return

    # Build table
    table = Table(title="RAG Memory Instances")
    table.add_column("Name", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("PostgreSQL", style="white")
    table.add_column("Neo4j Bolt", style="white")
    table.add_column("Neo4j HTTP", style="white")
    table.add_column("MCP", style="white")

    for instance in instances:
        status = get_instance_health(instance)

        # Color status
        if status == "running":
            status_display = "[green]running[/green]"
        elif status == "stopped":
            status_display = "[red]stopped[/red]"
        elif status == "partial":
            status_display = "[yellow]partial[/yellow]"
        else:
            status_display = "[dim]not found[/dim]"

        ports = instance['ports']
        table.add_row(
            instance['name'],
            status_display,
            str(ports['postgres']),
            str(ports['neo4j_bolt']),
            str(ports['neo4j_http']),
            str(ports['mcp']),
        )

    console.print(table)


@instance_group.command(name='status')
@click.argument('name')
def status_command(name: str):
    """Show detailed status of an instance.

    Displays container-level status for all services in the instance.

    Args:
        name: Instance name to check
    """
    registry = get_instance_registry()
    instance = registry.get_instance(name)

    if instance is None:
        console.print(f"[bold red]Instance '{name}' not found[/bold red]")
        sys.exit(1)

    console.print(f"[bold]Instance: {name}[/bold]")
    console.print()

    # Container status table
    table = Table(title="Container Status")
    table.add_column("Service", style="cyan")
    table.add_column("Container", style="white")
    table.add_column("Status", style="bold")

    services = [
        ("PostgreSQL", f"rag-memory-postgres-{name}"),
        ("Neo4j", f"rag-memory-neo4j-{name}"),
        ("MCP Server", f"rag-memory-mcp-{name}"),
        ("Backup", f"rag-memory-backup-{name}"),
    ]

    all_running = True

    for service_name, container_name in services:
        status = get_container_status(container_name)

        if status == "running":
            status_display = "[green]running[/green]"
        elif status == "stopped":
            status_display = "[red]stopped[/red]"
            all_running = False
        elif status == "not_found":
            status_display = "[dim]not found[/dim]"
            all_running = False
        else:
            status_display = f"[yellow]{status}[/yellow]"
            all_running = False

        table.add_row(service_name, container_name, status_display)

    console.print(table)
    console.print()

    # Port information
    ports = instance['ports']
    console.print("[bold]Connection Details:[/bold]")
    console.print(f"  PostgreSQL:    localhost:{ports['postgres']}")
    console.print(f"  Neo4j Browser: http://localhost:{ports['neo4j_http']}")
    console.print(f"  Neo4j Bolt:    bolt://localhost:{ports['neo4j_bolt']}")
    console.print(f"  MCP Server:    http://localhost:{ports['mcp']}/sse")
    console.print()

    # Overall status
    if all_running:
        console.print("[bold green]All services running[/bold green]")
    else:
        console.print("[bold yellow]Some services not running[/bold yellow]")
        console.print(f"[dim]Run 'rag instance start {name}' to start all services[/dim]")


@instance_group.command(name='logs')
@click.argument('name')
@click.option('--service', '-s', type=click.Choice(['postgres', 'neo4j', 'mcp', 'backup']),
              help='Show logs for specific service only')
@click.option('--follow', '-f', is_flag=True, help='Follow log output')
@click.option('--tail', '-n', default=100, help='Number of lines to show')
def logs_command(name: str, service: Optional[str], follow: bool, tail: int):
    """Show logs for an instance.

    Args:
        name: Instance name
    """
    registry = get_instance_registry()
    instance = registry.get_instance(name)

    if instance is None:
        console.print(f"[bold red]Instance '{name}' not found[/bold red]")
        sys.exit(1)

    compose_args = ["logs", f"--tail={tail}"]

    if follow:
        compose_args.append("-f")

    if service:
        # Map service name to compose service
        service_map = {
            'postgres': 'postgres',
            'neo4j': 'neo4j',
            'mcp': 'mcp',
            'backup': 'backup',
        }
        compose_args.append(service_map[service])

    # Run with output directly to terminal (not captured)
    compose_file = registry.get_compose_file()
    project_name = f"rag-memory-{instance['name']}"
    env = build_compose_env(instance, registry)

    cmd = [
        "docker", "compose",
        "-p", project_name,
        "-f", str(compose_file),
    ] + compose_args

    try:
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        pass  # User cancelled with Ctrl+C


# Export for CLI registration
instance = instance_group
```

---

### 4.3 Parameterized Docker Compose Template

**File:** `deploy/docker/compose/docker-compose.instance.yml`

This file replaces the static compose files. All service names, container names, volume names, and network names use `${INSTANCE_NAME}` for parameterization.

```yaml
version: '3.9'

# ================================================================================
# RAG Memory Multi-Instance Docker Compose Template
# ================================================================================
# This is a PARAMETERIZED template that supports unlimited instances.
# Each instance is identified by INSTANCE_NAME and gets unique ports/volumes.
#
# Usage:
#   INSTANCE_NAME=primary docker compose -p rag-memory-primary up -d
#   INSTANCE_NAME=research docker compose -p rag-memory-research up -d
#
# Required Environment Variables:
#   INSTANCE_NAME      - Unique instance identifier (e.g., "primary", "research")
#   POSTGRES_PORT      - Host port for PostgreSQL (e.g., 54320)
#   NEO4J_BOLT_PORT    - Host port for Neo4j Bolt protocol (e.g., 7687)
#   NEO4J_HTTP_PORT    - Host port for Neo4j Browser (e.g., 7474)
#   MCP_PORT           - Host port for MCP SSE server (e.g., 8000)
#   BACKUP_ARCHIVE_PATH - Host path for backup archives
#   RAG_CONFIG_DIR     - Path to config directory with config.yaml
#
# Optional Environment Variables:
#   POSTGRES_USER      - PostgreSQL username (default: raguser)
#   POSTGRES_PASSWORD  - PostgreSQL password (default: ragpassword)
#   POSTGRES_DB        - PostgreSQL database name (default: rag_memory)
#   NEO4J_USER         - Neo4j username (default: neo4j)
#   NEO4J_PASSWORD     - Neo4j password (default: graphiti-password)
#   BACKUP_CRON_EXPRESSION - Backup schedule (default: 5 2 * * *)
#   BACKUP_RETENTION_DAYS  - Days to keep backups (default: 14)
# ================================================================================

services:
  postgres:
    image: pgvector/pgvector:pg16
    container_name: rag-memory-postgres-${INSTANCE_NAME}
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-raguser}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-ragpassword}
      POSTGRES_DB: ${POSTGRES_DB:-rag_memory}
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ${RAG_CONFIG_DIR}/init.sql:/docker-entrypoint-initdb.d/01-init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-raguser} -d ${POSTGRES_DB:-rag_memory} && psql -U ${POSTGRES_USER:-raguser} -d ${POSTGRES_DB:-rag_memory} -tc 'SELECT 1' > /dev/null"]
      interval: 10s
      timeout: 5s
      retries: 5
    ports:
      - "${POSTGRES_PORT}:5432"
    restart: unless-stopped

  neo4j:
    image: neo4j:5-community
    container_name: rag-memory-neo4j-${INSTANCE_NAME}
    environment:
      NEO4J_AUTH: ${NEO4J_USER:-neo4j}/${NEO4J_PASSWORD:-graphiti-password}
      NEO4J_PLUGINS: '["apoc"]'
      NEO4J_server_memory_heap_initial__size: 256m
      NEO4J_server_memory_heap_max__size: 512m
    volumes:
      - neo4j-data:/var/lib/neo4j/data
      - neo4j-logs:/var/lib/neo4j/logs
    healthcheck:
      test: ["CMD-SHELL", "cypher-shell -u ${NEO4J_USER:-neo4j} -p ${NEO4J_PASSWORD:-graphiti-password} 'RETURN 1' || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 5
    ports:
      - "${NEO4J_BOLT_PORT}:7687"
      - "${NEO4J_HTTP_PORT}:7474"
    restart: unless-stopped

  mcp:
    image: rag-memory-mcp:latest
    container_name: rag-memory-mcp-${INSTANCE_NAME}
    shm_size: '2gb'
    ipc: host
    cap_add:
      - SYS_ADMIN
    environment:
      # Use Docker service names for inter-container communication
      DATABASE_URL: postgresql://${POSTGRES_USER:-raguser}:${POSTGRES_PASSWORD:-ragpassword}@postgres:5432/${POSTGRES_DB:-rag_memory}
      NEO4J_URI: bolt://neo4j:7687
      NEO4J_USER: ${NEO4J_USER:-neo4j}
      NEO4J_PASSWORD: ${NEO4J_PASSWORD:-graphiti-password}
    volumes:
      - ${RAG_CONFIG_DIR}:/root/.config/rag-memory:ro
      # USER_MOUNTS_PLACEHOLDER - Setup script will insert user directory mounts here
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
      interval: 15s
      timeout: 10s
      retries: 3
      start_period: 45s
    ports:
      - "${MCP_PORT}:8000"
    depends_on:
      postgres:
        condition: service_healthy
      neo4j:
        condition: service_healthy
    restart: on-failure

  backup:
    image: offen/docker-volume-backup:latest
    container_name: rag-memory-backup-${INSTANCE_NAME}
    restart: always
    volumes:
      - postgres-data:/backup/postgres:ro
      - neo4j-data:/backup/neo4j:ro
      - neo4j-logs:/backup/neo4j_logs:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ${BACKUP_ARCHIVE_PATH}:/archive
    depends_on:
      postgres:
        condition: service_healthy
      neo4j:
        condition: service_healthy
    environment:
      BACKUP_SOURCES: /backup
      BACKUP_FILENAME_EXPAND: "true"
      BACKUP_CRON_EXPRESSION: "${BACKUP_CRON_EXPRESSION:-5 2 * * *}"
      BACKUP_ARCHIVE: "/archive"
      BACKUP_LATEST_SYMLINK: "backup-latest.tar.gz"
      BACKUP_RETENTION_DAYS: "${BACKUP_RETENTION_DAYS:-14}"
      BACKUP_PRUNING_PREFIX: "backup-"
    healthcheck:
      test: ["CMD-SHELL", "test -w /archive || exit 1"]
      interval: 300s
      timeout: 10s
      retries: 2
      start_period: 30s

# Volumes use project name prefix automatically (e.g., rag-memory-primary_postgres-data)
volumes:
  postgres-data:
    driver: local
  neo4j-data:
    driver: local
  neo4j-logs:
    driver: local

# Network is automatically created with project name prefix
```

---

### 4.4 Setup Script Modifications

**File:** `scripts/setup.py`

The setup script needs significant modifications. Here are the key changes:

#### 4.4.1 Add Instance Name Prompt

Add after step for backup retention (around line 520):

```python
def prompt_for_instance_name() -> str:
    """
    Prompt user for the name of their first instance.

    Returns:
        Instance name (e.g., "default", "primary", "main")
    """
    print_header("STEP 10: Instance Name")

    print_info("RAG Memory supports multiple independent instances.")
    print_info("Each instance has its own databases and MCP server.")
    print_info("Choose a meaningful name for your first instance.\n")

    while True:
        name = input(f"{Colors.CYAN}Instance name (default: 'default'): {Colors.RESET}").strip()

        if not name:
            name = "default"

        # Validate name
        if not all(c.isalnum() or c in '-_' for c in name):
            print_error("Name must contain only letters, numbers, hyphens, and underscores")
            continue

        if len(name) > 50:
            print_error("Name must be 50 characters or less")
            continue

        print_success(f"Instance name: {name}")
        return name
```

#### 4.4.2 Modify `create_config_yaml` Function

Update to:
1. Copy `docker-compose.instance.yml` instead of generating from template
2. Create `instances.json` with the first instance
3. Update port variable names

Replace the compose file generation section (around lines 730-803) with:

```python
        # 3. Copy parameterized docker-compose template to system location
        instance_compose_src = project_root / 'deploy' / 'docker' / 'compose' / 'docker-compose.instance.yml'
        instance_compose_dest = config_dir / 'docker-compose.instance.yml'

        with open(instance_compose_src, 'r') as f:
            compose_content = f.read()

        # Inject user mounts
        mount_lines = ""
        if mounts:
            for mount in mounts:
                mount_path = mount['path']
                docker_path = convert_path_for_docker(mount_path)
                mount_lines += f"      - {docker_path}:{docker_path}:ro\n"

        if mount_lines:
            compose_content = compose_content.replace(
                "      # USER_MOUNTS_PLACEHOLDER - Setup script will insert user directory mounts here",
                "      # User directory mounts (read-only)\n" + mount_lines.rstrip()
            )
        else:
            compose_content = compose_content.replace(
                "      # USER_MOUNTS_PLACEHOLDER - Setup script will insert user directory mounts here\n",
                ""
            )

        with open(instance_compose_dest, 'w') as f:
            f.write(compose_content)
        print_success(f"Multi-instance compose template created: {instance_compose_dest}")

        # 4. Create instances.json with first instance
        instances_json = {
            "version": 1,
            "instances": [
                {
                    "name": instance_name,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "ports": {
                        "postgres": ports['postgres'],
                        "neo4j_bolt": ports['neo4j_bolt'],
                        "neo4j_http": ports['neo4j_http'],
                        "mcp": ports['mcp']
                    },
                    "config_overrides": {}
                }
            ]
        }

        instances_file = config_dir / 'instances.json'
        with open(instances_file, 'w') as f:
            json.dump(instances_json, f, indent=2)
        print_success(f"Instance registry created: {instances_file}")
```

#### 4.4.3 Modify `build_and_start_containers` Function

Update to use the new compose file and project name:

```python
def build_and_start_containers(config_dir: Path, instance_name: str, ports: dict = None) -> bool:
    """Build and start Docker containers for an instance."""
    print_header("STEP 13: Building and Starting Containers")

    project_root = Path(__file__).parent.parent
    instance_compose = config_dir / 'docker-compose.instance.yml'
    project_name = f"rag-memory-{instance_name}"

    # Set up environment
    backup_dir = config_dir / 'backups' / instance_name
    backup_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env.update({
        'INSTANCE_NAME': instance_name,
        'POSTGRES_PORT': str(ports['postgres']),
        'NEO4J_BOLT_PORT': str(ports['neo4j_bolt']),
        'NEO4J_HTTP_PORT': str(ports['neo4j_http']),
        'MCP_PORT': str(ports['mcp']),
        'BACKUP_ARCHIVE_PATH': str(backup_dir),
        'RAG_CONFIG_DIR': str(config_dir),
    })

    try:
        docker_compose_cmd = get_docker_compose_command()

        # Build MCP image
        print_info("Building MCP server image...")
        code, _, stderr = run_command(
            docker_compose_cmd + [
                "-p", project_name,
                "-f", str(instance_compose),
                "build", "--no-cache", "mcp"
            ],
            timeout=600,
            env=env
        )

        if code != 0:
            print_error(f"Failed to build MCP image: {stderr}")
            return False

        print_success("MCP image built")

        # Start containers
        print_info("Starting containers...")
        code, stdout, stderr = run_command(
            docker_compose_cmd + [
                "-p", project_name,
                "-f", str(instance_compose),
                "up", "-d", "--force-recreate"
            ],
            timeout=None,
            env=env
        )

        if code != 0:
            print_error(f"Failed to start containers: {stderr}")
            return False

        print_success("Containers started")
        return True

    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False
```

#### 4.4.4 Update Container Name References

Update all hardcoded container names to use the instance name pattern.

In `wait_for_health_checks` and other functions, replace:
- `"rag-memory-postgres-local"` → `f"rag-memory-postgres-{instance_name}"`
- `"rag-memory-neo4j-local"` → `f"rag-memory-neo4j-{instance_name}"`
- `"rag-memory-mcp-local"` → `f"rag-memory-mcp-{instance_name}"`

#### 4.4.5 Update Main Function

Add instance name to the flow:

```python
def main():
    # ... existing steps 1-9 ...

    # Step 10: Get instance name
    instance_name = prompt_for_instance_name()

    # Update all subsequent function calls to pass instance_name
    success, config_dir = create_config_yaml(
        api_key, ports, mounts, backup_cron, backup_dir,
        backup_retention, max_reflexion_iterations, instance_name
    )

    if not build_and_start_containers(config_dir, instance_name, ports):
        sys.exit(1)

    if not wait_for_health_checks(ports, config_dir, instance_name):
        # ...

    # Update final summary to show instance name
    print_final_summary(ports, config_dir, instance_name)
```

---

### 4.5 Service.py Deprecation/Migration

**File:** `src/cli_commands/service.py`

Add deprecation warnings and redirect to instance commands:

```python
"""Service management commands for RAG Memory.

DEPRECATED: These commands are deprecated in favor of 'rag instance' commands.
They are maintained for backwards compatibility with single-instance setups.
"""

import subprocess
import sys
from pathlib import Path

import click
from rich.console import Console

from src.core.instance_registry import get_instance_registry

console = Console()


def _get_default_instance() -> str:
    """Get the default instance name for legacy commands.

    Returns 'default' if exists, otherwise first registered instance.
    """
    registry = get_instance_registry()
    instances = registry.list_instances()

    if not instances:
        return None

    # Prefer 'default' instance
    for inst in instances:
        if inst['name'] == 'default':
            return 'default'

    # Fall back to first instance
    return instances[0]['name']


def _show_deprecation_warning(old_cmd: str, new_cmd: str):
    """Show deprecation warning for legacy commands."""
    console.print(f"[yellow]DEPRECATION WARNING:[/yellow] 'rag {old_cmd}' is deprecated.")
    console.print(f"[yellow]Use 'rag instance {new_cmd}' instead.[/yellow]")
    console.print()


@click.group(name='service')
def service_group():
    """[DEPRECATED] Manage RAG Memory services.

    These commands are deprecated. Use 'rag instance' commands instead:

        rag instance start <name>
        rag instance stop <name>
        rag instance list
        rag instance status <name>
    """
    pass


@service_group.command(name='start')
def start_command():
    """[DEPRECATED] Start RAG Memory services."""
    _show_deprecation_warning('start', 'start <name>')

    instance_name = _get_default_instance()

    if instance_name is None:
        console.print("[bold red]No instances found.[/bold red]")
        console.print("Run 'rag instance start <name>' to create one.")
        sys.exit(1)

    console.print(f"[dim]Starting instance: {instance_name}[/dim]")

    # Delegate to instance command
    from src.cli_commands.instance import start_command as instance_start
    ctx = click.Context(instance_start)
    ctx.invoke(instance_start, name=instance_name)


@service_group.command(name='stop')
def stop_command():
    """[DEPRECATED] Stop RAG Memory services."""
    _show_deprecation_warning('stop', 'stop <name>')

    instance_name = _get_default_instance()

    if instance_name is None:
        console.print("[bold red]No instances found.[/bold red]")
        sys.exit(1)

    from src.cli_commands.instance import stop_command as instance_stop
    ctx = click.Context(instance_stop)
    ctx.invoke(instance_stop, name=instance_name)


@service_group.command(name='restart')
def restart_command():
    """[DEPRECATED] Restart RAG Memory services."""
    _show_deprecation_warning('restart', 'stop <name> && rag instance start <name>')

    instance_name = _get_default_instance()

    if instance_name is None:
        console.print("[bold red]No instances found.[/bold red]")
        sys.exit(1)

    from src.cli_commands.instance import stop_command, start_command

    ctx = click.Context(stop_command)
    ctx.invoke(stop_command, name=instance_name)

    ctx = click.Context(start_command)
    ctx.invoke(start_command, name=instance_name)


@service_group.command(name='status')
def status_command():
    """[DEPRECATED] Check status of RAG Memory services."""
    _show_deprecation_warning('status', 'list OR rag instance status <name>')

    # Show all instances
    from src.cli_commands.instance import list_command
    ctx = click.Context(list_command)
    ctx.invoke(list_command)


# Shortcuts for top-level commands (also deprecated)
start = start_command
stop = stop_command
restart = restart_command
status = status_command
```

---

### 4.6 Update Scripts Migration

#### 4.6.1 `scripts/update_mcp.py`

Add `--instance` parameter and update container references.

Add after argument parser setup:

```python
parser.add_argument(
    '--instance', '-i',
    default=None,
    help='Instance name to update (default: prompts if multiple instances exist)'
)
```

Add function to resolve instance:

```python
def resolve_instance(instance_arg: str) -> str:
    """Resolve which instance to update.

    Args:
        instance_arg: Instance name from --instance flag, or None

    Returns:
        Instance name to use
    """
    import platformdirs
    import json

    config_dir = Path(platformdirs.user_config_dir('rag-memory', appauthor=False))
    instances_file = config_dir / 'instances.json'

    if not instances_file.exists():
        print_error("No instances found. Run setup.py first.")
        sys.exit(1)

    with open(instances_file) as f:
        data = json.load(f)

    instances = data.get('instances', [])

    if not instances:
        print_error("No instances registered.")
        sys.exit(1)

    if instance_arg:
        # Validate provided instance exists
        names = [i['name'] for i in instances]
        if instance_arg not in names:
            print_error(f"Instance '{instance_arg}' not found.")
            print_info(f"Available instances: {', '.join(names)}")
            sys.exit(1)
        return instance_arg

    if len(instances) == 1:
        return instances[0]['name']

    # Multiple instances - prompt user
    print_info("Multiple instances found:")
    for i, inst in enumerate(instances, 1):
        print(f"  {i}. {inst['name']}")

    while True:
        choice = input(f"{Colors.CYAN}Select instance (1-{len(instances)}): {Colors.RESET}").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(instances):
                return instances[idx]['name']
        except ValueError:
            pass
        print_error("Invalid choice")
```

Update container name references:

```python
# Replace hardcoded container names
instance_name = resolve_instance(args.instance)
MCP_CONTAINER = f"rag-memory-mcp-{instance_name}"
PROJECT_NAME = f"rag-memory-{instance_name}"
```

#### 4.6.2 `scripts/update_databases.py`

Same pattern as update_mcp.py - add `--instance` parameter and resolve function.

---

### 4.7 CLI Registration

**File:** `src/cli.py`

Add the new instance command group:

```python
# Add import
from src.cli_commands.instance import instance_group

# Register command group (add after service_group)
main.add_command(instance_group)  # rag instance start/stop/delete/list/status
```

---

## 5. Migration Strategy

### For New Users

New users running setup.py will:
1. Be prompted for an instance name (default: "default")
2. Get the multi-instance compose template installed
3. Have instances.json created with their first instance
4. See new CLI commands in help output

### For Existing Single-Instance Users

#### Automatic Migration (Recommended)

Add migration logic to setup.py that detects legacy setup:

```python
def migrate_legacy_setup(config_dir: Path) -> bool:
    """Migrate from single-instance to multi-instance setup.

    Detects legacy setup by presence of docker-compose.yml without instances.json.
    Creates instances.json with existing containers registered as 'default' instance.
    """
    compose_file = config_dir / 'docker-compose.yml'
    instances_file = config_dir / 'instances.json'
    env_file = config_dir / '.env'

    # Already migrated
    if instances_file.exists():
        return False

    # No legacy setup
    if not compose_file.exists():
        return False

    print_header("Migrating to Multi-Instance Support")
    print_info("Detected legacy single-instance setup.")
    print_info("Migrating to multi-instance architecture...")

    # Read existing ports from .env
    ports = {
        'postgres': 54320,
        'neo4j_bolt': 7687,
        'neo4j_http': 7474,
        'mcp': 8000,
    }

    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    if key == 'PROD_POSTGRES_PORT':
                        ports['postgres'] = int(value)
                    elif key == 'PROD_NEO4J_BOLT_PORT':
                        ports['neo4j_bolt'] = int(value)
                    elif key == 'PROD_NEO4J_HTTP_PORT':
                        ports['neo4j_http'] = int(value)
                    elif key == 'MCP_SSE_PORT':
                        ports['mcp'] = int(value)

    # Create instances.json
    instances_data = {
        "version": 1,
        "instances": [
            {
                "name": "default",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "ports": ports,
                "config_overrides": {},
                "migrated_from_legacy": True
            }
        ]
    }

    with open(instances_file, 'w') as f:
        json.dump(instances_data, f, indent=2)

    print_success("Created instances.json with 'default' instance")
    print_info("Your existing containers are now registered as the 'default' instance")
    print_info("Use 'rag instance list' to see your instances")
    print_info("Use 'rag instance start <name>' to create additional instances")

    return True
```

Call this at the start of main():

```python
def main():
    # Check for and perform migration before anything else
    config_dir = Path(platformdirs.user_config_dir('rag-memory', appauthor=False))
    if migrate_legacy_setup(config_dir):
        print()
        response = input(f"{Colors.CYAN}Continue with setup to update configuration? (yes/no): {Colors.RESET}").strip().lower()
        if response != "yes":
            print_info("Migration complete. Run 'rag instance list' to see your instances.")
            sys.exit(0)

    # Continue with normal setup...
```

### Container Renaming (Manual Step)

Existing containers have `-local` suffix. After migration, users should:

1. Stop old containers: `docker compose -f ~/.config/rag-memory/docker-compose.yml down`
2. Start new: `rag instance start default`

The new containers will have `-default` suffix. Old containers can be removed manually.

---

## 6. Testing Plan

### Unit Tests

**File:** `tests/unit/test_instance_registry.py`

```python
"""Unit tests for instance registry."""

import json
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.core.instance_registry import InstanceRegistry, get_instance_registry


class TestInstanceRegistry:

    @pytest.fixture
    def temp_config_dir(self):
        with TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def registry(self, temp_config_dir):
        return InstanceRegistry(temp_config_dir)

    def test_empty_registry(self, registry):
        """New registry should have no instances."""
        assert registry.list_instances() == []

    def test_register_instance(self, registry):
        """Should register instance with auto-assigned ports."""
        instance = registry.register("primary")

        assert instance['name'] == "primary"
        assert instance['ports']['postgres'] == 54320
        assert instance['ports']['neo4j_bolt'] == 7687
        assert instance['ports']['mcp'] == 8000

    def test_register_multiple_instances(self, registry):
        """Each instance should get unique ports."""
        inst1 = registry.register("first")
        inst2 = registry.register("second")
        inst3 = registry.register("third")

        assert inst1['ports']['postgres'] == 54320
        assert inst2['ports']['postgres'] == 54330
        assert inst3['ports']['postgres'] == 54340

        assert inst1['ports']['mcp'] == 8000
        assert inst2['ports']['mcp'] == 8001
        assert inst3['ports']['mcp'] == 8002

    def test_duplicate_name_raises(self, registry):
        """Should raise on duplicate instance name."""
        registry.register("test")

        with pytest.raises(ValueError, match="already exists"):
            registry.register("test")

    def test_invalid_name_raises(self, registry):
        """Should raise on invalid instance name."""
        with pytest.raises(ValueError, match="alphanumeric"):
            registry.register("invalid name!")

    def test_get_instance(self, registry):
        """Should retrieve instance by name."""
        registry.register("test")

        instance = registry.get_instance("test")
        assert instance is not None
        assert instance['name'] == "test"

        assert registry.get_instance("nonexistent") is None

    def test_unregister(self, registry):
        """Should remove instance from registry."""
        registry.register("test")
        assert registry.instance_exists("test")

        result = registry.unregister("test")
        assert result is True
        assert not registry.instance_exists("test")

    def test_persistence(self, temp_config_dir):
        """Registry should persist across instances."""
        reg1 = InstanceRegistry(temp_config_dir)
        reg1.register("persistent")

        reg2 = InstanceRegistry(temp_config_dir)
        assert reg2.instance_exists("persistent")
```

### Integration Tests

**File:** `tests/integration/test_instance_cli.py`

```python
"""Integration tests for instance CLI commands."""

import subprocess
import pytest


class TestInstanceCLI:

    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Clean up test instances after each test."""
        yield
        # Stop and remove test instance
        subprocess.run(
            ["rag", "instance", "delete", "test-instance", "--confirm"],
            capture_output=True
        )

    def test_instance_start_creates_new(self):
        """Starting new instance should create it."""
        result = subprocess.run(
            ["rag", "instance", "start", "test-instance"],
            capture_output=True,
            text=True,
            timeout=300
        )

        assert result.returncode == 0
        assert "test-instance" in result.stdout

    def test_instance_list_shows_instances(self):
        """List should show registered instances."""
        # Create instance
        subprocess.run(["rag", "instance", "start", "test-instance"], timeout=300)

        result = subprocess.run(
            ["rag", "instance", "list"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "test-instance" in result.stdout

    def test_instance_stop_preserves_data(self):
        """Stopping instance should preserve registry entry."""
        subprocess.run(["rag", "instance", "start", "test-instance"], timeout=300)

        result = subprocess.run(
            ["rag", "instance", "stop", "test-instance"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0

        # Should still be in list
        list_result = subprocess.run(
            ["rag", "instance", "list"],
            capture_output=True,
            text=True
        )
        assert "test-instance" in list_result.stdout
```

### Manual Testing Checklist

1. [ ] Fresh install with setup.py creates instance correctly
2. [ ] `rag instance start primary` creates first instance
3. [ ] `rag instance start secondary` creates second instance with different ports
4. [ ] `rag instance list` shows both instances
5. [ ] `rag instance stop primary` stops without removing from registry
6. [ ] `rag instance start primary` restarts with same ports
7. [ ] `rag instance delete secondary --confirm` removes instance and data
8. [ ] Legacy `rag start` shows deprecation warning and works
9. [ ] After repo deletion, `rag instance` commands still work
10. [ ] Backups go to instance-specific directories

---

## 7. Documentation Updates

### 7.1 README.md

Add section after Quick Start:

```markdown
## Multi-Instance Support

RAG Memory supports running multiple independent stacks on the same machine:

```bash
# Create your first instance
rag instance start primary

# Create additional instances
rag instance start research
rag instance start production

# List all instances with status and ports
rag instance list

# Stop an instance (preserves data)
rag instance stop research

# Delete an instance (removes all data)
rag instance delete research --confirm
```

Each instance has:
- Isolated PostgreSQL and Neo4j databases
- Separate MCP server on unique port
- Instance-specific backup directory
- Automatically assigned, collision-free ports
```

### 7.2 .reference/CLI_GUIDE.md

Add new section:

```markdown
## Instance Management

### rag instance start <name>

Start a new instance or restart an existing one.

```bash
# Create and start new instance
rag instance start primary

# Restart existing instance
rag instance start primary

# Force rebuild MCP container
rag instance start primary --build
```

### rag instance stop <name>

Stop an instance without deleting data.

```bash
rag instance stop primary
```

### rag instance delete <name>

Delete an instance and optionally its data.

```bash
# Delete with confirmation prompt
rag instance delete research

# Skip confirmation
rag instance delete research --confirm

# Keep data volumes (containers only)
rag instance delete research --confirm --keep-volumes
```

### rag instance list

Show all instances with status and ports.

```bash
rag instance list
```

Output:
```
┏━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━┓
┃ Name       ┃ Status   ┃ PostgreSQL ┃ Neo4j Bolt  ┃ Neo4j HTTP  ┃ MCP  ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━┩
│ primary    │ running  │ 54320      │ 7687        │ 7474        │ 8000 │
│ research   │ stopped  │ 54330      │ 7688        │ 7475        │ 8001 │
└────────────┴──────────┴────────────┴─────────────┴─────────────┴──────┘
```

### rag instance status <name>

Show detailed status for an instance.

```bash
rag instance status primary
```

### rag instance logs <name>

View logs for an instance.

```bash
# All services
rag instance logs primary

# Specific service
rag instance logs primary --service mcp

# Follow logs
rag instance logs primary -f
```
```

### 7.3 CLAUDE.md

Update Architecture section:

```markdown
## Multi-Instance Architecture

RAG Memory supports running multiple independent stacks. Each instance consists of:

- PostgreSQL container: `rag-memory-postgres-{instance_name}`
- Neo4j container: `rag-memory-neo4j-{instance_name}`
- MCP server container: `rag-memory-mcp-{instance_name}`
- Backup container: `rag-memory-backup-{instance_name}`

Instance state is stored in `~/.config/rag-memory/instances.json`.

### Port Allocation

Ports are automatically assigned to prevent collisions:

| Instance # | PostgreSQL | Neo4j Bolt | Neo4j HTTP | MCP  |
|------------|------------|------------|------------|------|
| 1          | 54320      | 7687       | 7474       | 8000 |
| 2          | 54330      | 7688       | 7475       | 8001 |
| 3          | 54340      | 7689       | 7476       | 8002 |

### Key Files

- `src/core/instance_registry.py` - Instance registry management
- `src/cli_commands/instance.py` - CLI commands
- `deploy/docker/compose/docker-compose.instance.yml` - Parameterized template
```

---

## 8. Implementation Checklist

### Phase 1: Core Infrastructure

- [ ] Create `src/core/instance_registry.py`
- [ ] Create `src/cli_commands/instance.py`
- [ ] Create `deploy/docker/compose/docker-compose.instance.yml`
- [ ] Add `tabulate` to `pyproject.toml` dependencies
- [ ] Register instance commands in `src/cli.py`
- [ ] Write unit tests for instance registry

### Phase 2: Setup Script Updates

- [ ] Add instance name prompt to setup.py
- [ ] Update `create_config_yaml` for multi-instance
- [ ] Update `build_and_start_containers` for instances
- [ ] Update container name references throughout setup.py
- [ ] Update `wait_for_health_checks` for instances
- [ ] Update `print_final_summary` for instances
- [ ] Add migration logic for legacy setups

### Phase 3: Legacy Support

- [ ] Update `src/cli_commands/service.py` with deprecation
- [ ] Update `scripts/update_mcp.py` with `--instance` flag
- [ ] Update `scripts/update_databases.py` with `--instance` flag

### Phase 4: Testing

- [ ] Run unit tests for instance registry
- [ ] Run integration tests for CLI commands
- [ ] Test fresh installation with setup.py
- [ ] Test migration from legacy setup
- [ ] Test multiple instances running simultaneously
- [ ] Test instance lifecycle (create, stop, start, delete)
- [ ] Test repo deletion scenario

### Phase 5: Documentation

- [ ] Update README.md
- [ ] Update .reference/CLI_GUIDE.md
- [ ] Update .reference/INSTALLATION.md
- [ ] Update CLAUDE.md

### Phase 6: Cleanup

- [ ] Mark old compose files as deprecated
- [ ] Update any remaining hardcoded container names
- [ ] Review and update error messages
- [ ] Final code review

---

## Appendix: Environment Variables Reference

### Instance-Specific Variables (set by CLI)

| Variable | Description | Example |
|----------|-------------|---------|
| `INSTANCE_NAME` | Instance identifier | `primary` |
| `POSTGRES_PORT` | Host port for PostgreSQL | `54320` |
| `NEO4J_BOLT_PORT` | Host port for Neo4j Bolt | `7687` |
| `NEO4J_HTTP_PORT` | Host port for Neo4j Browser | `7474` |
| `MCP_PORT` | Host port for MCP server | `8000` |
| `BACKUP_ARCHIVE_PATH` | Instance backup directory | `~/.config/rag-memory/backups/primary` |
| `RAG_CONFIG_DIR` | Path to config directory | `~/.config/rag-memory` |

### Shared Variables (from config.yaml)

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_USER` | PostgreSQL username | `raguser` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `ragpassword` |
| `POSTGRES_DB` | PostgreSQL database | `rag_memory` |
| `NEO4J_USER` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | `graphiti-password` |
| `BACKUP_CRON_EXPRESSION` | Backup schedule | `5 2 * * *` |
| `BACKUP_RETENTION_DAYS` | Days to keep backups | `14` |

---

**End of Implementation Plan**
