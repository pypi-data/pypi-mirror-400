#!/usr/bin/env python3
"""
RAG Memory Local Deployment Setup Script

One-command setup for end users deploying RAG Memory locally:
1. Checks Docker is installed and running
2. Checks for existing local containers
3. Prompts for OpenAI API key
4. Prompts for backup schedule and location
5. Prompts for directory mounts
6. Creates system-level configuration files
7. Builds and starts containers
8. Validates all services are healthy
9. Provides connection details and management commands

Cross-platform: macOS, Linux, Windows (with Docker Desktop)
"""

import os
import sys
import socket
import subprocess
import time
import signal
import asyncio
from pathlib import Path
from typing import Tuple, Optional
import json
import re


class Colors:
    """ANSI color codes for terminal output"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"


def print_header(text: str):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.RESET}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")


def run_command(cmd: list, check: bool = True, timeout: int = None, env: dict = None) -> Tuple[int, str, str]:
    """Run shell command and return exit code, stdout, stderr"""
    try:
        # If env is provided, use it; otherwise use os.environ
        run_env = env if env is not None else os.environ
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=run_env
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)


def get_docker_compose_command() -> list:
    """Detect which docker compose command is available (cross-platform)

    Modern Docker Desktop uses 'docker compose' (space)
    Older installations use 'docker-compose' (hyphen)
    """
    # Try new format first (docker compose)
    code, _, _ = run_command(["docker", "compose", "version"])
    if code == 0:
        return ["docker", "compose"]
    # Fall back to old format (docker-compose)
    return ["docker-compose"]


def convert_path_for_docker(path_str: str) -> str:
    """Convert Windows paths to Docker-compatible format

    Windows: C:\\Users\\name\\Documents
    Docker:  /c/Users/name/Documents

    On Mac/Linux, returns path unchanged.
    """
    if os.name == 'nt':  # Windows only
        path_obj = Path(path_str).resolve()  # Get absolute path
        if path_obj.is_absolute() and path_obj.drive:
            # Convert C: to /c, D: to /d, etc.
            drive = path_obj.drive.replace(':', '').lower()
            # Remove drive and convert backslashes to forward slashes
            rest = str(path_obj).replace(path_obj.drive, '').replace('\\', '/')
            return f"/{drive}{rest}"
    # Mac/Linux: return unchanged
    return str(path_str)


def check_python_dependencies() -> bool:
    """Verify required Python packages are installed before proceeding.

    This prevents the setup from failing 30+ minutes in when it tries to
    import dependencies that weren't installed with 'uv sync'.

    Returns:
        bool: True if all dependencies are available, False otherwise
    """
    print_header("STEP 0: Checking Python Dependencies")

    # Critical dependencies that setup.py needs
    required_packages = {
        'graphiti_core': 'graphiti-core',
        'platformdirs': 'platformdirs',
        'yaml': 'PyYAML'
    }

    missing = []

    # Try importing each package
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
            print_success(f"{package_name} is installed")
        except ImportError:
            print_error(f"{package_name} is NOT installed")
            missing.append(package_name)

    if missing:
        print_error(f"\nMissing {len(missing)} required package(s)")
        print_info("\nTo fix this, run these commands in order:")
        print_info(f"  {Colors.BOLD}1. uv sync{Colors.RESET}")
        print_info(f"  {Colors.BOLD}2. source .venv/bin/activate{Colors.RESET}  {Colors.YELLOW}# Linux/macOS{Colors.RESET}")
        print_info(f"     {Colors.BOLD}.venv\\Scripts\\activate{Colors.RESET}      {Colors.YELLOW}# Windows{Colors.RESET}")
        print_info(f"  {Colors.BOLD}3. python scripts/setup.py{Colors.RESET}")
        print_info("\nThe 'uv sync' command installs all project dependencies into a virtual environment.")
        print_info("You must activate that environment before running setup.py.")
        return False

    print_success("All required Python dependencies are installed")
    return True


def check_docker_installed() -> bool:
    """Check if Docker is installed"""
    print_header("STEP 1: Checking Docker Installation")

    code, _, _ = run_command(["docker", "--version"])

    if code == 0:
        print_success("Docker is installed")
        return True

    print_error("Docker is not installed")
    print_info("Please install Docker Desktop from: https://www.docker.com/products/docker-desktop")
    print_info("After installation, run this script again")
    return False


def check_docker_running() -> bool:
    """Check if Docker daemon is running"""
    print_header("STEP 2: Checking Docker Daemon")

    code, _, _ = run_command(["docker", "ps"])

    if code == 0:
        print_success("Docker daemon is running")
        return True

    print_error("Docker daemon is not running")
    print_info("Start Docker Desktop and try again")
    return False


def check_existing_containers() -> bool:
    """Check if RAG Memory local deployment containers are already running"""
    print_header("STEP 3: Checking for Existing RAG Memory Containers")

    # Check for LOCAL deployment containers (rag-memory-postgres-local, rag-memory-neo4j-local, NOT -dev or -test)
    postgres_code, _, _ = run_command(["docker", "container", "inspect", "rag-memory-postgres-local"])
    neo4j_code, _, _ = run_command(["docker", "container", "inspect", "rag-memory-neo4j-local"])

    postgres_exists = postgres_code == 0
    neo4j_exists = neo4j_code == 0

    if not (postgres_exists or neo4j_exists):
        print_info("No existing RAG Memory local containers found")
        return False

    # Found existing local containers
    print_warning("Found existing RAG Memory local containers")
    print_warning("This will destroy any data in PostgreSQL and Neo4j")

    response = input(f"\n{Colors.YELLOW}Proceed with setup? This will rebuild containers (yes/no): {Colors.RESET}").strip().lower()

    if response != "yes":
        print_info("Setup cancelled")
        return True

    print_info("Stopping and removing existing containers...")
    compose_file = Path(__file__).parent.parent / 'deploy' / 'docker' / 'compose' / 'docker-compose.yml'
    docker_compose_cmd = get_docker_compose_command()
    run_command(docker_compose_cmd + ["-f", str(compose_file), "down", "-v"])
    print_success("Existing containers removed")
    return False


def prompt_for_api_key() -> str:
    """Prompt user for OpenAI API key"""
    print_header("STEP 4: OpenAI API Key")

    print_info("You need an OpenAI API key to generate embeddings")
    print_info("Get one here: https://platform.openai.com/api/keys")
    print()

    while True:
        api_key = input(f"{Colors.CYAN}Enter your OpenAI API key (sk-...): {Colors.RESET}").strip()

        if api_key.startswith("sk-") and len(api_key) > 20:
            print_success(f"API key accepted: {api_key[:20]}...{api_key[-4:]}")
            return api_key

        print_error("Invalid API key format. Must start with 'sk-' and be at least 20 characters")


def is_port_available(port: int) -> bool:
    """Check if a port is available using a test HTTP server"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result != 0
    except Exception:
        return True


