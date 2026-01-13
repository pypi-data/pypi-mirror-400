#!/usr/bin/env python3
"""
Update MCP Server Container

Cross-platform script to rebuild and restart only the MCP server container
without affecting PostgreSQL or Neo4j databases.

Usage:
    python scripts/update_mcp.py                     # Update default/first instance
    python scripts/update_mcp.py --instance primary  # Update specific instance
    python scripts/update_mcp.py --all               # Update ALL registered instances
    python scripts/update_mcp.py --list              # List available instances

Requirements:
    - MCP container must have been deployed via setup.py
    - Docker must be running
    - Run from the rag-memory repository root
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path
from typing import Tuple, Optional


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
    print(f"{Colors.GREEN}  {text}{Colors.RESET}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}  {text}{Colors.RESET}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}  {text}{Colors.RESET}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.BLUE}  {text}{Colors.RESET}")


def run_command(cmd: list, check: bool = True, timeout: int = None, env: dict = None) -> Tuple[int, str, str]:
    """Run shell command and return exit code, stdout, stderr"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env
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


def check_docker_running() -> bool:
    """Check if Docker daemon is running"""
    print_info("Checking Docker daemon...")
    code, _, _ = run_command(["docker", "ps"])

    if code == 0:
        print_success("Docker daemon is running")
        return True

    print_error("Docker daemon is not running")
    print_info("Start Docker Desktop and try again")
    return False


def get_system_config_dir() -> Optional[Path]:
    """Get OS-appropriate system configuration directory"""
    try:
        import platformdirs
        config_dir = Path(platformdirs.user_config_dir('rag-memory', appauthor=False))
        return config_dir
    except ImportError:
        print_error("platformdirs package not found")
        print_info("Run: pip install platformdirs")
        return None


def get_instance_registry():
    """Get the instance registry"""
    try:
        # Ensure project root is in sys.path for src imports
        project_root = str(Path(__file__).parent.parent)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        from src.core.instance_registry import get_instance_registry
        return get_instance_registry()
    except ImportError:
        return None


def list_instances() -> list:
    """List all registered instances"""
    registry = get_instance_registry()
    if registry:
        return registry.list_instances()
    return []


def get_default_instance() -> Optional[str]:
    """Get the first/default instance name"""
    instances = list_instances()
    if instances:
        return instances[0]['name']
    return None


def get_instance_info(instance_name: str) -> Optional[dict]:
    """Get instance information from registry"""
    registry = get_instance_registry()
    if registry:
        return registry.get_instance(instance_name)
    return None


def check_container_exists(container_name: str) -> Tuple[bool, bool]:
    """Check if container exists and if it's running

    Returns:
        (exists, is_running)
    """
    # Check if container exists (running or stopped)
    code, stdout, _ = run_command(["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.Names}}"])
    exists = container_name in stdout

    if not exists:
        return False, False

    # Check if it's running
    code, stdout, _ = run_command(["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Names}}"])
    is_running = container_name in stdout

    return exists, is_running


def check_mcp_deployment(instance_name: str) -> Tuple[bool, Path, dict]:
    """Check if MCP has been deployed for the specified instance

    Returns:
        (is_deployed, system_compose_path, instance_info)
    """
    print_info(f"Checking MCP deployment status for instance '{instance_name}'...")

    # Get system config directory
    config_dir = get_system_config_dir()
    if not config_dir:
        return False, None, None

    # Check if system docker-compose.instance.yml exists
    system_compose_path = config_dir / 'docker-compose.instance.yml'
    if not system_compose_path.exists():
        # Fall back to legacy docker-compose.yml
        system_compose_path = config_dir / 'docker-compose.yml'
        if not system_compose_path.exists():
            print_error(f"Docker compose file not found at: {config_dir}")
            print_info("Run setup.py first to deploy the MCP server")
            return False, None, None

    # Get instance info from registry
    instance_info = get_instance_info(instance_name)
    if not instance_info:
        print_error(f"Instance '{instance_name}' not found in registry")
        instances = list_instances()
        if instances:
            print_info("Available instances:")
            for inst in instances:
                print(f"    - {inst['name']}")
        else:
            print_info("Run setup.py first to create an instance")
        return False, None, None

    # Check if MCP container exists
    container_name = f"rag-memory-mcp-{instance_name}"
    exists, is_running = check_container_exists(container_name)

    if not exists:
        print_warning(f"Container '{container_name}' does not exist")
        print_info(f"Run 'rag instance start {instance_name}' to create the MCP container")
        return False, None, None

    status = "running" if is_running else "stopped"
    print_success(f"MCP container exists and is {status}")

    return True, system_compose_path, instance_info


