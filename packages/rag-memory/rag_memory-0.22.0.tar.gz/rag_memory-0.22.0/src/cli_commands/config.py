"""Configuration management commands."""

import os
import subprocess
import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from src.core.config_loader import (
    get_config_path,
    load_config,
    save_config,
    is_legacy_config,
    list_configured_instances,
    REQUIRED_INSTANCE_KEYS,
    OPTIONAL_INSTANCE_KEYS,
)

console = Console()


@click.group()
def config():
    """Manage RAG Memory configuration."""
    pass


@config.command("show")
@click.option("--path", is_flag=True, help="Show config file path only")
def config_show(path):
    """Display current configuration.

    Shows the configuration from the active config.yaml file, including
    server settings and mounted directories. Sensitive values like API
    keys are masked for security.

    Examples:
        # Show full configuration
        rag config show

        # Show config file path
        rag config show --path
    """
    try:
        config_path = get_config_path()

        if path:
            console.print(f"[cyan]{config_path}[/cyan]")
            return

        if not config_path.exists():
            console.print(f"[yellow]⚠ Config file not found[/yellow]")
            console.print(f"Expected location: {config_path}")
            console.print("\n[dim]Run 'python scripts/setup.py' to create configuration[/dim]")
            sys.exit(1)

        # Load and display config
        config_data = load_config(config_path)

        if not config_data:
            console.print(f"[yellow]⚠ Config file is empty or invalid[/yellow]")
            console.print(f"Location: {config_path}")
            sys.exit(1)

        console.print(f"[bold blue]Configuration File:[/bold blue] {config_path}\n")

        # Check if using new instance-based format or legacy format
        if is_legacy_config(config_data):
            # Legacy format - display server settings
            console.print("[yellow]⚠ Legacy configuration format detected[/yellow]")
            console.print("[dim]Run 'python scripts/setup.py' to migrate to multi-instance format[/dim]\n")

            server_config = config_data.get('server', {})
            if server_config:
                console.print("[bold cyan]Server Settings:[/bold cyan]")
                for key, value in server_config.items():
                    if 'key' in key.lower() or 'password' in key.lower():
                        masked_value = str(value)[:8] + '...' if len(str(value)) > 8 else '***'
                        console.print(f"  {key}: [dim]{masked_value}[/dim]")
                    else:
                        console.print(f"  {key}: {value}")
                console.print()

            mounts = config_data.get('mounts', [])
            if mounts:
                console.print("[bold cyan]Mounted Directories:[/bold cyan]")
                for mount in mounts:
                    mount_path = mount.get('path', 'N/A')
                    read_only = mount.get('read_only', True)
                    ro_label = "[dim](read-only)[/dim]" if read_only else "[yellow](read-write)[/yellow]"
                    console.print(f"  • {mount_path} {ro_label}")
                console.print()
        else:
            # New instance-based format
            instances = config_data.get('instances', {})
            if not instances:
                console.print("[yellow]⚠ No instances configured[/yellow]")
                console.print("[dim]Run 'python scripts/setup.py' to create an instance[/dim]")
                return

            console.print(f"[bold cyan]Configured Instances: {len(instances)}[/bold cyan]\n")

            for instance_name, instance_config in instances.items():
                console.print(f"[bold green]Instance: {instance_name}[/bold green]")

                # Display settings with sensitive value masking
                for key, value in instance_config.items():
                    if key == 'mounts':
                        continue  # Show mounts separately
                    if 'key' in key.lower() or 'password' in key.lower():
                        masked_value = str(value)[:8] + '...' if len(str(value)) > 8 else '***'
                        console.print(f"  {key}: [dim]{masked_value}[/dim]")
                    else:
                        console.print(f"  {key}: {value}")

                # Display mounts for this instance
                mounts = instance_config.get('mounts', [])
                if mounts:
                    console.print("  [cyan]mounts:[/cyan]")
                    for mount in mounts:
                        mount_path = mount.get('path', 'N/A')
                        read_only = mount.get('read_only', True)
                        ro_label = "[dim](ro)[/dim]" if read_only else "[yellow](rw)[/yellow]"
                        console.print(f"    • {mount_path} {ro_label}")

                console.print()  # Blank line between instances

    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        sys.exit(1)