def find_available_ports(recheck: bool = False) -> dict:
    """Find available ports for services

    Args:
        recheck: If True, this is a recheck right before container start (different messaging)
    """
    if recheck:
        print_info("Verifying ports are still available before starting containers...")
    else:
        print_header("STEP 5: Finding Available Ports")

    default_ports = {
        "postgres": 54320,
        "neo4j_http": 7474,
        "neo4j_bolt": 7687,
        "mcp": 18000,  # Changed from 8000 to avoid common dev server conflicts
    }

    available_ports = {}

    for service, port in default_ports.items():
        original_port = port
        max_attempts = 10
        attempt = 0

        while attempt < max_attempts:
            if is_port_available(port):
                available_ports[service] = port
                if not recheck:
                    if port == original_port:
                        print_success(f"{service}: {port} (default)")
                    else:
                        print_warning(f"{service}: {port} (default {original_port} was unavailable)")
                else:
                    # During recheck, only report if port changed
                    if port != original_port:
                        print_warning(f"{service}: {port} (changed from default {original_port})")
                break

            port += 1
            attempt += 1

        if attempt >= max_attempts:
            if recheck:
                print_error(f"Port conflict detected: Could not find available port for {service}")
                print_error(f"Another process grabbed ports since initial check.")
                print_info(f"Kill the process using ports near {original_port} or re-run setup.")
            else:
                print_error(f"Could not find available port for {service}")
            return None

    if recheck:
        print_success("All ports verified available")

    return available_ports


def configure_directory_mounts() -> list:
    """
    Prompt user for read-only directory mounts for file/directory ingestion.

    Returns:
        List of mount configurations with 'path' and 'read_only' keys
    """
    print_header("STEP 6: Configure Directory Access for File Ingestion")

    print_info("The MCP server needs read-only access to directories on your system")
    print_info("to ingest files and documents.\n")

    mounts = []

    # Detect home directory
    home_dir = str(Path.home())
    print_info(f"Detected home directory: {home_dir}")
    print_info("We recommend mounting your home directory as read-only.\n")

    use_home = input(f"{Colors.CYAN}Mount home directory as read-only? (yes/no, default: yes): {Colors.RESET}").strip().lower()
    if use_home != "no":
        mounts.append({
            "path": home_dir,
            "read_only": True
        })
        print_success(f"Added mount: {home_dir} (read-only)")

    # Option to add custom directories
    while True:
        add_more = input(f"\n{Colors.CYAN}Add additional directories? (yes/no, default: no): {Colors.RESET}").strip().lower()
        if add_more == "no" or add_more == "":
            break

        custom_path = input(f"{Colors.CYAN}Enter directory path: {Colors.RESET}").strip()

        # Validate directory exists and is readable
        try:
            path_obj = Path(custom_path).expanduser().resolve()
            if not path_obj.exists():
                print_error(f"Directory does not exist: {path_obj}")
                continue

            if not path_obj.is_dir():
                print_error(f"Not a directory: {path_obj}")
                continue

            # Try to list directory to verify readability
            try:
                list(path_obj.iterdir())
            except PermissionError:
                print_error(f"Directory is not readable: {path_obj}")
                continue

            mounts.append({
                "path": str(path_obj),
                "read_only": True
            })
            print_success(f"Added mount: {path_obj} (read-only)")
        except Exception as e:
            print_error(f"Invalid path: {e}")

    if not mounts:
        print_warning("No directories configured for file ingestion")
        print_warning("The MCP server will not be able to ingest files from your system")
        response = input(f"\n{Colors.YELLOW}Continue without any mounted directories? (yes/no): {Colors.RESET}").strip().lower()
        if response != "yes":
            print_info("Setup cancelled")
            return None

    return mounts


def prompt_for_backup_schedule() -> str:
    """
    Prompt user for backup schedule in LOCAL time and convert to UTC for container.
    
    The backup container runs in UTC timezone, so we automatically convert
    the user's local time to UTC to ensure backups run at the expected time.

    Returns:
        Cron schedule string in UTC (e.g., "5 14 * * *" for 10:05 AM EDT = 14:05 UTC)
    """
    from datetime import datetime, timedelta
    
    print_header("STEP 7: Configure Backup Schedule")

    # Detect system timezone
    try:
        local_tz = time.tzname[time.daylight]
        print_info(f"Detected timezone: {local_tz}")
    except:
        local_tz = "Local Time"
    
    print_info("Backups will run automatically at the time you specify in YOUR LOCAL TIME")
    print_info("(Format: HH:MM in 24-hour format, e.g., 02:05 for 2:05 AM)")
    print_info("The system will automatically convert to UTC for the backup container\n")

    while True:
        backup_time = input(f"{Colors.CYAN}Enter backup time in {local_tz} (HH:MM, default: 02:05): {Colors.RESET}").strip()

        # Use default if empty
        if not backup_time:
            backup_time = "02:05"

        # Validate format
        try:
            parts = backup_time.split(':')
            if len(parts) != 2:
                print_error("Invalid format. Use HH:MM (e.g., 14:30)")
                continue

            hour = int(parts[0])
            minute = int(parts[1])

            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                print_error("Invalid time. Hour must be 0-23, minute must be 0-59")
                continue

            # Create datetime for today at the specified time
            now_local = datetime.now()
            backup_datetime_local = now_local.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Convert to UTC
            # Get UTC offset in seconds
            utc_offset_seconds = time.timezone if not time.daylight else time.altzone
            utc_offset_hours = utc_offset_seconds / 3600
            
            backup_datetime_utc = backup_datetime_local + timedelta(hours=utc_offset_hours)
            
            # Extract UTC hour and minute
            utc_hour = backup_datetime_utc.hour
            utc_minute = backup_datetime_utc.minute

            # Convert to cron format (minute hour * * *)
            cron_schedule = f"{utc_minute} {utc_hour} * * *"
            
            print_success(f"Backup schedule: Daily at {backup_time} {local_tz}")
            print_info(f"Container will use: {utc_hour:02d}:{utc_minute:02d} UTC → cron: {cron_schedule}")
            return cron_schedule

        except ValueError:
            print_error("Invalid format. Use HH:MM (e.g., 14:30)")


def prompt_for_backup_location() -> str:
    """
    Prompt user for backup archive directory location.

    Returns:
        Path to backup directory (can be absolute or relative)
    """
    print_header("STEP 8: Configure Backup Location")

    print_info("Backups will be stored as .tar.gz files in this directory")
    print_info("Use absolute path (e.g., /Users/name/rag-backups) or relative (e.g., ./backups)\n")

    default_location = "./backups"
    backup_location = input(f"{Colors.CYAN}Backup directory (default: {default_location}): {Colors.RESET}").strip()

    if not backup_location:
        backup_location = default_location

    print_success(f"Backup location: {backup_location}")
    return backup_location

