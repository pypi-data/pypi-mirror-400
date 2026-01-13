"""Unit tests for InstanceRegistry.

Tests cover:
- Instance creation and registration
- Port allocation strategy
- Instance lookup and listing
- Initialization marking
- Instance removal
- Registry persistence
"""

import json
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.core.instance_registry import InstanceRegistry, get_instance_registry


@pytest.fixture
def temp_config_dir():
    """Create a temporary config directory for testing."""
    with TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def registry(temp_config_dir):
    """Create a fresh InstanceRegistry with temp storage."""
    return InstanceRegistry(config_dir=temp_config_dir)


class TestInstanceRegistryCreation:
    """Tests for registry initialization."""

    def test_creates_config_directory(self, temp_config_dir):
        """Registry should create config directory if missing."""
        config_path = temp_config_dir / "subdir"
        assert not config_path.exists()

        InstanceRegistry(config_dir=config_path)

        assert config_path.exists()

    def test_creates_registry_file(self, temp_config_dir):
        """Registry should create instances.json on init."""
        registry_file = temp_config_dir / "instances.json"
        assert not registry_file.exists()

        InstanceRegistry(config_dir=temp_config_dir)

        assert registry_file.exists()
        data = json.loads(registry_file.read_text())
        assert data == {"version": 1, "instances": []}

    def test_preserves_existing_registry(self, temp_config_dir):
        """Registry should not overwrite existing data."""
        registry_file = temp_config_dir / "instances.json"
        registry_file.parent.mkdir(parents=True, exist_ok=True)

        existing_data = {
            "version": 1,
            "instances": [{"name": "existing", "ports": {}}]
        }
        registry_file.write_text(json.dumps(existing_data))

        registry = InstanceRegistry(config_dir=temp_config_dir)
        instances = registry.list_instances()

        assert len(instances) == 1
        assert instances[0]["name"] == "existing"


