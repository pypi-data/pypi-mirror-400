"""Instance registry for managing multiple RAG Memory stacks.

This module provides persistent storage and management for multiple
RAG Memory instances, including automatic port allocation and
collision prevention.

The registry is stored at ~/.config/rag-memory/instances.json
(or platform equivalent via platformdirs).
"""

import json
from datetime import datetime, timezone
from pathlib import Path

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

    def get_instance(self, name: str) -> dict:
        """Get instance by name.

        Args:
            name: Instance name (e.g., "primary", "research")

        Returns:
            Instance dict with name, created_at, ports, config_overrides, initialized
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
            raise ValueError(
                "Instance name must contain only alphanumeric characters, "
                "hyphens, and underscores"
            )

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
            'initialized': False,  # Set to True after Neo4j indices created
        }

        # Save to registry
        data = self._load()
        data['instances'].append(instance)
        self._save(data)

        return instance

    def mark_initialized(self, name: str) -> bool:
        """Mark an instance as fully initialized (Neo4j indices created).

        Args:
            name: Instance name to mark as initialized.

        Returns:
            True if updated, False if not found.
        """
        data = self._load()
        for instance in data['instances']:
            if instance['name'] == name:
                instance['initialized'] = True
                self._save(data)
                return True
        return False

    def is_initialized(self, name: str) -> bool:
        """Check if an instance has been fully initialized.

        Args:
            name: Instance name to check.

        Returns:
            True if initialized, False otherwise.
        """
        instance = self.get_instance(name)
        if instance is None:
            return False
        return instance.get('initialized', False)

    def unregister(self, name: str) -> bool:
        """Remove instance from registry.

        Note: This does NOT stop containers or delete volumes.
        Use instance CLI delete command for full cleanup.

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