def prompt_for_backup_retention() -> int:
    """
    Prompt user for backup retention period in days.
    
    Returns:
        Number of days to keep backups (positive integer)
    """
    print_header("STEP 9: Configure Backup Retention")
    
    print_info("Old backups will be automatically deleted after the retention period")
    print_info("This prevents your disk from filling up with unlimited backups")
    print_info("Recommended: 7-30 days depending on your needs\n")
    
    while True:
        retention_input = input(f"{Colors.CYAN}Keep backups for how many days? (default: 14): {Colors.RESET}").strip()
        
        # Use default if empty
        if not retention_input:
            retention_days = 14
            break
        
        # Validate input
        try:
            retention_days = int(retention_input)
            if retention_days < 1:
                print_error("Retention must be at least 1 day")
                continue
            if retention_days > 365:
                print_warning("Retention period over 1 year - this may use significant disk space")
                confirm = input(f"{Colors.YELLOW}Continue with {retention_days} days? (yes/no): {Colors.RESET}").strip().lower()
                if confirm != "yes":
                    continue
            break
        except ValueError:
            print_error("Please enter a valid number")
    
    print_success(f"Backup retention: {retention_days} days")
    print_info(f"Backups older than {retention_days} days will be automatically deleted")
    return retention_days


def prompt_for_entity_extraction_quality() -> int:
    """
    Prompt user for entity extraction quality level.

    This controls Graphiti's reflexion iterations - recursive entity extraction
    that improves quality but increases costs and processing time.

    Returns:
        Number of reflexion iterations (0-2)
    """
    print_header("STEP 10: Entity Extraction Quality (Optional)")

    print_info("RAG Memory uses AI to extract entities and relationships from your documents.")
    print_info("You can choose between:")
    print_info("  • Standard quality (default, faster and cheaper)")
    print_info("  • Enhanced quality (slower but more thorough)\n")

    print(f"{Colors.BOLD}Standard Quality (Recommended):{Colors.RESET}")
    print("  • Single-pass extraction")
    print("  • Fast processing (~30-60 seconds per document)")
    print("  • Lower cost (~$0.01 per document)")
    print("  • Good for most use cases\n")

    print(f"{Colors.BOLD}Enhanced Quality:{Colors.RESET}")
    print("  • Multi-pass recursive extraction")
    print("  • Catches entities that might be missed in first pass")
    print("  • Slower processing (2-3x longer)")
    print("  • Higher cost (2-3x more expensive)")
    print("  • Best for critical content where completeness matters\n")

    print_warning("⚠  Enhanced quality increases processing time and OpenAI API costs")
    print_info("ℹ  Only affects ingestion (ingest_text, ingest_url), not search")
    print_info("ℹ  You can always change this later in your config file\n")

    while True:
        choice = input(
            f"{Colors.CYAN}Choose quality level:\n"
            f"  0 = Standard (default, recommended)\n"
            f"  1 = Enhanced (1 additional pass)\n"
            f"  2 = High (2 additional passes, expensive)\n"
            f"Enter choice (0-2, default: 0): {Colors.RESET}"
        ).strip()

        # Default to 0 if empty
        if choice == "":
            choice = "0"

        if choice in ["0", "1", "2"]:
            level = int(choice)

            if level == 0:
                print_success("Using standard quality (fast, cost-effective)")
            elif level == 1:
                print_warning("Using enhanced quality (1 additional pass)")
                print_warning("This will approximately double processing time and costs")
                confirm = input(f"{Colors.YELLOW}Confirm enhanced quality? (yes/no): {Colors.RESET}").strip().lower()
                if confirm != "yes":
                    print_info("Reverting to standard quality")
                    level = 0
                else:
                    print_success("Enhanced quality confirmed")
            else:  # level == 2
                print_warning("Using high quality (2 additional passes)")
                print_warning("This will approximately triple processing time and costs")
                print_warning("Only recommended for critical documents")
                confirm = input(f"{Colors.YELLOW}Are you sure? (yes/no): {Colors.RESET}").strip().lower()
                if confirm != "yes":
                    print_info("Reverting to standard quality")
                    level = 0
                else:
                    print_success("High quality confirmed")

            return level

        print_error("Invalid choice. Please enter 0, 1, or 2")


def prompt_for_instance_name() -> str:
    """
    Prompt user for instance name.

    Instance names are used to identify and manage multiple RAG Memory stacks.
    The first instance is typically named "primary" or "default".

    Returns:
        Valid instance name (alphanumeric, hyphens, underscores only)
    """
    print_header("STEP 11: Instance Name")

    print_info("RAG Memory supports multiple isolated instances, each with its own")
    print_info("PostgreSQL, Neo4j, MCP server, and backup service.")
    print_info("")
    print_info("The instance name is used to identify containers and data volumes.")
    print_info("Examples: 'primary', 'research', 'project-x', 'dev'\n")

    # Load existing instances to check for conflicts
    import platformdirs
    import yaml as yaml_check
    config_dir = Path(platformdirs.user_config_dir('rag-memory', appauthor=False))
    config_path = config_dir / 'config.yaml'
    existing_instances = set()
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = yaml_check.safe_load(f) or {}
                existing_instances = set(config.get('instances', {}).keys())
        except Exception:
            pass

    while True:
        name = input(f"{Colors.CYAN}Enter instance name (default: primary): {Colors.RESET}").strip()

        # Use default if empty
        if not name:
            name = "primary"

        # Validate name
        if not name:
            print_error("Instance name cannot be empty")
            continue

        if not all(c.isalnum() or c in '-_' for c in name):
            print_error("Instance name must contain only letters, numbers, hyphens, and underscores")
            continue

        if name.startswith('-') or name.startswith('_'):
            print_error("Instance name cannot start with a hyphen or underscore")
            continue

        # Check if instance already exists
        if name in existing_instances:
            print_warning(f"Instance '{name}' already exists!")
            overwrite = input(f"{Colors.YELLOW}Overwrite existing instance? (yes/no): {Colors.RESET}").strip().lower()
            if overwrite != "yes":
                print_info("Choose a different name")
                continue

        print_success(f"Instance name: {name}")
        return name


def register_instance(name: str, ports: dict, config_dir: Path) -> bool:
    """
    Register instance in the instance registry.

    Args:
        name: Instance name
        ports: Dict with postgres, neo4j_bolt, neo4j_http, mcp ports
        config_dir: Path to config directory

    Returns:
        True if registered successfully
    """
    try:
        from src.core.instance_registry import get_instance_registry

        registry = get_instance_registry(config_dir)

        # Check if already exists
        if registry.instance_exists(name):
            print_warning(f"Instance '{name}' already exists in registry, updating...")
            registry.unregister(name)

        # Register with the exact ports we're using
        # Note: We override the automatic port allocation since ports were
        # already selected during setup
        registry.register(name)

        # Update ports to match what we actually selected
        # (The registry allocates ports automatically, but we want to use our selected ports)
        data = registry._load()
        for instance in data['instances']:
            if instance['name'] == name:
                instance['ports'] = ports
                registry._save(data)
                break

        print_success(f"Instance '{name}' registered in registry")
        return True

    except Exception as e:
        print_warning(f"Could not register instance: {e}")
        print_info("Instance will still work, but 'rag instance' commands may not function")
        return False