def rebuild_mcp_image() -> bool:
    """Rebuild the MCP Docker image from source code

    Returns:
        True if build succeeded
    """
    print_header("Step 1: Rebuilding MCP Image")

    docker_compose_cmd = get_docker_compose_command()
    project_root = Path(__file__).parent.parent
    # Use the main docker-compose.yml which has the build section
    repo_compose_path = project_root / 'deploy' / 'docker' / 'compose' / 'docker-compose.yml'

    if not repo_compose_path.exists():
        print_error(f"Docker compose file not found at: {repo_compose_path}")
        return False

    print_info("Building MCP server image from latest code...")
    print_info(f"Using: {repo_compose_path}")

    # Build the image using the repo compose file (rag-mcp-local service)
    code, stdout, stderr = run_command(
        docker_compose_cmd + ["-f", str(repo_compose_path), "build", "rag-mcp-local"],
        timeout=600
    )

    if code != 0:
        print_error(f"Failed to build MCP image: {stderr}")
        return False

    print_success("MCP image rebuilt successfully")
    return True


def restart_mcp_container(system_compose_path: Path, instance_name: str, instance_info: dict) -> bool:
    """Restart only the MCP container without affecting databases

    Args:
        system_compose_path: Path to system docker-compose.yml
        instance_name: Name of the instance
        instance_info: Instance configuration from registry

    Returns:
        True if restart succeeded
    """
    print_header("Step 2: Restarting MCP Container")

    docker_compose_cmd = get_docker_compose_command()
    config_dir = get_system_config_dir()

    print_info("Restarting MCP container (databases will NOT be affected)...")
    print_info(f"Using: {system_compose_path}")

    # Build environment for docker-compose
    ports = instance_info.get('ports', {})
    compose_env = os.environ.copy()
    compose_env.update({
        'INSTANCE_NAME': instance_name,
        'POSTGRES_PORT': str(ports.get('postgres', 54320)),
        'NEO4J_BOLT_PORT': str(ports.get('neo4j_bolt', 7687)),
        'NEO4J_HTTP_PORT': str(ports.get('neo4j_http', 7474)),
        'MCP_PORT': str(ports.get('mcp', 8000)),
        'RAG_CONFIG_DIR': str(config_dir),
        'BACKUP_ARCHIVE_PATH': str(instance_info.get('backup_dir', config_dir / 'backups')),
    })

    # Use --no-deps to prevent restarting postgres and neo4j
    # Use --force-recreate to ensure container picks up new image
    code, stdout, stderr = run_command(
        docker_compose_cmd + [
            "-p", f"rag-memory-{instance_name}",
            "-f", str(system_compose_path),
            "up", "-d", "--no-deps", "--force-recreate", "mcp"
        ],
        timeout=120,
        env=compose_env
    )

    if code != 0:
        print_error(f"Failed to restart MCP container: {stderr}")
        return False

    print_success("MCP container restarted with updated code")
    return True


def verify_mcp_health(instance_name: str, timeout_seconds: int = 60) -> bool:
    """Wait for MCP container to become healthy

    Args:
        instance_name: Name of the instance
        timeout_seconds: How long to wait for health check

    Returns:
        True if container became healthy
    """
    print_header("Step 3: Verifying MCP Health")

    import time

    container_name = f"rag-memory-mcp-{instance_name}"
    print_info(f"Waiting up to {timeout_seconds}s for MCP to become healthy...")

    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        code, stdout, _ = run_command(
            ["docker", "inspect", "--format", "{{.State.Health.Status}}", container_name]
        )

        if code == 0:
            health_status = stdout.strip()

            if health_status == "healthy":
                elapsed = int(time.time() - start_time)
                print_success(f"MCP container is healthy (took {elapsed}s)")
                return True

            print_info(f"Health status: {health_status}, waiting...")

        time.sleep(5)

    print_warning("Health check timeout - container may still be starting")
    print_info(f"Check logs with: docker logs {container_name}")
    return False


def print_instances():
    """Print list of available instances"""
    instances = list_instances()
    if not instances:
        print_info("No instances found. Run setup.py first.")
        return

    print(f"\n{Colors.BOLD}Available Instances:{Colors.RESET}")
    for inst in instances:
        name = inst['name']
        ports = inst.get('ports', {})
        print(f"  {Colors.CYAN}{name}{Colors.RESET}")
        print(f"    PostgreSQL: localhost:{ports.get('postgres', 'N/A')}")
        print(f"    Neo4j:      localhost:{ports.get('neo4j_bolt', 'N/A')}")
        print(f"    MCP:        localhost:{ports.get('mcp', 'N/A')}")
    print()


