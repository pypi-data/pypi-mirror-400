"""Configuration loader for RAG Memory with OS-standard locations.

This module provides cross-platform configuration loading that supports:
1. Multi-instance configuration (each instance has its own settings)
2. Environment variable overrides (highest priority)
3. OS-standard config file location (user-specific, platform-aware)

Config locations:
- macOS: ~/Library/Application Support/rag-memory/config.yaml
- Linux: ~/.config/rag-memory/config.yaml
- Windows: %LOCALAPPDATA%\\rag-memory\\config.yaml

Configuration Structure (multi-instance):
    instances:
      instance-name:
        openai_api_key: "sk-..."
        database_url: "postgresql://..."
        neo4j_uri: "bolt://..."
        neo4j_user: "neo4j"
        neo4j_password: "..."
        neo4j_http_port: 7475
        mcp_sse_port: 8000
        backup_cron_expression: "0 5 * * *"
        backup_archive_path: "./backups/instance-name"
        backup_retention_days: 14
        max_reflexion_iterations: 0
        mounts:
          - path: /Users/yourname
            read_only: true

Legacy Structure (single instance, backward compatible):
    server:
      openai_api_key: "sk-..."
      database_url: "postgresql://..."
      ...
    mounts:
      - path: /Users/yourname
        read_only: true
"""

import os
import stat
from pathlib import Path
from typing import Any

import platformdirs
import yaml

# List of required configuration keys per instance
REQUIRED_INSTANCE_KEYS = [
    'openai_api_key',
    'database_url',
    'neo4j_uri',
    'neo4j_user',
    'neo4j_password',
]

# Optional configuration keys (won't fail if missing)
OPTIONAL_INSTANCE_KEYS = [
    'neo4j_http_port',
    'mcp_sse_port',
    'backup_cron_expression',
    'backup_archive_path',
    'backup_retention_days',
    'graphiti_model',
    'graphiti_small_model',
    'max_reflexion_iterations',
    'search_strategy',
    'mounts',
    'dry_run_model',
    'dry_run_temperature',
    'dry_run_max_tokens',
]

# Map config keys to environment variable names
CONFIG_KEY_TO_ENV_VAR = {
    'openai_api_key': 'OPENAI_API_KEY',
    'database_url': 'DATABASE_URL',
    'neo4j_uri': 'NEO4J_URI',
    'neo4j_user': 'NEO4J_USER',
    'neo4j_password': 'NEO4J_PASSWORD',
    'graphiti_model': 'GRAPHITI_MODEL',
    'graphiti_small_model': 'GRAPHITI_SMALL_MODEL',
    'max_reflexion_iterations': 'MAX_REFLEXION_ITERATIONS',
    'search_strategy': 'SEARCH_STRATEGY',
    'dry_run_model': 'DRY_RUN_MODEL',
    'dry_run_temperature': 'DRY_RUN_TEMPERATURE',
    'dry_run_max_tokens': 'DRY_RUN_MAX_TOKENS',
}