def mark_instance_initialized(name: str, config_dir: Path) -> bool:
    """
    Mark instance as fully initialized (Neo4j indices created).

    Args:
        name: Instance name
        config_dir: Path to config directory

    Returns:
        True if marked successfully
    """
    try:
        from src.core.instance_registry import get_instance_registry

        registry = get_instance_registry(config_dir)
        if registry.mark_initialized(name):
            print_success(f"Instance '{name}' marked as initialized")
            return True
        else:
            print_warning(f"Could not mark instance '{name}' as initialized")
            return False

    except Exception as e:
        print_warning(f"Could not mark instance as initialized: {e}")
        return False


def create_config_yaml(api_key: str, ports: dict, mounts: list, backup_cron: str, backup_dir: str, backup_retention: int, max_reflexion_iterations: int, instance_name: str = "primary"):
    """Create all configuration files in OS-standard system directory.

    Uses the new multi-instance configuration structure where each instance
    has its own complete configuration under the 'instances' section.
    """
    print_header("STEP 12: Creating Configuration Files")

    import platformdirs
    import yaml

    # Get OS-appropriate config directory (Windows, macOS, Linux compatible)
    config_dir = Path(platformdirs.user_config_dir('rag-memory', appauthor=False))
    config_dir.mkdir(parents=True, exist_ok=True)

    project_root = Path(__file__).parent.parent
    config_path = config_dir / 'config.yaml'

    try:
        # Build instance configuration
        database_url = f"postgresql://raguser:ragpassword@localhost:{ports['postgres']}/rag_memory"
        neo4j_uri = f"bolt://localhost:{ports['neo4j_bolt']}"

        instance_config = {
            'openai_api_key': api_key,
            'database_url': database_url,
            'neo4j_uri': neo4j_uri,
            'neo4j_http_port': ports['neo4j_http'],
            'neo4j_user': 'neo4j',
            'neo4j_password': 'graphiti-password',
            'mcp_sse_port': ports['mcp'],
            'backup_cron_expression': backup_cron,
            'backup_archive_path': f"./backups/{instance_name}",
            'backup_retention_days': backup_retention,
            'max_reflexion_iterations': max_reflexion_iterations,
            'mounts': mounts if mounts else [],
        }

        # Load existing config or create new
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f) or {}
        else:
            config = {}

        # Ensure instances section exists
        if 'instances' not in config:
            config['instances'] = {}

        # Add/update this instance
        config['instances'][instance_name] = instance_config

        # Remove legacy 'server' section if present (migration)
        if 'server' in config:
            del config['server']
        if 'mounts' in config and 'instances' in config:
            del config['mounts']

        # Write config with header comment
        config_header = """# RAG Memory Configuration
# =============================================================================
# Multi-instance configuration file. Each instance has its own complete
# configuration including API keys, database connections, mounts, and settings.
#
# Structure:
#   instances:
#     instance-name:
#       openai_api_key: "sk-..."
#       database_url: "postgresql://..."
#       neo4j_uri: "bolt://..."
#       mounts:
#         - path: /path/to/directory
#           read_only: true
#       ... other settings ...
# =============================================================================

"""
        with open(config_path, 'w') as f:
            f.write(config_header)
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        # Set restrictive permissions
        try:
            if os.name != 'nt':
                os.chmod(config_path, 0o600)
        except Exception:
            pass

        print_success(f"Configuration created: {config_path}")

        # 2. Create .env file for docker-compose
        # Create in BOTH locations for compatibility
        repo_env_path = project_root / 'deploy' / 'docker' / 'compose' / '.env'
        system_env_path = config_dir / '.env'
        env_content = f"""# Docker Compose Environment Variables
# Generated by setup.py

# Configuration directory
RAG_CONFIG_DIR={config_dir}

# HOST ports (left side of docker-compose port mappings)
# Can be changed if there are port conflicts
PROD_POSTGRES_PORT={ports['postgres']}
PROD_NEO4J_BOLT_PORT={ports['neo4j_bolt']}
PROD_NEO4J_HTTP_PORT={ports['neo4j_http']}
MCP_SSE_PORT={ports['mcp']}

# Database credentials (used by containers)
# Can be changed for security - update in both .env and config.yaml
POSTGRES_USER=raguser
POSTGRES_PASSWORD=ragpassword
POSTGRES_DB=rag_memory
NEO4J_USER=neo4j
NEO4J_PASSWORD=graphiti-password

# Backup configuration
BACKUP_CRON_EXPRESSION={backup_cron}
BACKUP_ARCHIVE_PATH={backup_dir}
BACKUP_RETENTION_DAYS={backup_retention}
"""
        # Write to both locations
        with open(repo_env_path, 'w') as f:
            f.write(env_content)
        print_success(f"Environment file created: {repo_env_path}")

        with open(system_env_path, 'w') as f:
            f.write(env_content)
        print_success(f"Environment file copied to system location: {system_env_path}")

        # 3. Generate docker-compose.yml from template with user mounts
        template_path = project_root / 'deploy' / 'docker' / 'compose' / 'docker-compose.template.yml'

        # Create docker-compose.yml in BOTH locations for compatibility
        # 1. In repo location for immediate use by setup.py
        repo_compose_path = project_root / 'deploy' / 'docker' / 'compose' / 'docker-compose.yml'
        # 2. In system location for CLI commands
        system_compose_path = config_dir / 'docker-compose.yml'

        with open(template_path, 'r') as f:
            compose_content = f.read()

        # Prepare mount lines
        mount_lines = ""
        if mounts:
            for mount in mounts:
                mount_path = mount['path']
                # Convert path to Docker-compatible format (handles Windows paths)
                docker_path = convert_path_for_docker(mount_path)
                mount_lines += f"      - {docker_path}:{docker_path}:ro\n"

        # Replace placeholder with actual mounts
        if mount_lines:
            # Replace the placeholder line with actual mounts
            compose_content = compose_content.replace(
                "      # USER_MOUNTS_PLACEHOLDER - Setup script will insert user directory mounts here",
                "      # User directory mounts (read-only)\n" + mount_lines.rstrip()
            )
        else:
            # Just remove the placeholder if no mounts
            compose_content = compose_content.replace(
                "      # USER_MOUNTS_PLACEHOLDER - Setup script will insert user directory mounts here\n",
                ""
            )

        # Inject backup destination mount
        # Convert path to Docker-compatible format (handles Windows paths)
        docker_backup_dir = convert_path_for_docker(backup_dir)
        backup_mount_line = f"      - {docker_backup_dir}:/archive\n"
        compose_content = compose_content.replace(
            "      # BACKUP_MOUNT_PLACEHOLDER - Setup script will insert backup destination mount here\n",
            backup_mount_line
        )

        # Write to repo location (keep ../init.sql path and build context)
        with open(repo_compose_path, 'w') as f:
            f.write(compose_content)
        print_success(f"Docker Compose configuration created: {repo_compose_path}")

        # For system location:
        # 1. Fix init.sql path to be relative to system directory
        # 2. Remove build section from rag-mcp-local (image is pre-built during setup)
        system_compose_content = compose_content.replace(
            "- ../init.sql:/docker-entrypoint-initdb.d/01-init.sql",
            "- ./init.sql:/docker-entrypoint-initdb.d/01-init.sql"
        )

        # Remove build section from rag-mcp-local service
        # The image will be pre-built during setup, so system compose doesn't need build context
        import re
        # Template format (lines 70-73):
        #     image: rag-memory-rag-mcp-local:latest
        #     build:
        #       context: ../../../
        #       dockerfile: deploy/docker/Dockerfile
        # Remove the build, context, and dockerfile lines, keep image line
        system_compose_content = re.sub(
            r'    build:\n      context: \.\./\.\./\.\./\n      dockerfile: deploy/docker/Dockerfile\n',
            '',
            system_compose_content
        )

        with open(system_compose_path, 'w') as f:
            f.write(system_compose_content)
        print_success(f"Docker Compose copied to system location: {system_compose_path}")

        # 4. Copy init.sql to system location
        init_sql_source = project_root / 'deploy' / 'docker' / 'init.sql'
        init_sql_dest = config_dir / 'init.sql'
        if init_sql_source.exists():
            with open(init_sql_source, 'r') as f:
                init_content = f.read()
            with open(init_sql_dest, 'w') as f:
                f.write(init_content)
            print_success(f"init.sql copied to system location: {init_sql_dest}")

        # 5. Copy docker-compose.instance.yml for multi-instance support
        instance_template_source = project_root / 'deploy' / 'docker' / 'compose' / 'docker-compose.instance.yml'
        instance_template_dest = config_dir / 'docker-compose.instance.yml'
        if instance_template_source.exists():
            with open(instance_template_source, 'r') as f:
                instance_template_content = f.read()

            # Fix init.sql path for system location
            instance_template_content = instance_template_content.replace(
                "- ../init.sql:/docker-entrypoint-initdb.d/01-init.sql",
                "- ./init.sql:/docker-entrypoint-initdb.d/01-init.sql"
            )

            # Collect ALL unique mounts from ALL instances in config
            # This ensures all instances can access their configured directories
            all_mount_paths = set()
            for inst_name, inst_config in config.get('instances', {}).items():
                for mount in inst_config.get('mounts', []):
                    mount_path = mount.get('path')
                    if mount_path:
                        all_mount_paths.add(mount_path)

            # Inject all unique mounts into docker-compose
            if all_mount_paths:
                mount_lines = ""
                for mount_path in sorted(all_mount_paths):
                    docker_path = convert_path_for_docker(mount_path)
                    mount_lines += f"      - {docker_path}:{docker_path}:ro\n"
                instance_template_content = instance_template_content.replace(
                    "      # USER_MOUNTS_PLACEHOLDER - Setup script will insert user directory mounts here",
                    "      # User directory mounts (read-only)\n" + mount_lines.rstrip()
                )
            else:
                instance_template_content = instance_template_content.replace(
                    "      # USER_MOUNTS_PLACEHOLDER - Setup script will insert user directory mounts here\n",
                    ""
                )

            with open(instance_template_dest, 'w') as f:
                f.write(instance_template_content)
            print_success(f"Instance template copied to system location: {instance_template_dest}")

        # 6. Create backups directory for the instance
        backup_instance_dir = config_dir / 'backups' / instance_name
        backup_instance_dir.mkdir(parents=True, exist_ok=True)
        print_success(f"Backup directory created: {backup_instance_dir}")

        return True, config_dir
    except Exception as e:
        print_error(f"Failed to create configuration: {e}")
        return False, None


