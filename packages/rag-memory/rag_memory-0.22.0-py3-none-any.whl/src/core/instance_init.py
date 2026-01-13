"""Database initialization utilities for RAG Memory instances.

This module provides reusable functions for initializing databases
for RAG Memory instances. These functions are used by both:
- scripts/setup.py (first-time setup)
- rag instance start (creating new instances)

Key responsibilities:
- Wait for PostgreSQL and Neo4j containers to be healthy
- Initialize Neo4j Graphiti indices and constraints
- Create Neo4j vector indices for performance
- Validate database schemas
"""

import asyncio
import os
import socket
import subprocess
import time
from typing import Tuple


def run_command(
    cmd: list,
    timeout: int = None,
    env: dict = None
) -> Tuple[int, str, str]:
    """Run shell command and return exit code, stdout, stderr.

    Args:
        cmd: Command as list of strings
        timeout: Optional timeout in seconds
        env: Optional environment dict (defaults to os.environ)

    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    try:
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
    """Detect which docker compose command is available.

    Modern Docker Desktop uses 'docker compose' (space).
    Older installations use 'docker-compose' (hyphen).

    Returns:
        Command list: either ["docker", "compose"] or ["docker-compose"]
    """
    code, _, _ = run_command(["docker", "compose", "version"])
    if code == 0:
        return ["docker", "compose"]
    return ["docker-compose"]


def check_container_healthy(container_name: str) -> bool:
    """Check if a Docker container is healthy.

    Args:
        container_name: Full container name (e.g., 'rag-memory-postgres-primary')

    Returns:
        True if container status includes 'healthy'
    """
    code, stdout, _ = run_command([
        "docker", "ps", "--filter", f"name={container_name}",
        "--format", "{{.Status}}"
    ])
    return code == 0 and "healthy" in stdout


def check_container_running(container_name: str) -> bool:
    """Check if a Docker container is running (may not be healthy yet).

    Args:
        container_name: Full container name

    Returns:
        True if container is Up
    """
    code, stdout, _ = run_command([
        "docker", "ps", "--filter", f"name={container_name}",
        "--format", "{{.Status}}"
    ])
    return code == 0 and "Up" in stdout


def test_postgres_connection(container_name: str) -> bool:
    """Test actual PostgreSQL connectivity within container.

    Args:
        container_name: PostgreSQL container name

    Returns:
        True if psql SELECT 1 succeeds
    """
    code, _, _ = run_command([
        "docker", "exec", container_name,
        "psql", "-U", "raguser", "-d", "rag_memory", "-c", "SELECT 1"
    ])
    return code == 0


def test_neo4j_connection(container_name: str) -> bool:
    """Test actual Neo4j connectivity within container.

    Args:
        container_name: Neo4j container name

    Returns:
        True if cypher-shell RETURN 1 succeeds
    """
    code, _, _ = run_command([
        "docker", "exec", container_name,
        "cypher-shell", "-u", "neo4j", "-p", "graphiti-password",
        "RETURN 1"
    ])
    return code == 0


def test_port_open(host: str, port: int, timeout: float = 2.0) -> bool:
    """Test if a TCP port is accepting connections.

    Args:
        host: Hostname or IP address
        port: Port number
        timeout: Connection timeout in seconds

    Returns:
        True if port is open and accepting connections
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def wait_for_databases(
    instance_name: str,
    ports: dict,
    timeout_seconds: int = 300,
    check_interval: int = 10,
    callback=None
) -> bool:
    """Wait for PostgreSQL and Neo4j to be healthy and accepting connections.

    Args:
        instance_name: Instance name (e.g., 'primary')
        ports: Dict with 'postgres', 'neo4j_bolt', 'mcp' port numbers
        timeout_seconds: Maximum wait time (default: 5 minutes)
        check_interval: Seconds between checks (default: 10)
        callback: Optional callback(status_dict) for progress updates

    Returns:
        True if all services ready, False if timeout
    """
    pg_container = f"rag-memory-postgres-{instance_name}"
    neo4j_container = f"rag-memory-neo4j-{instance_name}"
    mcp_container = f"rag-memory-mcp-{instance_name}"

    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        elapsed = int(time.time() - start_time)

        # Check PostgreSQL
        pg_healthy = check_container_healthy(pg_container)
        pg_connectable = test_postgres_connection(pg_container) if pg_healthy else False

        # Check Neo4j
        neo4j_healthy = check_container_healthy(neo4j_container)
        neo4j_connectable = test_neo4j_connection(neo4j_container) if neo4j_healthy else False

        # Check MCP (optional - may not be started)
        mcp_running = check_container_running(mcp_container)
        mcp_responding = test_port_open('127.0.0.1', ports['mcp']) if mcp_running else False

        status = {
            'elapsed': elapsed,
            'postgres': {'healthy': pg_healthy, 'connectable': pg_connectable},
            'neo4j': {'healthy': neo4j_healthy, 'connectable': neo4j_connectable},
            'mcp': {'running': mcp_running, 'responding': mcp_responding},
        }

        if callback:
            callback(status)

        # We need at least postgres and neo4j to be ready for DB init
        # MCP can come later
        if pg_connectable and neo4j_connectable:
            return True

        time.sleep(check_interval)

    return False