@config.command("edit")
def config_edit():
    """Open configuration file in system editor.

    Opens the config.yaml file in your default text editor. The editor
    is determined by the $EDITOR environment variable (defaults to 'nano'
    on Unix systems, 'notepad' on Windows).

    Examples:
        # Edit with default editor
        rag config edit

        # Use specific editor (bash)
        EDITOR=vim rag config edit
    """
    try:
        config_path = get_config_path()

        if not config_path.exists():
            console.print(f"[yellow]⚠ Config file not found[/yellow]")
            console.print(f"Expected location: {config_path}")
            console.print("\n[dim]Run 'python scripts/setup.py' to create configuration[/dim]")
            sys.exit(1)

        # Determine editor to use
        if os.name == 'nt':
            # Windows
            editor = os.getenv('EDITOR', 'notepad')
        else:
            # Unix-like systems
            editor = os.getenv('EDITOR', 'nano')

        console.print(f"[dim]Opening {config_path} with {editor}...[/dim]\n")

        # Open editor
        try:
            subprocess.run([editor, str(config_path)], check=True)
            console.print("\n[bold green]✓ Editor closed[/bold green]")
        except subprocess.CalledProcessError:
            console.print(f"[bold red]✗ Editor exited with error[/bold red]")
            sys.exit(1)
        except FileNotFoundError:
            console.print(f"[bold red]✗ Editor '{editor}' not found[/bold red]")
            console.print("[yellow]Set the $EDITOR environment variable to your preferred editor[/yellow]")
            sys.exit(1)

    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        sys.exit(1)


@config.command("set")
@click.argument("key")
@click.argument("value")
@click.option("--instance", "-i", default=None, help="Instance name (required for multi-instance configs)")
def config_set(key, value, instance):
    """Set a specific configuration value for an instance.

    Updates a configuration key in the config.yaml file. For multi-instance
    configurations, you must specify which instance to update with --instance.

    Examples:
        # Set API key for an instance
        rag config set openai_api_key sk-xxx --instance primary

        # Set database URL
        rag config set database_url postgresql://user:pass@localhost:5432/db -i primary

        # Set optional Graphiti model
        rag config set graphiti_model gpt-4 --instance research
    """
    try:
        config_path = get_config_path()

        # Load existing config or create empty
        if config_path.exists():
            config_data = load_config(config_path)
        else:
            console.print(f"[yellow]⚠ Config file not found[/yellow]")
            console.print("[dim]Run 'python scripts/setup.py' to create configuration[/dim]")
            sys.exit(1)

        # Normalize key to lowercase with underscores
        normalized_key = key.lower().replace('-', '_')

        # Handle new instance-based format
        if not is_legacy_config(config_data):
            instances = config_data.get('instances', {})

            if not instance:
                # If only one instance, use it by default
                if len(instances) == 1:
                    instance = list(instances.keys())[0]
                    console.print(f"[dim]Using instance: {instance}[/dim]")
                else:
                    console.print("[bold red]✗ Multiple instances configured[/bold red]")
                    console.print("Available instances:")
                    for inst_name in instances.keys():
                        console.print(f"  - {inst_name}")
                    console.print("\n[yellow]Use --instance <name> to specify which instance to update[/yellow]")
                    sys.exit(1)

            if instance not in instances:
                console.print(f"[bold red]✗ Instance '{instance}' not found[/bold red]")
                console.print("Available instances:")
                for inst_name in instances.keys():
                    console.print(f"  - {inst_name}")
                sys.exit(1)

            # Update instance config
            old_value = instances[instance].get(normalized_key)
            instances[instance][normalized_key] = value
            config_data['instances'] = instances
        else:
            # Legacy format - update server section
            if 'server' not in config_data:
                config_data['server'] = {}
            old_value = config_data['server'].get(normalized_key)
            config_data['server'][normalized_key] = value

        # Save config
        if save_config(config_data, config_path):
            target = f"instances.{instance}.{normalized_key}" if not is_legacy_config(config_data) else f"server.{normalized_key}"
            if old_value:
                console.print(f"[bold green]✓ Updated {target}[/bold green]")
                # Don't show old/new values for sensitive keys
                if 'key' not in normalized_key and 'password' not in normalized_key:
                    console.print(f"  Old: {old_value}")
                    console.print(f"  New: {value}")
            else:
                console.print(f"[bold green]✓ Set {target} = {value}[/bold green]")

            console.print(f"\n[dim]Config saved to {config_path}[/dim]")
        else:
            console.print(f"[bold red]✗ Failed to save configuration[/bold red]")
            sys.exit(1)

    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        sys.exit(1)