def build_and_start_containers(config_dir: Path, ports: dict = None, instance_name: str = "primary") -> bool:
    """Build and start Docker containers for an instance.

    Args:
        config_dir: Path to system config directory
        ports: Port configuration dict
        instance_name: Name of the instance (used for project name)
    """
    print_header("STEP 13: Building and Starting Containers")

    project_root = Path(__file__).parent.parent
    repo_compose_file = project_root / 'deploy' / 'docker' / 'compose' / 'docker-compose.yml'
    # Use instance template for multi-instance support
    instance_compose_file = config_dir / 'docker-compose.instance.yml'
    # Fall back to legacy compose file if instance template doesn't exist
    system_compose_file = instance_compose_file if instance_compose_file.exists() else config_dir / 'docker-compose.yml'

    try:
        # Detect which docker compose command to use (cross-platform)
        docker_compose_cmd = get_docker_compose_command()

        # Step 1: Build the MCP image using repo docker-compose.yml (needs build context)
        # Force fresh build with --no-cache to always pick up latest code changes
        print_info("Building MCP server image (forcing fresh build)...")
        code, _, stderr = run_command(
            docker_compose_cmd + ["-f", str(repo_compose_file),
                                  "build", "--no-cache", "rag-mcp-local"],
            timeout=600
        )

        if code != 0:
            print_error(f"Failed to build MCP image: {stderr}")
            return False

        print_success("MCP image built (fresh build)")

        # Step 1.5: Verify ports are STILL available right before starting containers
        # This prevents race conditions where ports are grabbed during image build
        print()
        rechecked_ports = find_available_ports(recheck=True)
        if not rechecked_ports:
            print_error("Port verification failed - cannot start containers")
            return False

        # Check if any ports changed since initial selection
        if ports and rechecked_ports != ports:
            print_warning("Port availability changed since initial check!")
            print_info("Original ports selected:")
            for service, port in ports.items():
                print(f"  {service}: {port}")
            print_info("New ports available:")
            for service, port in rechecked_ports.items():
                print(f"  {service}: {port}")
            print()
            response = input(f"{Colors.YELLOW}Continue with new ports? (yes/no): {Colors.RESET}").strip().lower()
            if response != "yes":
                print_info("Setup cancelled. Kill processes using the original ports and re-run setup.")
                return False
            # Update ports reference for later use
            ports.clear()
            ports.update(rechecked_ports)

        print()

        # Step 2: Start containers using instance compose template
        # Use project name for isolation (rag-memory-{instance_name})
        # Use --force-recreate to ensure fresh containers with latest code
        print_info(f"Starting containers for instance '{instance_name}' (forcing recreate)...")

        # Build environment for docker-compose
        compose_env = os.environ.copy()
        compose_env.update({
            'INSTANCE_NAME': instance_name,
            'POSTGRES_PORT': str(ports['postgres']),
            'NEO4J_BOLT_PORT': str(ports['neo4j_bolt']),
            'NEO4J_HTTP_PORT': str(ports['neo4j_http']),
            'MCP_PORT': str(ports['mcp']),
            'RAG_CONFIG_DIR': str(config_dir),
            'BACKUP_ARCHIVE_PATH': str(config_dir / 'backups' / instance_name),
        })

        code, stdout, stderr = run_command(
            docker_compose_cmd + [
                "-p", f"rag-memory-{instance_name}",
                "-f", str(system_compose_file),
                "up", "-d", "--force-recreate"
            ],
            timeout=None,
            env=compose_env
        )

        if code != 0:
            print_error(f"Failed to start containers: {stderr}")

            # Detect port conflict errors and provide helpful guidance
            if "port is already allocated" in stderr.lower() or "bind" in stderr.lower():
                print()
                print_error("PORT CONFLICT DETECTED")
                print_info("Another process is using one of the required ports.")
                print_info("")
                print_info("Find what's using your ports:")
                print_info(f"  Mac/Linux:  lsof -i :18000  (or other port number)")
                print_info(f"  Windows:    netstat -ano | findstr :18000")
                print_info("")
                print_info("Then either:")
                print_info("  1. Kill the process using that port")
                print_info("  2. Re-run this setup script to find different ports")

            return False

        print_success("Containers started (fresh recreate)")
        return True

    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False