def get_system_config_dir() -> Path:
    """
    Get the OS-standard configuration directory for RAG Memory.

    This function is used by instance management commands and always returns
    the system-level config directory, skipping repo-local ./config/ detection.

    Detection logic (in order of priority):
    1. If RAG_CONFIG_PATH env var is set: use that directory
    2. Otherwise: use platformdirs for OS-standard locations:
       - macOS: ~/Library/Application Support/rag-memory
       - Linux (including Docker): ~/.config/rag-memory (respects $XDG_CONFIG_HOME)
       - Windows: %LOCALAPPDATA%\\rag-memory

    Returns:
        Path to system configuration directory
    """
    # 1. Check environment variable override
    if env_override := os.getenv('RAG_CONFIG_PATH'):
        config_dir = Path(env_override)
    else:
        # 2. Use OS-standard locations (platformdirs)
        # - macOS: ~/Library/Application Support/rag-memory
        # - Linux (including Docker): ~/.config/rag-memory
        # - Windows: %LOCALAPPDATA%\rag-memory
        config_dir = Path(platformdirs.user_config_dir('rag-memory', appauthor=False))

    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_dir() -> Path:
    """
    Get the configuration directory for RAG Memory.

    Detection logic (in order of priority):
    1. If RAG_CONFIG_PATH env var is set: use that directory
    2. If repo-local config exists (./config/): use that (dev/test scenarios)
    3. Otherwise: use platformdirs for OS-standard locations:
       - macOS: ~/Library/Application Support/rag-memory
       - Linux (including Docker): ~/.config/rag-memory (respects $XDG_CONFIG_HOME)
       - Windows: %LOCALAPPDATA%\\rag-memory

    Returns:
        Path to configuration directory
    """
    # 1. Check environment variable override
    if env_override := os.getenv('RAG_CONFIG_PATH'):
        config_dir = Path(env_override)
    # 2. Check for repo-local config (when running from within repo)
    elif (repo_local := Path('./config')).exists():
        config_dir = repo_local
    else:
        # 3. System-level CLI and Docker: use OS-standard locations
        # - macOS: ~/Library/Application Support/rag-memory
        # - Linux (including Docker): ~/.config/rag-memory
        # - Windows: %LOCALAPPDATA%\rag-memory
        config_dir = Path(platformdirs.user_config_dir('rag-memory', appauthor=False))

    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_path() -> Path:
    """
    Get the path to the RAG Memory configuration file.

    Returns:
        Path to config.yaml (or config.test.yaml for tests) in OS-appropriate location
    """
    config_dir = get_config_dir()

    # Check if a specific config filename is requested (for tests)
    # Environment variable: RAG_CONFIG_FILE (e.g., 'config.test.yaml')
    config_filename = os.getenv('RAG_CONFIG_FILE', 'config.yaml')

    return config_dir / config_filename