def update_all_instances():
    """Update MCP containers for ALL registered instances.

    Rebuilds the image once, then restarts containers for each instance.
    Continues with remaining instances even if one fails.
    """
    instances = list_instances()
    if not instances:
        print_error("No instances found. Run setup.py first.")
        sys.exit(1)

    instance_names = [inst['name'] for inst in instances]
    print_info(f"Found {len(instance_names)} instance(s): {', '.join(instance_names)}")

    # Step 1: Verify all instances have MCP deployed and collect their info
    print_header("Step 1: Verifying All Instances")
    deployments = {}  # name -> (compose_path, instance_info)

    for inst in instances:
        name = inst['name']
        is_deployed, system_compose_path, instance_info = check_mcp_deployment(name)
        if is_deployed:
            deployments[name] = (system_compose_path, instance_info)
            print_success(f"Instance '{name}' is ready for update")
        else:
            print_warning(f"Instance '{name}' skipped - not deployed or container missing")

    if not deployments:
        print_error("No instances available for update")
        sys.exit(1)

    print_info(f"{len(deployments)} instance(s) will be updated")

    # Step 2: Rebuild MCP image ONCE (shared across all instances)
    if not rebuild_mcp_image():
        sys.exit(1)

    # Step 3: Restart MCP container for each instance
    print_header(f"Step 3: Restarting MCP Containers ({len(deployments)} instances)")

    results = {}  # name -> success boolean
    for name, (compose_path, instance_info) in deployments.items():
        print(f"\n{Colors.BOLD}Updating instance: {name}{Colors.RESET}")

        if restart_mcp_container(compose_path, name, instance_info):
            results[name] = True
        else:
            results[name] = False
            print_error(f"Failed to restart MCP for instance '{name}'")

    # Step 4: Verify health for all successfully restarted instances
    print_header("Step 4: Verifying Health")

    health_results = {}
    for name, restart_success in results.items():
        if restart_success:
            health_results[name] = verify_mcp_health(name, timeout_seconds=60)
        else:
            health_results[name] = False

    # Final summary
    print_header("Update Complete - Summary")

    successful = [name for name, healthy in health_results.items() if healthy]
    failed = [name for name, healthy in health_results.items() if not healthy]
    skipped = [inst['name'] for inst in instances if inst['name'] not in deployments]

    if successful:
        print_success(f"Successfully updated: {', '.join(successful)}")
    if failed:
        print_warning(f"Failed or unhealthy: {', '.join(failed)}")
    if skipped:
        print_info(f"Skipped (not deployed): {', '.join(skipped)}")

    print()
    print_info("PostgreSQL and Neo4j containers were not affected")
    print()

    if failed:
        print_info("To investigate failures:")
        for name in failed:
            print(f"  {Colors.CYAN}docker logs rag-memory-mcp-{name}{Colors.RESET}")
        sys.exit(1)


def main():
    """Main update flow"""
    parser = argparse.ArgumentParser(
        description="Update MCP Server Container",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/update_mcp.py                     # Update default instance
  python scripts/update_mcp.py --instance primary  # Update specific instance
  python scripts/update_mcp.py --all               # Update ALL registered instances
  python scripts/update_mcp.py --list              # List available instances
"""
    )
    parser.add_argument(
        '--instance', '-i',
        help='Instance name to update (default: first registered instance)'
    )
    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='Update ALL registered instances (rebuilds image once, restarts all containers)'
    )
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List available instances'
    )

    args = parser.parse_args()

    # Validate mutually exclusive options
    if args.all and args.instance:
        print_error("Cannot use --all and --instance together")
        sys.exit(1)

    if args.list:
        print_instances()
        return

    print(f"\n{Colors.BOLD}{Colors.GREEN}RAG Memory - MCP Server Update Script{Colors.RESET}")
    print("Updates only the MCP container, databases are not affected\n")

    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    print_info(f"Working directory: {project_root}")

    # Step 0: Check Docker is running
    if not check_docker_running():
        sys.exit(1)

    # Handle --all flag: update all registered instances
    if args.all:
        update_all_instances()
        return

    # Determine instance name (single instance mode)
    instance_name = args.instance
    if not instance_name:
        instance_name = get_default_instance()
        if not instance_name:
            print_error("No instances found. Run setup.py first.")
            sys.exit(1)
        print_info(f"Using default instance: {instance_name}")

    # Step 1: Check MCP deployment exists
    is_deployed, system_compose_path, instance_info = check_mcp_deployment(instance_name)
    if not is_deployed:
        sys.exit(1)

    # Step 2: Rebuild MCP image from repo
    if not rebuild_mcp_image():
        sys.exit(1)

    # Step 3: Restart MCP container from system compose
    if not restart_mcp_container(system_compose_path, instance_name, instance_info):
        sys.exit(1)

    # Step 4: Verify health
    verify_mcp_health(instance_name, timeout_seconds=60)

    # Success summary
    ports = instance_info.get('ports', {})
    print_header("Update Complete")
    print_success(f"MCP server for instance '{instance_name}' has been updated")
    print_info("PostgreSQL and Neo4j containers were not affected")
    print()
    print_info("Useful commands:")
    print(f"  View logs: {Colors.CYAN}docker logs -f rag-memory-mcp-{instance_name}{Colors.RESET}")
    print(f"  Check status: {Colors.CYAN}rag instance status {instance_name}{Colors.RESET}")
    print(f"  Health check: {Colors.CYAN}curl http://localhost:{ports.get('mcp', 8000)}/health{Colors.RESET}")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Update cancelled by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