def wait_for_health_checks(ports: dict, config_dir: Path, instance_name: str = "primary", timeout_seconds: int = 300, check_interval: int = 30) -> bool:
    """Wait for all services to be healthy with status updates.

    Args:
        ports: Port configuration dict
        config_dir: Path to config directory
        instance_name: Name of the instance (for container names)
        timeout_seconds: Maximum time to wait
        check_interval: Seconds between health checks
    """
    print_header("STEP 14: Waiting for Services to Be Ready")

    # Build container names using instance name
    pg_container = f"rag-memory-postgres-{instance_name}"
    neo4j_container = f"rag-memory-neo4j-{instance_name}"
    mcp_container = f"rag-memory-mcp-{instance_name}"

    print_info(f"Checking services every {check_interval} seconds (timeout: {timeout_seconds}s)")
    print_info(f"Instance: {instance_name}")

    start_time = time.time()
    checks_performed = 0

    while time.time() - start_time < timeout_seconds:
        elapsed = int(time.time() - start_time)
        checks_performed += 1

        print_info(f"[{elapsed}s] Health check #{checks_performed}...")

        # Check PostgreSQL health status AND test connection
        pg_code, pg_stdout, _ = run_command([
            "docker", "ps", "--filter", f"name={pg_container}",
            "--format", "{{.Status}}"
        ])
        pg_container_ready = pg_code == 0 and "healthy" in pg_stdout

        # Test actual PostgreSQL connection
        pg_connectable = False
        if pg_container_ready:
            test_code, _, _ = run_command([
                "docker", "exec", pg_container,
                "psql", "-U", "raguser", "-d", "rag_memory", "-c", "SELECT 1"
            ])
            pg_connectable = test_code == 0

        # Check Neo4j health status AND test connection
        neo4j_code, neo4j_stdout, _ = run_command([
            "docker", "ps", "--filter", f"name={neo4j_container}",
            "--format", "{{.Status}}"
        ])
        neo4j_container_ready = neo4j_code == 0 and "healthy" in neo4j_stdout

        # Test actual Neo4j connection
        neo4j_connectable = False
        if neo4j_container_ready:
            test_code, _, _ = run_command([
                "docker", "exec", neo4j_container,
                "cypher-shell", "-u", "neo4j", "-p", "graphiti-password",
                "RETURN 1"
            ])
            neo4j_connectable = test_code == 0

        # Check MCP running status AND test SSE endpoint
        mcp_code, mcp_stdout, _ = run_command([
            "docker", "ps", "--filter", f"name={mcp_container}",
            "--format", "{{.Status}}"
        ])
        mcp_container_running = mcp_code == 0 and "Up" in mcp_stdout

        # Test actual MCP SSE endpoint (using curl to test if port is open)
        mcp_responding = False
        if mcp_container_running:
            import socket
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex(('127.0.0.1', ports['mcp']))
                sock.close()
                mcp_responding = result == 0
            except Exception:
                mcp_responding = False

        if pg_connectable and neo4j_connectable and mcp_responding:
            print_success("PostgreSQL is ready and accepting connections")
            print_success("Neo4j is ready and accepting connections")
            print_success("MCP server is running and responding on port " + str(ports['mcp']))
            return True

        if not pg_connectable:
            if not pg_container_ready:
                print_info("  - PostgreSQL: container starting...")
            else:
                print_warning("  - PostgreSQL: container healthy but not accepting connections")
        else:
            print_success("  - PostgreSQL: ready")

        if not neo4j_connectable:
            if not neo4j_container_ready:
                print_info("  - Neo4j: container starting...")
            else:
                print_warning("  - Neo4j: container healthy but not accepting connections")
        else:
            print_success("  - Neo4j: ready")

        if not mcp_responding:
            if not mcp_container_running:
                print_info("  - MCP: container starting...")
            else:
                print_warning(f"  - MCP: container running but not responding on port {ports['mcp']}")
                # Check logs for errors
                log_code, log_output, _ = run_command([
                    "docker", "logs", "--tail", "5", mcp_container
                ])
                if log_code == 0 and "error" in log_output.lower():
                    print_error("  - MCP logs show errors (last 5 lines):")
                    for line in log_output.split('\n')[-5:]:
                        if line.strip():
                            print(f"    {line}")
        else:
            print_success("  - MCP: ready")

        if time.time() - start_time < timeout_seconds:
            time.sleep(check_interval)

    print_error(f"Services did not become ready within {timeout_seconds} seconds")
    print_error("Check docker logs for more information:")
    print_info(f"  docker logs {pg_container}")
    print_info(f"  docker logs {neo4j_container}")
    print_info(f"  docker logs {mcp_container}")
    return False


def validate_schemas(ports: dict, instance_name: str = "primary") -> bool:
    """Validate that database schemas were created correctly"""
    print_header("STEP 15: Validating Database Schemas")

    pg_container = f"rag-memory-postgres-{instance_name}"
    neo4j_container = f"rag-memory-neo4j-{instance_name}"

    # Check PostgreSQL schema
    print_info("Checking PostgreSQL schema...")
    code, stdout, _ = run_command([
        "docker", "exec", pg_container,
        "psql", "-U", "raguser", "-d", "rag_memory", "-c",
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public'"
    ])

    if code == 0 and "4" in stdout:
        print_success("PostgreSQL schema validated (4 tables found)")
    else:
        print_error("PostgreSQL schema validation failed")
        return False

    # Check Neo4j
    print_info("Checking Neo4j...")
    code, _, _ = run_command([
        "docker", "exec", neo4j_container,
        "cypher-shell", "-u", "neo4j", "-p", "graphiti-password",
        "MATCH (n) RETURN COUNT(n)"
    ])

    if code == 0:
        print_success("Neo4j is accessible")
    else:
        print_warning("Could not verify Neo4j schema (may still be initializing)")

    return True


async def init_neo4j_indices(ports: dict, api_key: str) -> bool:
    """Initialize Neo4j Graphiti indices and constraints.

    This must be called AFTER Neo4j container is verified healthy.
    Creates the required indices and constraints for Graphiti to function.

    Note: Graphiti requires OPENAI_API_KEY environment variable even though
    build_indices_and_constraints() doesn't call LLM (it creates clients internally).
    """
    print_header("STEP 16: Initializing Neo4j Indices")

    try:
        from graphiti_core import Graphiti
        import os

        neo4j_uri = f"bolt://localhost:{ports['neo4j_bolt']}"
        neo4j_user = "neo4j"
        neo4j_password = "graphiti-password"

        print_info("Connecting to Neo4j...")

        # Set OPENAI_API_KEY in environment - Graphiti requires it even for schema operations
        os.environ['OPENAI_API_KEY'] = api_key

        graphiti = Graphiti(neo4j_uri, neo4j_user, neo4j_password)

        print_info("Creating indices and constraints (this is idempotent)...")
        await graphiti.build_indices_and_constraints(delete_existing=False)

        print_success("✅ Neo4j indices initialized successfully")
        await graphiti.close()
        return True

    except Exception as e:
        print_warning(f"Failed to initialize Neo4j indices: {e}")
        print_info("You can run 'rag init' manually after setup completes")
        return False