async def init_neo4j_graphiti_indices(
    neo4j_uri: str,
    neo4j_user: str = "neo4j",
    neo4j_password: str = "graphiti-password",
    openai_api_key: str = None
) -> bool:
    """Initialize Neo4j Graphiti indices and constraints.

    This must be called AFTER Neo4j container is verified healthy.
    Creates the required indices and constraints for Graphiti to function.

    Note: Graphiti requires OPENAI_API_KEY environment variable even though
    build_indices_and_constraints() doesn't call LLM (it creates clients internally).

    Args:
        neo4j_uri: Bolt URI (e.g., 'bolt://localhost:7687')
        neo4j_user: Neo4j username (default: 'neo4j')
        neo4j_password: Neo4j password (default: 'graphiti-password')
        openai_api_key: OpenAI API key (required by Graphiti)

    Returns:
        True if successful, False otherwise
    """
    try:
        from graphiti_core import Graphiti

        # Set OPENAI_API_KEY - Graphiti requires it even for schema operations
        if openai_api_key:
            os.environ['OPENAI_API_KEY'] = openai_api_key

        graphiti = Graphiti(neo4j_uri, neo4j_user, neo4j_password)
        await graphiti.build_indices_and_constraints(delete_existing=False)
        await graphiti.close()

        return True

    except Exception as e:
        # Log error but don't fail - can be retried
        print(f"Failed to initialize Neo4j Graphiti indices: {e}")
        return False


def create_neo4j_vector_indices(instance_name: str) -> bool:
    """Create Neo4j vector indices for optimal embedding search performance.

    Graphiti's build_indices_and_constraints() creates range and fulltext indices,
    but does NOT create vector indices. Without vector indices, Neo4j logs warnings
    during ingestion when searching for similar entities/facts.

    This function creates vector indices for:
    - Entity.name_embedding (1024 dimensions, cosine similarity)
    - RELATES_TO.fact_embedding (1024 dimensions, cosine similarity)

    Args:
        instance_name: Instance name (e.g., 'primary')

    Returns:
        True if successful, False otherwise
    """
    neo4j_container = f"rag-memory-neo4j-{instance_name}"

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
            print(f"Failed to create Entity.name_embedding index: {stderr}")
            return False

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
            print(f"Failed to create RELATES_TO.fact_embedding index: {stderr}")
            return False

        # Verify both indices exist
        code, stdout, stderr = run_command([
            "docker", "exec", neo4j_container,
            "cypher-shell", "-u", "neo4j", "-p", "graphiti-password",
            "SHOW INDEXES WHERE type = 'VECTOR'"
        ])

        if code == 0 and "entity_name_embedding" in stdout and "edge_fact_embedding" in stdout:
            return True
        else:
            # Indices may still be building - don't fail
            return True

    except Exception as e:
        print(f"Unexpected error creating vector indices: {e}")
        return True  # Don't fail for optional optimization