class TestInstanceRegistration:
    """Tests for registering new instances."""

    def test_register_first_instance(self, registry):
        """First instance should get base ports."""
        instance = registry.register("primary")

        assert instance["name"] == "primary"
        assert instance["ports"]["postgres"] == 54320
        assert instance["ports"]["neo4j_bolt"] == 7687
        assert instance["ports"]["neo4j_http"] == 7474
        assert instance["ports"]["mcp"] == 8000
        assert instance["initialized"] is False
        assert "created_at" in instance

    def test_register_second_instance(self, registry):
        """Second instance should get offset ports."""
        registry.register("primary")
        instance = registry.register("secondary")

        assert instance["ports"]["postgres"] == 54330  # +10
        assert instance["ports"]["neo4j_bolt"] == 7688  # +1
        assert instance["ports"]["neo4j_http"] == 7475  # +1
        assert instance["ports"]["mcp"] == 8001  # +1

    def test_register_third_instance(self, registry):
        """Third instance should get double offset."""
        registry.register("first")
        registry.register("second")
        instance = registry.register("third")

        assert instance["ports"]["postgres"] == 54340  # +20
        assert instance["ports"]["neo4j_bolt"] == 7689  # +2
        assert instance["ports"]["neo4j_http"] == 7476  # +2
        assert instance["ports"]["mcp"] == 8002  # +2

    def test_register_with_config_overrides(self, registry):
        """Instance should store config overrides."""
        overrides = {"backup_retention_days": 30}
        instance = registry.register("custom", config_overrides=overrides)

        assert instance["config_overrides"] == overrides

    def test_register_duplicate_name_raises(self, registry):
        """Registering duplicate name should raise ValueError."""
        registry.register("primary")

        with pytest.raises(ValueError, match="already exists"):
            registry.register("primary")

    def test_register_empty_name_raises(self, registry):
        """Empty name should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            registry.register("")

    def test_register_invalid_name_raises(self, registry):
        """Invalid characters in name should raise ValueError."""
        with pytest.raises(ValueError, match="alphanumeric"):
            registry.register("invalid name")

        with pytest.raises(ValueError, match="alphanumeric"):
            registry.register("invalid.name")

    def test_register_valid_special_chars(self, registry):
        """Hyphens and underscores should be allowed."""
        instance1 = registry.register("my-instance")
        instance2 = registry.register("my_instance")

        assert instance1["name"] == "my-instance"
        assert instance2["name"] == "my_instance"


class TestInstanceLookup:
    """Tests for finding instances."""

    def test_get_instance_exists(self, registry):
        """Should return instance when found."""
        registry.register("primary")
        instance = registry.get_instance("primary")

        assert instance is not None
        assert instance["name"] == "primary"

    def test_get_instance_not_found(self, registry):
        """Should return None when not found."""
        instance = registry.get_instance("nonexistent")
        assert instance is None

    def test_instance_exists_true(self, registry):
        """instance_exists should return True for existing."""
        registry.register("primary")
        assert registry.instance_exists("primary") is True

    def test_instance_exists_false(self, registry):
        """instance_exists should return False for missing."""
        assert registry.instance_exists("nonexistent") is False

    def test_list_instances_empty(self, registry):
        """Should return empty list when no instances."""
        instances = registry.list_instances()
        assert instances == []

    def test_list_instances_multiple(self, registry):
        """Should return all instances."""
        registry.register("first")
        registry.register("second")
        registry.register("third")

        instances = registry.list_instances()

        assert len(instances) == 3
        names = [i["name"] for i in instances]
        assert "first" in names
        assert "second" in names
        assert "third" in names


class TestPortAllocation:
    """Tests for port allocation strategy."""

    def test_calculate_ports_offset_zero(self, registry):
        """Offset 0 should return base ports."""
        ports = registry.calculate_ports(0)

        assert ports["postgres"] == 54320
        assert ports["neo4j_bolt"] == 7687
        assert ports["neo4j_http"] == 7474
        assert ports["mcp"] == 8000

    def test_calculate_ports_offset_one(self, registry):
        """Offset 1 should return first incremented ports."""
        ports = registry.calculate_ports(1)

        assert ports["postgres"] == 54330
        assert ports["neo4j_bolt"] == 7688
        assert ports["neo4j_http"] == 7475
        assert ports["mcp"] == 8001

    def test_calculate_ports_offset_five(self, registry):
        """Offset 5 should follow pattern."""
        ports = registry.calculate_ports(5)

        assert ports["postgres"] == 54370  # 54320 + (5 * 10)
        assert ports["neo4j_bolt"] == 7692  # 7687 + (5 * 1)
        assert ports["neo4j_http"] == 7479  # 7474 + (5 * 1)
        assert ports["mcp"] == 8005  # 8000 + (5 * 1)

    def test_get_next_port_offset_empty(self, registry):
        """Should return 0 when no instances."""
        offset = registry.get_next_port_offset()
        assert offset == 0

    def test_get_next_port_offset_sequential(self, registry):
        """Should return next available offset."""
        registry.register("first")
        assert registry.get_next_port_offset() == 1

        registry.register("second")
        assert registry.get_next_port_offset() == 2

    def test_port_reuse_after_delete(self, registry):
        """Deleting instance should NOT allow port reuse (gap stays)."""
        registry.register("first")  # offset 0
        registry.register("second")  # offset 1
        registry.register("third")  # offset 2

        registry.unregister("second")

        # Next offset should still be 3, not 1 (we don't fill gaps)
        offset = registry.get_next_port_offset()
        assert offset == 3


class TestInitialization:
    """Tests for instance initialization tracking."""

    def test_new_instance_not_initialized(self, registry):
        """New instances should start as not initialized."""
        registry.register("primary")
        assert registry.is_initialized("primary") is False

    def test_mark_initialized(self, registry):
        """mark_initialized should set initialized=True."""
        registry.register("primary")

        result = registry.mark_initialized("primary")

        assert result is True
        assert registry.is_initialized("primary") is True

    def test_mark_initialized_nonexistent(self, registry):
        """mark_initialized should return False for missing instance."""
        result = registry.mark_initialized("nonexistent")
        assert result is False

    def test_is_initialized_nonexistent(self, registry):
        """is_initialized should return False for missing instance."""
        assert registry.is_initialized("nonexistent") is False


class TestUnregistration:
    """Tests for removing instances."""

    def test_unregister_existing(self, registry):
        """Should remove existing instance."""
        registry.register("primary")
        assert registry.instance_exists("primary") is True

        result = registry.unregister("primary")

        assert result is True
        assert registry.instance_exists("primary") is False

    def test_unregister_nonexistent(self, registry):
        """Should return False for missing instance."""
        result = registry.unregister("nonexistent")
        assert result is False

    def test_unregister_preserves_others(self, registry):
        """Unregistering one should not affect others."""
        registry.register("first")
        registry.register("second")
        registry.register("third")

        registry.unregister("second")

        assert registry.instance_exists("first") is True
        assert registry.instance_exists("second") is False
        assert registry.instance_exists("third") is True


class TestPersistence:
    """Tests for registry persistence."""

    def test_survives_reload(self, temp_config_dir):
        """Data should survive registry recreation."""
        # Create and populate registry
        registry1 = InstanceRegistry(config_dir=temp_config_dir)
        registry1.register("primary")
        registry1.mark_initialized("primary")

        # Create new registry instance with same dir
        registry2 = InstanceRegistry(config_dir=temp_config_dir)

        assert registry2.instance_exists("primary")
        assert registry2.is_initialized("primary")
        instance = registry2.get_instance("primary")
        assert instance["ports"]["postgres"] == 54320


class TestBackupDirectory:
    """Tests for backup directory management."""

    def test_get_backup_dir(self, registry, temp_config_dir):
        """Should return instance-specific backup path."""
        backup_dir = registry.get_backup_dir("primary")

        expected = temp_config_dir / "backups" / "primary"
        assert backup_dir == expected

    def test_backup_dirs_unique_per_instance(self, registry):
        """Each instance should have unique backup directory."""
        dir1 = registry.get_backup_dir("first")
        dir2 = registry.get_backup_dir("second")

        assert dir1 != dir2
        assert "first" in str(dir1)
        assert "second" in str(dir2)


class TestComposeFile:
    """Tests for compose file management."""

    def test_get_compose_file_exists(self, temp_config_dir):
        """Should return path when compose file exists."""
        compose_file = temp_config_dir / "docker-compose.instance.yml"
        compose_file.write_text("version: '3'")

        registry = InstanceRegistry(config_dir=temp_config_dir)
        result = registry.get_compose_file()

        assert result == compose_file

    def test_get_compose_file_missing_raises(self, registry):
        """Should raise FileNotFoundError when missing."""
        with pytest.raises(FileNotFoundError, match="Compose template not found"):
            registry.get_compose_file()


class TestFactoryFunction:
    """Tests for get_instance_registry factory."""

    def test_factory_creates_registry(self, temp_config_dir):
        """Factory should create working registry."""
        registry = get_instance_registry(config_dir=temp_config_dir)

        assert isinstance(registry, InstanceRegistry)
        registry.register("test")
        assert registry.instance_exists("test")

    def test_factory_uses_default_dir(self):
        """Factory without arg should use platformdirs location."""
        registry = get_instance_registry()

        # Should not raise, uses platform-specific default
        assert registry.config_dir is not None