def create_neo4j_vector_indices(ports: dict, instance_name: str = "primary") -> bool:
    """Create Neo4j vector indices for optimal embedding search performance.

    Graphiti's build_indices_and_constraints() creates range and fulltext indices,
    but does NOT create vector indices. Without vector indices, Neo4j logs warnings
    during ingestion when searching for similar entities/facts.

    This function creates vector indices for:
    - Entity.name_embedding (1024 dimensions, cosine similarity)
    - RELATES_TO.fact_embedding (1024 dimensions, cosine similarity)

    These are used during ingestion when Graphiti searches for duplicate/similar
    entities and relationships. Vector indices dramatically improve performance.

    This must be called AFTER init_neo4j_indices() completes.
    """
    print_header("STEP 14.5: Creating Neo4j Vector Indices")

    neo4j_container = f"rag-memory-neo4j-{instance_name}"

    print_info("Creating vector indices for embedding similarity search...")
    print_info("This eliminates Neo4j warnings during ingestion and improves performance")

    try:
        # Create Entity.name_embedding vector index
        code, stdout, stderr = run_command([
            "docker", "exec", neo4j_container,
            "cypher-shell", "-u", "neo4j", "-p", "graphiti-password",
            """CREATE VECTOR INDEX entity_name_embedding IF NOT EXISTS
            FOR (n:Entity)
            ON n.name_embedding
            OPTIONS {indexConfig: {
              `vector.dimensions`: 1024,
              `vector.similarity_function`: 'cosine'
            }}"""
        ])

        if code != 0:
            print_warning(f"Failed to create Entity.name_embedding index: {stderr}")
            return False

        print_success("Entity.name_embedding vector index created")

        # Create RELATES_TO.fact_embedding vector index
        code, stdout, stderr = run_command([
            "docker", "exec", neo4j_container,
            "cypher-shell", "-u", "neo4j", "-p", "graphiti-password",
            """CREATE VECTOR INDEX edge_fact_embedding IF NOT EXISTS
            FOR ()-[r:RELATES_TO]-()
            ON r.fact_embedding
            OPTIONS {indexConfig: {
              `vector.dimensions`: 1024,
              `vector.similarity_function`: 'cosine'
            }}"""
        ])

        if code != 0:
            print_warning(f"Failed to create RELATES_TO.fact_embedding index: {stderr}")
            return False

        print_success("RELATES_TO.fact_embedding vector index created")

        # Verify both indices exist
        code, stdout, stderr = run_command([
            "docker", "exec", neo4j_container,
            "cypher-shell", "-u", "neo4j", "-p", "graphiti-password",
            "SHOW INDEXES WHERE type = 'VECTOR'"
        ])

        if code == 0 and "entity_name_embedding" in stdout and "edge_fact_embedding" in stdout:
            print_success("Vector indices verified (2 VECTOR indices found)")
            return True
        else:
            print_warning("Could not verify vector indices (may still be building)")
            return True  # Don't fail setup, indices may be building

    except Exception as e:
        print_warning(f"Unexpected error creating vector indices: {e}")
        print_info("Vector indices are optional - system will work without them")
        return True  # Don't fail setup for optional optimization


def print_final_summary(ports: dict, config_dir: Path, instance_name: str = "primary"):
    """Print final summary with all connection info and management commands"""
    print_header("Setup Complete!")

    print(f"{Colors.GREEN}{Colors.BOLD}RAG Memory is now running on your machine!{Colors.RESET}")
    print(f"Instance '{instance_name}' is ready with:")
    print(f"  • Semantic search (PostgreSQL + pgvector)")
    print(f"  • Entity relationships (Neo4j)")
    print(f"  • CLI tool and MCP server for AI agents")
    print()

    # Configuration location
    print(f"{Colors.BOLD}Configuration Location{Colors.RESET}")
    print(f"  {Colors.CYAN}{config_dir}{Colors.RESET}")
    print(f"  Contains: config.yaml, docker-compose.instance.yml")
    print()

    # Connection information
    print(f"{Colors.BOLD}Service URLs{Colors.RESET}")
    print(f"  PostgreSQL: postgresql://raguser:ragpassword@localhost:{ports['postgres']}/rag_memory")
    print(f"  Neo4j Browser: http://localhost:{ports['neo4j_http']} (user: neo4j, pass: graphiti-password)")

    # Neo4j Bolt port warning if not using default port
    if ports['neo4j_bolt'] != 7687:
        print(f"    {Colors.YELLOW}Note: When Neo4j Browser opens, change connection URL from:{Colors.RESET}")
        print(f"    {Colors.YELLOW}  Default: bolt://localhost:7687{Colors.RESET}")
        print(f"    {Colors.YELLOW}  To:      {Colors.CYAN}bolt://localhost:{ports['neo4j_bolt']}{Colors.RESET}")

    print(f"  MCP Server: http://localhost:{ports['mcp']}/sse")
    print()

    # MCP Client Configuration
    print(f"{Colors.BOLD}Connect to AI Assistants{Colors.RESET}")
    print(f"\n  For Claude Code:")
    print(f"    {Colors.CYAN}claude mcp add --transport sse --scope user rag-memory http://localhost:{ports['mcp']}/sse{Colors.RESET}")
    print(f"    Then restart Claude Code and verify with: {Colors.CYAN}claude mcp list{Colors.RESET}")

    print(f"\n  For Claude Desktop:")
    print(f"    Add this entry to the 'mcpServers' section of claude_desktop_config.json:")
    print(f"""    {Colors.CYAN}"rag-memory": {{
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "http://localhost:{ports['mcp']}/sse",
        "--allow-http"
      ]
    }}{Colors.RESET}""")
    print()

    # Instance management
    print(f"{Colors.BOLD}Managing Instances{Colors.RESET}")
    print(f"  {Colors.CYAN}rag instance list{Colors.RESET} - List all instances")
    print(f"  {Colors.CYAN}rag instance status {instance_name}{Colors.RESET} - Check instance health")
    print(f"  {Colors.CYAN}rag instance stop {instance_name}{Colors.RESET} - Stop this instance")
    print(f"  {Colors.CYAN}rag instance start {instance_name}{Colors.RESET} - Start this instance")
    print(f"  {Colors.CYAN}rag instance logs {instance_name}{Colors.RESET} - View instance logs")
    print()
    print(f"  Create additional instances:")
    print(f"    {Colors.CYAN}rag instance start research{Colors.RESET} - Creates new 'research' instance")
    print()

    # CLI commands
    print(f"{Colors.BOLD}Try These Commands{Colors.RESET}")
    print(f"  {Colors.CYAN}rag status{Colors.RESET} - Check database connections")
    print(f"  {Colors.CYAN}rag collection create my-notes --description \"My personal notes\"{Colors.RESET}")
    print(f"  {Colors.CYAN}rag ingest text \"Your first document\" --collection my-notes{Colors.RESET}")
    print(f"  {Colors.CYAN}rag search \"document\" --collection my-notes{Colors.RESET}")
    print()

    # Next steps
    print(f"{Colors.BOLD}Next Steps{Colors.RESET}")
    print(f"  • For Claude Code: Run {Colors.CYAN}/getting-started{Colors.RESET} in Claude Code")
    print(f"  • For CLI help: Run {Colors.CYAN}rag --help{Colors.RESET}")
    print(f"  • Documentation: {Colors.CYAN}.reference/README.md{Colors.RESET}")
    print()

    print(f"Start using it now - try the commands above!")
    print()