def load_config(file_path: Path = None) -> dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        file_path: Path to config file. Defaults to OS-standard location.

    Returns:
        Dictionary with config contents, or empty dict if not found.
    """
    if file_path is None:
        file_path = get_config_path()

    if not file_path.exists():
        return {}

    try:
        with open(file_path, 'r') as f:
            config = yaml.safe_load(f) or {}
        return config
    except Exception:
        # Log error but don't crash - config loading shouldn't break the app
        return {}


def save_config(config: dict[str, Any], file_path: Path = None) -> bool:
    """
    Save configuration to YAML file.

    Args:
        config: Configuration dictionary
        file_path: Path to config file. Defaults to OS-standard location.

    Returns:
        True if saved successfully, False otherwise.
    """
    if file_path is None:
        file_path = get_config_path()

    try:
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write YAML config
        with open(file_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        # Set restrictive permissions on Unix-like systems (chmod 0o600)
        try:
            if os.name != 'nt':
                os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)
        except Exception:
            pass

        return True
    except Exception:
        return False


def is_legacy_config(config: dict = None) -> bool:
    """
    Check if config uses legacy (pre-multi-instance) format.

    Legacy format has 'server' section at top level.
    New format has 'instances' section with per-instance configs.

    Args:
        config: Config dict to check. Loads from file if None.

    Returns:
        True if legacy format, False if new multi-instance format.
    """
    if config is None:
        config = load_config()

    # Legacy format has 'server' section, new format has 'instances'
    has_server = 'server' in config
    has_instances = 'instances' in config

    # If both exist, prefer new format (instances)
    if has_instances:
        return False

    return has_server


def list_configured_instances(use_system_config: bool = False) -> list[str]:
    """
    List all instances configured in config.yaml.

    Args:
        use_system_config: If True, always use OS-standard config location
                          (skips repo-local ./config/). Used by instance
                          management commands.

    Returns:
        List of instance names. Empty list if no instances or legacy format.
    """
    if use_system_config:
        config_path = get_system_config_dir() / 'config.yaml'
        config = load_config(config_path) if config_path.exists() else {}
    else:
        config = load_config()

    if is_legacy_config(config):
        return []

    instances = config.get('instances', {})
    return list(instances.keys()) if isinstance(instances, dict) else []


def get_instance_config(instance_name: str) -> dict[str, Any]:
    """
    Get configuration for a specific instance.

    Args:
        instance_name: Name of the instance (e.g., "primary", "research")

    Returns:
        Dictionary with instance configuration, or empty dict if not found.

    Raises:
        ValueError: If instance_name is None or empty.
    """
    if not instance_name:
        raise ValueError("instance_name is required")

    config = load_config()

    # Check for new multi-instance format first
    instances = config.get('instances', {})
    if isinstance(instances, dict) and instance_name in instances:
        instance_config = instances[instance_name]
        return instance_config if isinstance(instance_config, dict) else {}

    # Fall back to legacy format if instance matches default
    if is_legacy_config(config):
        # For legacy configs, treat as a single instance
        # The MCP container inside Docker won't hit this path since it uses
        # the new format, but CLI tools might for backward compatibility
        server_config = config.get('server', {})
        mounts = config.get('mounts', [])
        if mounts:
            server_config['mounts'] = mounts
        return server_config

    return {}


def load_environment_variables(instance_name: str = None):
    """
    Load environment variables from config file.

    Priority order (highest to lowest):
    1. Environment variables (already set in shell/docker-compose)
    2. Instance config from config.yaml
    3. Legacy server config (backward compatibility)

    Args:
        instance_name: Instance to load config for. If None, tries to read
                      from INSTANCE_NAME env var, then falls back to legacy format.
    """
    # Determine instance name
    if instance_name is None:
        instance_name = os.getenv('INSTANCE_NAME')

    config = load_config()

    # Get config based on format
    if instance_name and not is_legacy_config(config):
        # New multi-instance format
        instance_config = get_instance_config(instance_name)
    elif is_legacy_config(config):
        # Legacy format - use server section
        instance_config = config.get('server', {})
    else:
        # No valid config found
        instance_config = {}

    # Set environment variables (only if not already set)
    for config_key, env_var in CONFIG_KEY_TO_ENV_VAR.items():
        if config_key in instance_config and env_var not in os.environ:
            os.environ[env_var] = str(instance_config[config_key])


def get_mounts(instance_name: str = None) -> list[dict[str, Any]]:
    """
    Get the list of read-only directory mounts from config.

    Args:
        instance_name: Instance to get mounts for. If None, tries to read
                      from INSTANCE_NAME env var, then falls back to legacy format.

    Returns:
        List of mount configurations, each with 'path' and 'read_only' keys.
        Empty list if no mounts configured.
    """
    # Determine instance name
    if instance_name is None:
        instance_name = os.getenv('INSTANCE_NAME')

    config = load_config()

    # Get mounts based on format
    if instance_name and not is_legacy_config(config):
        # New multi-instance format - mounts are inside instance config
        instance_config = get_instance_config(instance_name)
        mounts = instance_config.get('mounts', [])
    elif is_legacy_config(config):
        # Legacy format - mounts are at top level
        mounts = config.get('mounts', [])
    else:
        mounts = []

    return mounts if isinstance(mounts, list) else []


def ensure_config_exists(instance_name: str = None) -> bool:
    """
    Check if config file exists and contains required settings.

    Args:
        instance_name: Instance to check. If None, tries INSTANCE_NAME env var,
                      then checks for any valid config.

    Returns:
        True if config exists and has all required keys for the instance.
    """
    config_path = get_config_path()
    if not config_path.exists():
        return False

    # Determine instance name
    if instance_name is None:
        instance_name = os.getenv('INSTANCE_NAME')

    config = load_config(config_path)

    # Get config based on format
    if instance_name and not is_legacy_config(config):
        instance_config = get_instance_config(instance_name)
    elif is_legacy_config(config):
        instance_config = config.get('server', {})
    else:
        # No valid format
        return False

    # Check if all required keys are present (either in config or in environment)
    for key in REQUIRED_INSTANCE_KEYS:
        env_var = CONFIG_KEY_TO_ENV_VAR.get(key, key.upper())
        if key not in instance_config and env_var not in os.environ:
            return False

    return True


def get_missing_config_keys(instance_name: str = None) -> list[str]:
    """
    Get list of required configuration keys that are missing.

    Args:
        instance_name: Instance to check. If None, tries INSTANCE_NAME env var.

    Returns:
        List of missing key names. Empty list if all keys present.
    """
    # Determine instance name
    if instance_name is None:
        instance_name = os.getenv('INSTANCE_NAME')

    config_path = get_config_path()
    config = load_config(config_path) if config_path.exists() else {}

    # Get config based on format
    if instance_name and not is_legacy_config(config):
        instance_config = get_instance_config(instance_name)
    elif is_legacy_config(config):
        instance_config = config.get('server', {})
    else:
        instance_config = {}

    missing = []
    for key in REQUIRED_INSTANCE_KEYS:
        env_var = CONFIG_KEY_TO_ENV_VAR.get(key, key.upper())
        if key not in instance_config and env_var not in os.environ:
            missing.append(key)

    return missing


def is_path_in_mounts(file_path: str, instance_name: str = None) -> tuple[bool, str]:
    """
    Check if a file path is within one of the configured mount directories.

    This is used by the MCP server running in Docker to validate that tools
    like ingest_file and ingest_directory only access paths that were
    explicitly mounted and made available at setup time.

    Args:
        file_path: Absolute or relative path to check
        instance_name: Instance to check mounts for. If None, tries INSTANCE_NAME env var.

    Returns:
        Tuple of (is_valid, message) where:
        - is_valid (bool): True if path is within a configured mount
        - message (str): Explanation of why path is valid/invalid
    """
    try:
        # Resolve path to absolute, canonical form
        requested_path = Path(file_path).expanduser().resolve()

        # Get configured mounts for this instance
        mounts = get_mounts(instance_name)

        # If no mounts configured, reject all file access
        if not mounts:
            return False, (
                "No directories are currently mounted for file access. "
                "Run setup.py to configure mounts for this instance."
            )

        # Check if path is within any mounted directory
        for mount in mounts:
            mount_path = mount.get('path')
            if not mount_path:
                continue

            try:
                mount_path_resolved = Path(mount_path).expanduser().resolve()

                # Check if requested path is under the mount
                # This will succeed if requested_path == mount_path or is a descendant
                requested_path.relative_to(mount_path_resolved)
                return True, f"Path is within configured mount: {mount_path}"

            except ValueError:
                # relative_to() raises ValueError if path is not relative
                # This means requested_path is not under this mount
                continue

        # Path is not under any mount
        mounted_dirs = [m.get('path') for m in mounts if m.get('path')]
        return False, (
            f"Path is not within configured mounts. "
            f"Mounted directories: {', '.join(mounted_dirs)}"
        )

    except Exception as e:
        return False, f"Error validating path: {str(e)}"


def add_instance_config(
    instance_name: str,
    instance_config: dict[str, Any],
    config_path: Path = None
) -> bool:
    """
    Add or update an instance configuration in config.yaml.

    Args:
        instance_name: Name of the instance to add/update
        instance_config: Configuration dictionary for the instance
        config_path: Path to config file. Defaults to OS-standard location.

    Returns:
        True if saved successfully, False otherwise.
    """
    if config_path is None:
        config_path = get_config_path()

    # Load existing config
    config = load_config(config_path)

    # Ensure instances section exists
    if 'instances' not in config:
        config['instances'] = {}

    # Add/update instance
    config['instances'][instance_name] = instance_config

    # If migrating from legacy format, remove old sections
    if 'server' in config:
        del config['server']
    if 'mounts' in config and 'instances' in config:
        # Only remove top-level mounts if we have instances section
        del config['mounts']

    return save_config(config, config_path)


def remove_instance_config(instance_name: str, config_path: Path = None) -> bool:
    """
    Remove an instance configuration from config.yaml.

    Args:
        instance_name: Name of the instance to remove
        config_path: Path to config file. Defaults to OS-standard location.

    Returns:
        True if removed successfully, False otherwise.
    """
    if config_path is None:
        config_path = get_config_path()

    config = load_config(config_path)

    instances = config.get('instances', {})
    if instance_name in instances:
        del instances[instance_name]
        config['instances'] = instances
        return save_config(config, config_path)

    return False


# Legacy compatibility aliases
REQUIRED_SERVER_KEYS = REQUIRED_INSTANCE_KEYS
OPTIONAL_SERVER_KEYS = OPTIONAL_INSTANCE_KEYS


def _config_key_to_env_var(config_key: str) -> str:
    """Convert config key to environment variable name."""
    return CONFIG_KEY_TO_ENV_VAR.get(config_key, config_key.upper())
