"""Command-line interface for RAG Memory - Thin Orchestrator."""

import logging
import click

# Suppress harmless Neo4j server notifications (they query properties before they exist)
# These are cosmetic warnings, not errors. Real Neo4j errors will still be shown.
logging.getLogger("neo4j.notifications").setLevel(logging.ERROR)

# Suppress verbose httpx HTTP request logs (OpenAI API calls)
# These clutter console output during graph queries. Errors still visible.
logging.getLogger("httpx").setLevel(logging.WARNING)

# Suppress python-dotenv parsing warnings from third-party libraries
# Libraries like crawl4ai and graphiti-core auto-load .env files during import.
# These warnings are cosmetic - the variables still load correctly.
logging.getLogger("dotenv.main").setLevel(logging.ERROR)

# CRITICAL: Load configuration BEFORE importing command modules
# Third-party libraries (graphiti-core, crawl4ai) auto-load ~/.env at import time.
# By loading our config first, we ensure system config takes precedence over ~/.env.
# Priority: 1) Shell env vars, 2) System config, 3) ~/.env (ignored if already set)
#
# For multi-instance configs: If only one instance exists and no INSTANCE_NAME is set,
# we automatically use that instance. For multiple instances, commands that need
# database access should have the user set INSTANCE_NAME or use --instance flag.
from src.core.config_loader import load_environment_variables, list_configured_instances
import os

# Auto-select instance if only one exists and INSTANCE_NAME not set
if not os.getenv('INSTANCE_NAME'):
    instances = list_configured_instances()
    if len(instances) == 1:
        os.environ['INSTANCE_NAME'] = instances[0]

load_environment_variables()

# Import all command groups and commands (AFTER config is loaded)
from src.cli_commands.service import service_group, start, stop, restart, status
from src.cli_commands.instance import instance_group
from src.cli_commands.collection import collection
from src.cli_commands.ingest import ingest
from src.cli_commands.search import search
from src.cli_commands.document import document
from src.cli_commands.graph import graph
from src.cli_commands.analyze import analyze
from src.cli_commands.config import config
from src.cli_commands.logs import logs


def get_version():
    """Get package version from installed metadata."""
    try:
        from importlib.metadata import version
        return version("rag-memory")
    except Exception:
        return "unknown"


@click.group()
@click.version_option(version=get_version(), prog_name="rag")
def main():
    """RAG Memory - AI knowledge base management system.

    Instance Management (Multi-Instance):
      rag instance start <name>   # Create/start an instance
      rag instance stop <name>    # Stop an instance
      rag instance delete <name>  # Delete an instance
      rag instance list           # List all instances
      rag instance status <name>  # Detailed instance status
      rag instance logs <name>    # View instance logs

    Service Management (Legacy - uses default instance):
      rag start/stop/restart  # Manage services
      rag status              # Check system status
      rag logs                # View service logs
      rag config show         # View configuration

    Document Management:
      rag collection create/list/info/delete
      rag ingest text/file/directory/url
      rag search "query"
      rag document list/view/update/delete

    Knowledge Graph:
      rag graph query-relationships
      rag graph query-temporal

    Analysis:
      rag analyze website <url>

    Use 'rag COMMAND --help' for more information on a specific command.
    """
    # NOTE: Configuration validation removed from main entrypoint.
    # Instance management commands (rag instance start/stop/etc) don't need database config.
    # Commands that need database access handle validation in their own command groups.
    pass


# Register command groups
main.add_command(service_group)  # rag service start/stop/restart/status
main.add_command(instance_group) # rag instance start/stop/delete/list/status/logs
main.add_command(collection)     # rag collection create/list/info/delete
main.add_command(ingest)         # rag ingest text/file/directory/url
main.add_command(document)       # rag document list/view/update/delete
main.add_command(graph)          # rag graph query-relationships/query-temporal
main.add_command(analyze)        # rag analyze website
main.add_command(config)         # rag config show/edit/set

# Register standalone commands
main.add_command(search)         # rag search
main.add_command(logs)           # rag logs

# Register service shortcuts as top-level commands
main.add_command(start, name='start')      # rag start
main.add_command(stop, name='stop')        # rag stop
main.add_command(restart, name='restart')  # rag restart
main.add_command(status, name='status')    # rag status


if __name__ == "__main__":
    main()