def install_cli_tool() -> bool:
    """Install the RAG Memory CLI tool using uv tool install"""
    print_header("STEP 17: Installing CLI Tool")

    print_info("Installing rag-memory CLI tool globally...")
    project_root = Path(__file__).parent.parent

    # Run uv tool install from the project root
    code, _, stderr = run_command(
        ["uv", "tool", "install", str(project_root)],
        timeout=300
    )

    if code != 0:
        print_error(f"Failed to install CLI tool: {stderr}")
        return False

    print_success("CLI tool installed successfully")
    print_info("You can now run 'rag' commands from anywhere")
    return True


def main():
    """Main setup flow"""
    print(f"\n{Colors.BOLD}{Colors.GREEN}RAG Memory Setup Script{Colors.RESET}")
    print(f"Cross-platform local development environment setup\n")

    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    # Ensure project root is in sys.path for src imports
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    print_info(f"Working directory: {project_root}")

    # Step 0: Check Python dependencies (MUST run before anything else)
    if not check_python_dependencies():
        sys.exit(1)

    # Step 1: Check Docker
    if not check_docker_installed():
        sys.exit(1)

    # Step 2: Check Docker running
    if not check_docker_running():
        sys.exit(1)

    # Step 3: Check existing containers
    if check_existing_containers():
        sys.exit(0)

    # Step 4: Check if configuration already exists
    # Offer to add a new instance or reconfigure
    import platformdirs
    import yaml as yaml_module
    config_dir = Path(platformdirs.user_config_dir('rag-memory', appauthor=False))
    config_path = config_dir / 'config.yaml'
    adding_instance = False

    if config_path.exists():
        # Load existing config to see what instances exist
        with open(config_path, 'r') as f:
            existing_config = yaml_module.safe_load(f) or {}

        existing_instances = list(existing_config.get('instances', {}).keys())

        if existing_instances:
            print_warning("Configuration file already exists with instances:")
            for inst in existing_instances:
                print(f"  - {inst}")
            print()
            print_info("Options:")
            print("  1. Add a new instance (keeps existing instances)")
            print("  2. Start fresh (removes all existing configuration)")
            print("  3. Cancel")
            print()
            response = input(f"{Colors.YELLOW}Choose option (1/2/3): {Colors.RESET}").strip()

            if response == "1":
                adding_instance = True
                print_info("Adding a new instance...")
            elif response == "2":
                print_warning("This will remove ALL existing instances and configuration!")
                confirm = input(f"{Colors.YELLOW}Type 'yes' to confirm: {Colors.RESET}").strip().lower()
                if confirm != "yes":
                    print_info("Setup cancelled")
                    sys.exit(0)
                # Will proceed to create fresh config
            else:
                print_info("Setup cancelled")
                sys.exit(0)
        else:
            # Legacy config without instances section
            print_warning("Legacy configuration found (will be migrated)")
            response = input(f"\n{Colors.YELLOW}Migrate to new format? (yes/no): {Colors.RESET}").strip().lower()
            if response != "yes":
                print_info("Setup cancelled")
                sys.exit(0)

    # Step 5: Get API key
    api_key = prompt_for_api_key()

    # Step 6: Find ports
    ports = find_available_ports()
    if not ports:
        sys.exit(1)

    # Confirm port selection with user
    print()
    print_info("These ports will be used for your local services:")
    print(f"  PostgreSQL:  localhost:{ports['postgres']}")
    print(f"  Neo4j HTTP:  localhost:{ports['neo4j_http']}")
    print(f"  Neo4j Bolt:  localhost:{ports['neo4j_bolt']}")
    print(f"  MCP Server:  localhost:{ports['mcp']}")
    print()
    print_info("Ports will be verified again right before starting containers.")
    print()

    # Step 7: Configure directory mounts
    mounts = configure_directory_mounts()
    if mounts is None:
        sys.exit(1)

    # Step 8: Configure backup schedule
    backup_cron = prompt_for_backup_schedule()

    # Step 9: Configure backup location
    backup_dir = prompt_for_backup_location()

    # Step 10: Configure backup retention
    backup_retention = prompt_for_backup_retention()

    # Step 11: Configure entity extraction quality
    max_reflexion_iterations = prompt_for_entity_extraction_quality()

    # Step 12: Get instance name
    instance_name = prompt_for_instance_name()

    # Step 13: Create YAML configuration from template
    success, config_dir = create_config_yaml(
        api_key, ports, mounts, backup_cron, backup_dir,
        backup_retention, max_reflexion_iterations, instance_name
    )
    if not success:
        sys.exit(1)

    # Step 14: Register instance in registry
    register_instance(instance_name, ports, config_dir)

    # Step 15: Build and start
    if not build_and_start_containers(config_dir, ports, instance_name):
        sys.exit(1)

    # Step 16: Wait for health
    if not wait_for_health_checks(ports, config_dir, instance_name):
        print_error("Setup completed but services are not responding")
        print_info(f"Try: docker logs rag-memory-postgres-{instance_name}")
        sys.exit(1)

    # Step 17: Initialize Neo4j indices
    # Run this after health checks confirm Neo4j is up
    if not asyncio.run(init_neo4j_indices(ports, api_key)):
        print_error("Failed to initialize Neo4j indices - this is REQUIRED for the system to work")
        print_info("Neo4j indices are mandatory. Setup cannot continue.")
        sys.exit(1)

    # Step 18: Create Neo4j vector indices for performance
    # Run this after Graphiti indices are created
    if not create_neo4j_vector_indices(ports, instance_name):
        print_warning("Failed to create vector indices - performance may be degraded")
        print_info("Vector indices are optional but recommended for best performance")

    # Step 19: Mark instance as initialized
    mark_instance_initialized(instance_name, config_dir)

    # Step 20: Install CLI tool
    if not install_cli_tool():
        print_warning("Failed to install CLI tool, but setup is otherwise complete")

    # Step 21: Validate schemas
    if not validate_schemas(ports, instance_name):
        print_warning("Schema validation had issues, but setup may still work")

    # Step 22: Print final summary
    print_final_summary(ports, config_dir, instance_name)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_error("\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