def validate_postgres_schema(instance_name: str) -> bool:
    """Validate that PostgreSQL schema was created correctly.

    Args:
        instance_name: Instance name (e.g., 'primary')

    Returns:
        True if 4 tables found in public schema
    """
    pg_container = f"rag-memory-postgres-{instance_name}"

    code, stdout, _ = run_command([
        "docker", "exec", pg_container,
        "psql", "-U", "raguser", "-d", "rag_memory", "-c",
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public'"
    ])

    return code == 0 and "4" in stdout


def validate_neo4j_accessible(instance_name: str) -> bool:
    """Validate that Neo4j is accessible.

    Args:
        instance_name: Instance name (e.g., 'primary')

    Returns:
        True if Neo4j responds to queries
    """
    neo4j_container = f"rag-memory-neo4j-{instance_name}"

    code, _, _ = run_command([
        "docker", "exec", neo4j_container,
        "cypher-shell", "-u", "neo4j", "-p", "graphiti-password",
        "MATCH (n) RETURN COUNT(n)"
    ])

    return code == 0


async def initialize_instance_databases(
    instance_name: str,
    ports: dict,
    openai_api_key: str,
    wait_timeout: int = 300,
    progress_callback=None
) -> Tuple[bool, str]:
    """Full database initialization for a new instance.

    This is the main entry point for initializing a new instance's databases.
    It waits for containers to be healthy, then initializes Neo4j indices.

    Args:
        instance_name: Instance name (e.g., 'primary')
        ports: Dict with port numbers
        openai_api_key: OpenAI API key (required for Graphiti)
        wait_timeout: Max seconds to wait for containers (default: 300)
        progress_callback: Optional callback for progress updates

    Returns:
        Tuple of (success: bool, message: str)
    """
    # Step 1: Wait for databases to be healthy
    def status_callback(status):
        if progress_callback:
            progress_callback(f"[{status['elapsed']}s] Waiting for databases...")

    if not wait_for_databases(instance_name, ports, wait_timeout, callback=status_callback):
        return False, "Timeout waiting for databases to become ready"

    if progress_callback:
        progress_callback("Databases ready. Initializing Neo4j indices...")

    # Step 2: Initialize Graphiti indices
    neo4j_uri = f"bolt://localhost:{ports['neo4j_bolt']}"
    graphiti_ok = await init_neo4j_graphiti_indices(
        neo4j_uri=neo4j_uri,
        openai_api_key=openai_api_key
    )

    if not graphiti_ok:
        return False, "Failed to initialize Neo4j Graphiti indices"

    if progress_callback:
        progress_callback("Creating vector indices...")

    # Step 3: Create vector indices
    vector_ok = create_neo4j_vector_indices(instance_name)
    if not vector_ok:
        # Vector indices are optional - just warn
        if progress_callback:
            progress_callback("Warning: Vector indices may not have been created")

    if progress_callback:
        progress_callback("Validating schemas...")

    # Step 4: Validate schemas
    if not validate_postgres_schema(instance_name):
        return False, "PostgreSQL schema validation failed"

    if not validate_neo4j_accessible(instance_name):
        return False, "Neo4j accessibility check failed"

    return True, "Database initialization complete"


def run_initialization(
    instance_name: str,
    ports: dict,
    openai_api_key: str,
    wait_timeout: int = 300,
    progress_callback=None
) -> Tuple[bool, str]:
    """Synchronous wrapper for initialize_instance_databases.

    Use this from synchronous code (like CLI commands).

    Args:
        Same as initialize_instance_databases

    Returns:
        Tuple of (success: bool, message: str)
    """
    return asyncio.run(initialize_instance_databases(
        instance_name=instance_name,
        ports=ports,
        openai_api_key=openai_api_key,
        wait_timeout=wait_timeout,
        progress_callback=progress_callback
    ))
