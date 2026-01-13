"""
MCP Server for RAG Memory.

Exposes RAG functionality via Model Context Protocol for AI agents.
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from mcp.server.fastmcp import FastMCP, Context
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from src.core.database import get_database
from src.core.embeddings import get_embedding_generator
from src.core.collections import get_collection_manager
from src.core.first_run import ensure_config_or_exit
from src.core.config_loader import load_environment_variables
from src.retrieval.search import get_similarity_search
from src.ingestion.document_store import get_document_store
from src.unified import GraphStore, UnifiedIngestionMediator
from src.mcp.tools import (
    search_documents_impl,
    list_collections_impl,
    create_collection_impl,
    get_collection_metadata_schema_impl,
    delete_collection_impl,
    ingest_text_impl,
    get_document_by_id_impl,
    get_collection_info_impl,
    analyze_website_impl,
    ingest_url_impl,
    ingest_file_impl,
    ingest_directory_impl,
    list_directory_impl,
    update_document_impl,
    delete_document_impl,
    list_documents_impl,
    query_relationships_impl,
    query_temporal_impl,
    update_collection_metadata_impl,
)

logger = logging.getLogger(__name__)


def configure_logging():
    """
    Configure logging for MCP server.

    Called when server starts, NOT at module import time.
    This prevents CLI commands from triggering DEBUG logging when they
    import from src.mcp.tools.
    """
    # Configure cross-platform file logging
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "mcp_server.log"),
            logging.StreamHandler()  # Also log to stderr for debugging
        ]
    )

    # Suppress harmless Neo4j server notifications (they query properties before they exist)
    # These are cosmetic warnings about missing indices on array properties, not errors.
    # Real Neo4j errors will still be shown.
    logging.getLogger("neo4j.notifications").setLevel(logging.ERROR)

    # Suppress verbose httpx HTTP request logs (OpenAI API calls)
    # These clutter logs during graph extraction and embeddings generation.
    # Errors and warnings still visible.
    logging.getLogger("httpx").setLevel(logging.WARNING)

    # TEMPORARILY: Ensure crawl4ai logging is visible (for verifying patched code)
    logging.getLogger("crawl4ai").setLevel(logging.INFO)

# Global variables to hold RAG components (initialized once on first use)
db = None
embedder = None
coll_mgr = None
searcher = None
doc_store = None

# Global variables for Knowledge Graph components
graph_store = None
unified_mediator = None

# Lazy initialization state (prevents concurrent session conflicts)
_initialized = False
_init_lock = asyncio.Lock()


async def get_or_create_components():
    """
    Lazy singleton initialization of RAG and Knowledge Graph components.

    This function is called by the lifespan manager and ensures components
    are initialized exactly once, even when multiple MCP clients connect
    concurrently via SSE. The lock prevents race conditions.

    **BUG FIX:** Previously, each SSE session would create new driver instances
    in the lifespan context manager, overwriting module-level globals. When a
    session disconnected, lifespan cleanup would close drivers that other active
    sessions were still using, causing "Driver closed" errors.

    **SOLUTION:** Initialize once on first connection, never cleanup. Drivers
    remain open for the lifetime of the MCP server process.
    """
    global db, embedder, coll_mgr, searcher, doc_store
    global graph_store, unified_mediator, _initialized

    async with _init_lock:
        if _initialized:
            logger.debug("Components already initialized, reusing existing instances")
            return

        logger.info("First-time initialization of application components...")

        # Load configuration from YAML files before initializing components
        load_environment_variables()

        # Initialize RAG components (MANDATORY per Gap 2.1)
        logger.info("Initializing RAG components...")
        try:
            db = get_database()
            embedder = get_embedding_generator()
            coll_mgr = get_collection_manager(db)
            searcher = get_similarity_search(db, embedder, coll_mgr)
            doc_store = get_document_store(db, embedder, coll_mgr)
            logger.info("RAG components initialized successfully")
        except Exception as e:
            # FAIL-FAST per Gap 2.1 (Option B): PostgreSQL is mandatory
            logger.error(f"FATAL: RAG initialization failed (PostgreSQL unavailable): {e}")
            logger.error("Gap 2.1 (Option B: Mandatory Graph) requires both PostgreSQL and Neo4j to be operational.")
            logger.error("Please ensure PostgreSQL is running and accessible, then restart the server.")
            raise SystemExit(1)

        # Initialize Knowledge Graph components (MANDATORY per Gap 2.1, Option B: All or Nothing)
        logger.info("Initializing Knowledge Graph components...")
        try:
            from graphiti_core import Graphiti

            # Read Neo4j connection details from environment
            neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            neo4j_user = os.getenv("NEO4J_USER", "neo4j")
            neo4j_password = os.getenv("NEO4J_PASSWORD", "graphiti-password")

            graphiti = Graphiti(
                uri=neo4j_uri,
                user=neo4j_user,
                password=neo4j_password
            )

            graph_store = GraphStore(graphiti)
            unified_mediator = UnifiedIngestionMediator(db, embedder, coll_mgr, graph_store)
            logger.info("Knowledge Graph components initialized successfully")
        except Exception as e:
            # FAIL-FAST per Gap 2.1 (Option B): Knowledge Graph is mandatory
            logger.error(f"FATAL: Knowledge Graph initialization failed (Neo4j unavailable): {e}")
            logger.error("Gap 2.1 (Option B: Mandatory Graph) requires both PostgreSQL and Neo4j to be operational.")
            logger.error("Please ensure Neo4j is running and accessible, then restart the server.")
            raise SystemExit(1)

        # Validate PostgreSQL schema (only at first initialization)
        logger.info("Validating PostgreSQL schema...")
        try:
            pg_validation = await db.validate_schema()
            if pg_validation["status"] != "valid":
                logger.error("FATAL: PostgreSQL schema validation failed")
                for error in pg_validation["errors"]:
                    logger.error(f"  - {error}")
                raise SystemExit(1)
            logger.info(
                f"PostgreSQL schema valid ✓ "
                f"(tables: 3/3, pgvector: {'✓' if pg_validation['pgvector_loaded'] else '✗'}, "
                f"indexes: {pg_validation['hnsw_indexes']}/1)"
            )
        except SystemExit:
            raise
        except Exception as e:
            logger.error(f"FATAL: PostgreSQL schema validation error: {e}")
            raise SystemExit(1)

        # Validate Neo4j schema (only at first initialization)
        logger.info("Validating Neo4j schema...")
        try:
            graph_validation = await graph_store.validate_schema()
            if graph_validation["status"] != "valid":
                logger.error("FATAL: Neo4j schema validation failed")
                for error in graph_validation["errors"]:
                    logger.error(f"  - {error}")
                raise SystemExit(1)
            logger.info(
                f"Neo4j schema valid ✓ "
                f"(indexes: {graph_validation['indexes_found']}, queryable: "
                f"{'✓' if graph_validation['can_query_nodes'] else '✗'})"
            )
        except SystemExit:
            raise
        except Exception as e:
            logger.error(f"FATAL: Neo4j schema validation error: {e}")
            raise SystemExit(1)

        _initialized = True
        logger.info("All components initialized and validated - server ready ✓")


@asynccontextmanager
async def lifespan(app: FastMCP):
    """
    Lifespan context manager for MCP server.

    Ensures components are initialized when first SSE client connects.
    Does NOT clean up on disconnect - components persist for server lifetime.

    **BUG FIX:** Previously cleaned up drivers on session disconnect, causing
    "Driver closed" errors for other concurrent sessions. Now uses lazy singleton
    pattern via get_or_create_components().
    """
    # Initialize components on first connection (or reuse if already initialized)
    await get_or_create_components()

    yield {}  # Server runs here

    # NO CLEANUP - components persist for lifetime of MCP server process
    # This prevents "Driver closed" errors when multiple SSE sessions are active


# Load server instructions from file
_instructions_path = Path(__file__).parent / "server_instructions.txt"
_server_instructions = _instructions_path.read_text() if _instructions_path.exists() else None

# Initialize FastMCP server (no authentication)
mcp = FastMCP("rag-memory", instructions=_server_instructions, lifespan=lifespan)


# Add health check endpoint for Docker healthcheck
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> Response:
    """
    Health check endpoint that verifies PostgreSQL and Neo4j connectivity.

    If components aren't initialized yet (no MCP client has connected),
    returns healthy since the HTTP endpoint is responding.

    Once components are initialized, performs actual database health checks
    and returns detailed status for each database.

    Returns:
        200 OK: All databases healthy or not yet initialized
        503 Service Unavailable: One or more databases unhealthy
    """
    global db, graph_store, _initialized

    # If not initialized, just report HTTP is responding
    # Components initialize on first MCP client connection
    if not _initialized or db is None:
        return JSONResponse({
            "status": "healthy",
            "message": "MCP server ready, databases not yet initialized (awaiting first client connection)"
        })

    errors = []
    pg_status = {"status": "unknown"}
    neo_status = {"status": "unknown"}

    # Check PostgreSQL
    try:
        pg_status = await db.health_check()
        if pg_status.get("status") != "healthy":
            errors.append(f"PostgreSQL: {pg_status.get('error', 'unhealthy')}")
    except Exception as e:
        pg_status = {"status": "unhealthy", "error": str(e)}
        errors.append(f"PostgreSQL: {e}")

    # Check Neo4j (if graph store is available)
    if graph_store is not None:
        try:
            neo_status = await graph_store.health_check()
            # "unavailable" is acceptable (graph store disabled)
            if neo_status.get("status") not in ("healthy", "unavailable"):
                errors.append(f"Neo4j: {neo_status.get('error', 'unhealthy')}")
        except Exception as e:
            neo_status = {"status": "unhealthy", "error": str(e)}
            errors.append(f"Neo4j: {e}")
    else:
        neo_status = {"status": "unavailable", "message": "Graph store not initialized"}

    overall_status = "healthy" if not errors else "unhealthy"
    status_code = 200 if overall_status == "healthy" else 503

    return JSONResponse(
        {
            "status": overall_status,
            "postgres": pg_status,
            "neo4j": neo_status,
            "errors": errors if errors else None
        },
        status_code=status_code
    )


# Tool definitions (FastMCP auto-generates from type hints + docstrings)


@mcp.tool()
def search_documents(
    query: str,
    collection_name: str | None = None,
    limit: int = 5,
    threshold: float = 0.35,
    include_source: bool = False,
    include_metadata: bool = False,
    metadata_filter: dict | None = None,
) -> list[dict]:
    """
    Search for relevant document chunks by meaning.

    Results ranked by relevance (best first). Use natural language questions, not keywords.
    [Ref: Section 2 (query format guidance)]

    Args:
        query: (REQUIRED) Natural language question - complete sentences work best!
        collection_name: Optional - limit search to one collection. If None, searches all.
        limit: Maximum results to return (default: 5, max: 50)
        threshold: Min score 0-1 (default: 0.35). 0.60+=excellent, 0.4-0.6=good, 0.25-0.4=moderate, <0.25=weak.
                  None returns all ranked by relevance.
        include_source: If True, includes full source document content
        include_metadata: If True, includes chunk_id, chunk_index, char_start, char_end
        metadata_filter: Optional dict for filtering by custom metadata fields

    Returns:
        List of matching chunks ordered by relevance (best first).

        Minimal response (default):
        [
            {
                "content": str,  # Chunk content
                "similarity": float,  # 0-1 relevance score (higher = better match)
                "source_document_id": int,
                "source_filename": str,
                "source_content": str  # Only if include_source=True
            }
        ]

        Extended response (include_metadata=True):
        [
            {
                "content": str,
                "similarity": float,
                "source_document_id": int,
                "source_filename": str,
                "chunk_id": int,
                "chunk_index": int,
                "char_start": int,
                "char_end": int,
                "metadata": dict,
                "source_content": str  # Only if include_source=True
            }
        ]

    Example:
        # Basic search
        results = search_documents(
            query="How do I configure authentication?",
            collection_name="api-docs",
            limit=3
        )

        # With full details
        results = search_documents(
            query="How do I configure authentication?",
            collection_name="api-docs",
            limit=3,
            include_metadata=True
        )
    """
    return search_documents_impl(
        searcher, query, collection_name, limit, threshold, include_source, include_metadata, metadata_filter
    )


@mcp.tool()
def list_collections() -> list[dict]:
    """
    List all available document collections.

    Collections are named groups of documents (like folders for knowledge).
    Use this to discover what knowledge bases are available before searching.

    Returns:
        List of collections with metadata:
        [
            {
                "name": str,  # Collection identifier
                "description": str,  # Human-readable description
                "document_count": int,  # Number of source documents
                "created_at": str  # ISO 8601 timestamp
            }
        ]

    Example:
        collections = list_collections()
        # Find collection about Python
        python_colls = [c for c in collections if 'python' in c['name'].lower()]
    """
    return list_collections_impl(coll_mgr)


@mcp.tool()
def create_collection(
    name: str,
    description: str,
    domain: str,
    domain_scope: str,
    metadata_schema: dict | None = None
) -> dict:
    """
    Create a new collection for organizing documents by domain.

    **CRITICAL - Collection Discipline:**
    Collections partition BOTH vector search and knowledge graph. Create separate collections
    for different domains (e.g., "api-docs", "meeting-notes", "project-x") rather than mixing
    unrelated content. This ensures better search relevance and isolated knowledge graphs.

    Args:
        name: Collection identifier (unique, lowercase recommended)
        description: Human-readable purpose (REQUIRED, cannot be empty)
        domain: High-level category (e.g., "engineering", "finance")
        domain_scope: Scope description (e.g., "Internal API documentation")
        metadata_schema: Optional schema for custom fields. Format: {"custom": {"field": {"type": "string"}}}

    Returns:
        {"collection_id": int, "name": str, "description": str, "metadata_schema": dict, "created": bool}

    Best Practices [Ref: Collection Discipline]: One collection per domain; use clear descriptions; define schema upfront; check existing collections first

    Note: Free operation (no API calls).
    """
    return create_collection_impl(coll_mgr, name, description, domain, domain_scope, metadata_schema)


@mcp.tool()
def get_collection_metadata_schema(collection_name: str) -> dict:
    """
    Get metadata schema for a collection to discover required/optional fields before ingestion.

    Args:
        collection_name: Collection name

    Returns:
        {"collection_name": str, "description": str, "metadata_schema": dict,
         "custom_fields": dict, "system_fields": list, "document_count": int}

    Best Practices:
    - Use before ingesting to check required metadata fields
    - Helps avoid schema validation errors during ingest

    Note: Free operation (no API calls).
    """
    return get_collection_metadata_schema_impl(coll_mgr, collection_name)


@mcp.tool()
async def delete_collection(name: str, confirm: bool = False) -> dict:
    """
    Permanently delete a collection and all its documents.

    **⚠️ DESTRUCTIVE - Cannot be undone. Two-step confirmation required.**

    Workflow:
    1. Call with confirm=False (default) → Returns error requiring confirmation
    2. Review what will be deleted
    3. Call with confirm=True → Permanently deletes

    Args:
        name: Collection to delete (must exist)
        confirm: Must be True to proceed (default: False)

    Returns:
        {"name": str, "deleted": bool, "message": str}

    Best Practices [Ref: Collection Discipline]: Verify contents first; ensure no references; two-step confirmation prevents accidents

    Note: Free operation (deletes data, no API calls).
    """
    return await delete_collection_impl(coll_mgr, name, confirm, graph_store, db)


@mcp.tool()
def update_collection_metadata(
    collection_name: str,
    new_fields: dict
) -> dict:
    """
    Add new optional metadata fields to existing collection (additive only).

    **IMPORTANT:** Can only ADD fields, cannot remove or change types.

    Args:
        collection_name: Collection to update
        new_fields: New fields to add. Format: {"field": {"type": "string"}} or {"field": "string"}

    Returns:
        {"name": str, "description": str, "metadata_schema": dict,
         "fields_added": int, "total_fields": int}

    Best Practices:
    - All new fields automatically become optional
    - Existing documents won't have new fields until re-ingestion
    - Plan schema upfront to minimize updates

    Note: Free operation (no API calls).
    """
    return update_collection_metadata_impl(coll_mgr, collection_name, new_fields)


@mcp.tool()
async def ingest_text(
    content: str,
    collection_name: str,
    document_title: str | None = None,
    metadata: dict | None = None,
    include_chunk_ids: bool = False,
    mode: str = "ingest",
    context: Context | None = None,
) -> dict:
    """
    Ingest text content for semantic search and relationship analysis with automatic chunking.

    IMPORTANT: Collection must exist. Use create_collection() first.

    PAYLOAD LIMITS: Cloud clients ~1MB (~500K-1M chars). Split large content or use ingest_url()/ingest_file().
    TIMING: [Ref: Section 5 (timeout/duplicate protection)]

    Args:
        content: Text to ingest (any length, auto-chunked)
        collection_name: Target collection (must exist)
        document_title: Optional title (auto-generated if None)
        metadata: Optional metadata dict
        include_chunk_ids: If True, returns chunk IDs (default: False for minimal response)
        mode: "ingest" (new, errors if exists) or "reingest" (update, deletes old). Default: "ingest".

    Returns:
        {"source_document_id": int, "num_chunks": int, "collection_name": str,
         "chunk_ids": list (only if include_chunk_ids=True)}

    Best Practices [Ref: Ingestion Workflows]: Check duplicates first; use meaningful titles; add metadata for filtering

    Note: Uses AI models, has cost (semantic analysis and relationship extraction).
    """
    # Create progress callback wrapper if context available
    async def progress_callback(progress: float, total: float, message: str) -> None:
        if context:
            await context.report_progress(progress, total, message)

    result = await ingest_text_impl(
        db,
        doc_store,
        unified_mediator,
        graph_store,
        content,
        collection_name,
        document_title,
        metadata,
        include_chunk_ids,
        progress_callback=progress_callback if context else None,
        mode=mode,
    )

    # Progress: Complete
    if context:
        await context.report_progress(100, 100, "Ingestion complete!")

    return result


@mcp.tool()
def get_document_by_id(document_id: int, include_chunks: bool = False) -> dict:
    """
    Retrieve full document by ID (from search results).

    Args:
        document_id: Source document ID (from search_documents results)
        include_chunks: If True, includes chunk details (default: False)

    Returns:
        {"id": int, "filename": str, "content": str, "file_type": str, "file_size": int,
         "metadata": dict, "created_at": str, "updated_at": str,
         "chunks": list (only if include_chunks=True)}

    Best Practices:
    - Use when search chunk needs full document context
    - Document IDs come from search results (source_document_id field)

    Note: Free operation (no API calls).
    """
    return get_document_by_id_impl(doc_store, document_id, include_chunks)


@mcp.tool()
def get_collection_info(collection_name: str) -> dict:
    """
    Get detailed collection stats including crawled URLs history.

    **Use before ingesting** to check existing content and avoid duplicates.

    Args:
        collection_name: Collection name

    Returns:
        {"name": str, "description": str, "document_count": int, "chunk_count": int,
         "created_at": str, "sample_documents": list, "crawled_urls": list}

    Best Practices (see server instructions: Ingestion Workflows):
    - Check before ingesting to avoid duplicates
    - Review crawled_urls to see if website already ingested
    - Use sample_documents to verify collection content

    Note: Free operation (no API calls).
    """
    return get_collection_info_impl(db, coll_mgr, collection_name)


@mcp.tool()
async def analyze_website(
    base_url: str,
    timeout: int = 10,
    include_url_lists: bool = False,
    max_urls_per_pattern: int = 10
) -> dict:
    """
    Analyze website structure to discover URL patterns from sitemaps or Common Crawl index.

    Discovers URL patterns from public sources (sitemaps and search indexes). Returns up to 150 URLs
    grouped by path pattern. FREE operation (no AI models, just HTTP requests).

    50-second timeout. Check status field in response: "success", "timeout", "error", or "not_available".
    [Ref: Section 3 (workflow guidance)]

    Args:
        base_url: Website URL (root domain recommended for best results)
                 e.g., "https://docs.example.com" or "https://docs.example.com/api"
        timeout: DEPRECATED (ignored, actual timeout: 50s)
        include_url_lists: If True, includes full URL lists per pattern (default: False)
        max_urls_per_pattern: Max URLs per pattern when include_url_lists=True (default: 10)

    Returns:
        {
            "base_url": str,
            "status": str,  # "success", "timeout", "error", or "not_available"
            "total_urls": int,  # URLs discovered (1-150) or 0 if failed
            "url_patterns": int,  # Number of pattern groups
            "elapsed_seconds": float,
            "pattern_stats": {
                "/pattern": {
                    "count": int,
                    "avg_depth": float,
                    "example_urls": [str]
                }
            },
            "domains": [str],
            "notes": str,  # Summary or error details
            "url_groups": dict  # Only if include_url_lists=True
        }

    Example:
        analysis = analyze_website("https://docs.example.com")
        # Check analysis["status"] - "success", "timeout", or "error"

    Note: [Ref: Section 3 (workflow and usage guidance)]
    """
    return await analyze_website_impl(base_url, timeout, include_url_lists, max_urls_per_pattern)


@mcp.tool()
async def ingest_url(
    url: str,
    collection_name: str,
    mode: str = "ingest",
    follow_links: bool = False,
    max_pages: int = 10,
    analysis_token: str | None = None,
    metadata: dict | None = None,
    include_document_ids: bool = False,
    dry_run: bool = False,
    topic: str | None = None,
    context: Context | None = None,
) -> dict:
    """
    Ingest content from a web URL with duplicate prevention and optional dry run.

    IMPORTANT: Collection must exist before ingesting. Use create_collection() first.

    **Duplicate Prevention:**
    - mode="ingest": New ingest. ERROR if URL already ingested into collection.
    - mode="reingest": Update existing. Deletes old pages and re-ingests fresh content.

    **Dry Run & Timing:**
    [Ref: Section 3 (dry_run workflow), Section 5 (timeout/duplicate protection)]

    By default, returns minimal response without document_ids array (may be large for multi-page ingests).
    Use include_document_ids=True to get the list of document IDs.

    Args:
        url: (REQUIRED) URL to ingest (e.g., "https://docs.python.org/3/")
        collection_name: (REQUIRED) Collection to add content to (must already exist)
        mode: "ingest" (new, errors if exists) or "reingest" (update, deletes old). Default: "ingest".
        follow_links: If True, follows internal links for multi-page ingest (default: False).
                     If False, ingests only the single specified URL.
        max_pages: Maximum pages to ingest when follow_links=True (default: 10, max: 20).
                  Ingest stops after this many pages even if more links discovered.
        analysis_token: Optional. Deprecated parameter, no longer required. Kept for backward compatibility.
        metadata: Custom metadata to apply to ALL ingested pages (merged with page metadata).
                  Must match collection's metadata_schema if defined.
        include_document_ids: If True, includes list of document IDs. Default: False (minimal response).
        dry_run: If True, crawls pages but does NOT ingest them. Instead, returns relevance
                scores for each page based on the provided topic. Use this to preview what
                would be ingested and filter out irrelevant pages. Default: False.
        topic: REQUIRED when dry_run=True. Describes the content you're looking for.
               Examples: "LCEL pipelines in LangChain", "React hooks", "API authentication".
               The LLM uses this to score each page's relevance (0.0-1.0).

    Returns:
        **Normal mode (dry_run=False):**
        {
            "mode": str,
            "pages_crawled": int,
            "pages_ingested": int,
            "total_chunks": int,
            "collection_name": str,
            "crawl_metadata": {"crawl_root_url": str, "crawl_session_id": str, "crawl_timestamp": str},
            "pages_failed": [{"url": str, "status_code": int | null, "reason": str}],  # If any failed
            "old_pages_deleted": int,  # Only for mode="reingest"
            "document_ids": list[int]  # Only if include_document_ids=True
        }

        **Dry run mode (dry_run=True):**
        {
            "dry_run": true,
            "topic": str,  # The topic used for scoring
            "url": str,  # Starting URL
            "pages_crawled": int,
            "pages_recommended": int,  # Pages with recommendation="ingest"
            "pages_to_review": int,  # Pages with recommendation="review" (borderline)
            "pages_to_skip": int,  # Pages with recommendation="skip"
            "pages_failed": int,  # Count of pages with HTTP errors (404, 403, etc.)
            "collection_name": str,
            "pages": [
                {
                    "url": str,
                    "title": str,
                    "status_code": int | null,  # HTTP status code (200, 404, etc.)
                    "relevance_score": float | null,  # 0.0-1.0, or null for HTTP errors
                    "relevance_summary": str | null,  # Explanation, or null for HTTP errors
                    "recommendation": str,  # "ingest", "review", or "skip"
                    "reason": str  # Only present for HTTP errors (e.g., "Page not found")
                }
            ],
            "next_steps": str  # Guidance on what to do next
        }

        Recommendations: "ingest" (score ≥0.5), "review" (0.4-0.49), "skip" (<0.4 or HTTP error)

    Raises:
        ValueError: If collection doesn't exist, or if mode="ingest" and URL already
                   ingested into this collection. Error message suggests using
                   mode="reingest" to update.
        ValueError: If dry_run=True but topic is not provided.

    Example:
        # Single page
        result = ingest_url(url="https://example.com/docs", collection_name="docs")

        # Dry run workflow (see Section 3 for details)
        preview = ingest_url(url="https://example.com/docs", collection_name="docs",
                           follow_links=True, max_pages=20, dry_run=True,
                           topic="API authentication")

    Note: [Ref: Section 3 (dry_run workflow), Section 5 (timeout/duplicate protection)]
    """
    # Create progress callback wrapper if context available
    async def progress_callback(progress: float, total: float, message: str) -> None:
        if context:
            await context.report_progress(progress, total, message)

    result = await ingest_url_impl(
        db, doc_store, unified_mediator, graph_store, url, collection_name, follow_links, max_pages, analysis_token, mode, metadata, include_document_ids,
        progress_callback=progress_callback if context else None,
        dry_run=dry_run,
        topic=topic
    )

    # Progress: Complete (different message for dry run)
    if context:
        if dry_run:
            await context.report_progress(100, 100, f"Dry run complete! {result['pages_crawled']} pages scored")
        else:
            await context.report_progress(100, 100, f"Crawl complete! {result['pages_ingested']} pages ingested")

    return result


@mcp.tool()
async def ingest_file(
    file_path: str,
    collection_name: str,
    metadata: dict | None = None,
    include_chunk_ids: bool = False,
    mode: str = "ingest",
    context: Context | None = None,
) -> dict:
    """
    Ingest text-based file from file system (text/code/config only, not binary).

    FILESYSTEM: [Ref: Section 1.5]  |  TIMING: [Ref: Section 5 (timeout/duplicate protection)]

    Args:
        file_path: Absolute path ON THE MCP SERVER's filesystem (e.g., "/path/to/document.txt")
        collection_name: Target collection (must exist)
        metadata: Optional metadata dict
        include_chunk_ids: If True, returns chunk IDs (default: False)
        mode: "ingest" (new, errors if exists) or "reingest" (update, deletes old). Default: "ingest".

    Returns:
        {"source_document_id": int, "num_chunks": int, "filename": str, "file_type": str,
         "file_size": int, "collection_name": str, "chunk_ids": list (only if include_chunk_ids=True)}

    Best Practices [Ref: Ingestion Workflows]: Supports .txt/.md/code/.json/.yaml/.html (UTF-8 text); NOT PDF/Office/images/archives

    Note: Uses AI models, has cost (semantic analysis and relationship extraction).
    """
    # Create progress callback wrapper if context available
    async def progress_callback(progress: float, total: float, message: str) -> None:
        if context:
            await context.report_progress(progress, total, message)

    result = await ingest_file_impl(
        db, doc_store, unified_mediator, graph_store, file_path, collection_name, metadata, include_chunk_ids,
        progress_callback=progress_callback if context else None, mode=mode
    )

    # Progress: Complete
    if context:
        await context.report_progress(100, 100, f"File ingestion complete!")

    return result


@mcp.tool()
async def ingest_directory(
    directory_path: str,
    collection_name: str,
    file_extensions: list | None = None,
    recursive: bool = False,
    metadata: dict | None = None,
    include_document_ids: bool = False,
    mode: str = "ingest",
    context: Context | None = None,
) -> dict:
    """
    Batch ingest multiple text files from directory (text-based only, skips binary).

    DOMAIN: Mixed content? Create separate collections or use file_extensions to filter.
    FILESYSTEM: [Ref: Section 1.5]  |  TIMING: [Ref: Section 5 (timeout/duplicate protection)]

    Args:
        directory_path: Absolute path ON THE MCP SERVER's filesystem (e.g., "/path/to/docs")
        collection_name: Target collection (must exist)
        file_extensions: Extensions to process (default: [".txt", ".md"])
        recursive: If True, searches subdirectories (default: False)
        metadata: Metadata applied to ALL files (merged with file metadata)
        include_document_ids: If True, returns document IDs (default: False)
        mode: "ingest" (new, errors if exists) or "reingest" (update, deletes old). Default: "ingest".

    Returns:
        {"files_found": int, "files_ingested": int, "files_failed": int, "total_chunks": int,
         "collection_name": str, "failed_files": list, "document_ids": list (only if include_document_ids=True)}

    Best Practices [Ref: Collection Discipline]: Assess domain consistency; estimate scope before batch ingesting

    Note: Uses AI models, has cost (semantic analysis and relationship extraction per file).
    """
    # Create progress callback wrapper if context available
    async def progress_callback(progress: float, total: float, message: str) -> None:
        if context:
            await context.report_progress(progress, total, message)

    result = await ingest_directory_impl(
        db,
        doc_store,
        unified_mediator,
        graph_store,
        directory_path,
        collection_name,
        file_extensions,
        recursive,
        metadata,
        include_document_ids,
        progress_callback=progress_callback if context else None,
        mode=mode
    )

    # Progress: Complete
    if context:
        await context.report_progress(100, 100, f"Directory ingestion complete! {result['files_ingested']} files ingested")

    return result


@mcp.tool()
def list_directory(
    directory_path: str,
    file_extensions: list = None,
    recursive: bool = False,
    include_preview: bool = False,
    preview_chars: int = 500,
    max_files: int = 100,
) -> dict:
    """
    List files in a directory WITHOUT ingesting them. Use this to explore and assess directory contents
    before deciding what to ingest.

    READ-ONLY exploration tool for making informed decisions about which files to ingest.
    [Ref: Section 3 (recommended workflow)]

    FILESYSTEM: [Ref: Section 1.5 (constraints)]

    Args:
        directory_path: Absolute path to the directory to explore
        file_extensions: Filter by extensions, e.g., [".md", ".pdf", ".txt"].
                        If None, returns all files.
        recursive: If True, searches subdirectories recursively (default: False)
        include_preview: If True, includes first N characters of text-based files
                        for content assessment (default: False)
        preview_chars: Number of characters to include in preview (default: 500)
                      Only used if include_preview=True
        max_files: Maximum number of files to return (default: 100)
                  Prevents overwhelming output for large directories

    Returns:
        {
            "status": "success" or "error",
            "directory_path": str,
            "total_files_found": int,  # Total files matching criteria
            "files_returned": int,  # May be less than total if max_files exceeded
            "truncated": bool,  # True if results were limited by max_files
            "files": [
                {
                    "path": str,  # Absolute path for use with ingest_file
                    "filename": str,
                    "extension": str,
                    "size_bytes": int,
                    "size_human": str,  # e.g., "14.9 KB"
                    "modified": str,  # ISO 8601 timestamp
                    "preview": str  # Only if include_preview=True
                }
            ],
            "extensions_found": {".md": 8, ".pdf": 5},  # Summary by file type
            "error": str or null
        }

    Example:
        # Explore a directory before ingestion
        result = list_directory(
            directory_path="/docs/onboarding",
            file_extensions=[".md", ".pdf"],
            recursive=True,
            include_preview=True
        )
        # Result shows 15 files with previews
        # Agent can now assess relevance and recommend which to ingest

    Note: This is a FREE operation (no AI models, just filesystem access).
    """
    return list_directory_impl(
        directory_path=directory_path,
        file_extensions=file_extensions,
        recursive=recursive,
        include_preview=include_preview,
        preview_chars=preview_chars,
        max_files=max_files,
    )


@mcp.tool()
async def update_document(
    document_id: int,
    content: str | None = None,
    title: str | None = None,
    metadata: dict | None = None,
) -> dict:
    """
    Update existing document's content, title, or metadata (prevents duplicates).

    **IMPORTANT:** At least one field (content, title, or metadata) must be provided.

    Args:
        document_id: Document ID (from search results or list_documents)
        content: New content (triggers re-chunking and re-embedding)
        title: New title/filename
        metadata: New metadata (merged with existing, not replaced)

    Returns:
        {"document_id": int, "updated_fields": list, "old_chunk_count": int (if content updated),
         "new_chunk_count": int (if content updated)}

    Best Practices (see server instructions: Ingestion Workflows):
    - Essential for memory management (avoid duplicates)
    - Content updates trigger full re-chunking/re-embedding
    - Metadata is merged (to remove key, delete and re-ingest)

    Note: Content updates use AI models, has cost (embeddings + graph extraction).
    """
    return await update_document_impl(db, doc_store, document_id, content, title, metadata, graph_store)


@mcp.tool()
async def delete_document(document_id: int) -> dict:
    """
    Permanently delete document and all chunks (cannot be undone).

    **⚠️ PERMANENT - Essential for memory management** to remove outdated/incorrect knowledge.

    Args:
        document_id: Document ID (from search results or list_documents)

    Returns:
        {"document_id": int, "document_title": str, "chunks_deleted": int,
         "collections_affected": list (collections that had this document)}

    Best Practices:
    - Does NOT delete collections (only removes document from them)
    - Other documents in collections are unaffected
    - Use with caution - deletion is permanent

    Note: Free operation (no API calls, only database deletion).
    """
    return await delete_document_impl(db, doc_store, document_id, graph_store)


@mcp.tool()
def list_documents(
    collection_name: str | None = None,
    limit: int = 50,
    offset: int = 0,
    include_details: bool = False,
) -> dict:
    """
    Browse documents in knowledge base (supports pagination).

    Args:
        collection_name: Filter by collection (if None, lists all)
        limit: Max documents to return (default: 50, max: 200)
        offset: Documents to skip for pagination (default: 0)
        include_details: If True, includes file_type, file_size, timestamps, collections, metadata (default: False)

    Returns:
        {"documents": list, "total_count": int, "returned_count": int, "has_more": bool}
        Each document: {"id": int, "filename": str, "chunk_count": int, ... (more if include_details=True)}

    Best Practices:
    - Discover documents before updating/deleting
    - Use pagination (has_more) for large collections
    - Default minimal response recommended for browsing

    Note: Free operation (no API calls).
    """
    return list_documents_impl(doc_store, collection_name, limit, offset, include_details)


# =============================================================================
# Knowledge Graph Query Tools
# =============================================================================


@mcp.tool()
async def query_relationships(
    query: str,
    collection_name: str | None = None,
    num_results: int = 5,
    threshold: float = 0.35,
) -> dict:
    """
    Query knowledge graph for entity relationships using natural language.

    **Best for:** "How" questions about connections (e.g., "How does X relate to Y?")

    Args:
        query: Natural language query (e.g., "How does my content strategy support my business?")
        collection_name: Scope to collection (if None, searches all)
        num_results: Max relationships to return (default: 5, max: 20)
        threshold: Relevance filter 0.0-1.0 (default: 0.35, higher = stricter)

    Returns:
        {"status": str, "query": str, "num_results": int, "relationships": list}
        Each relationship: {"id": str, "relationship_type": str, "fact": str, "source_node_id": str,
                           "target_node_id": str, "valid_from": str, "valid_until": str}

    Best Practices (see server instructions: Knowledge Graph):
    - Collection scoping isolates domains (same as search_documents)
    - Returns status="unavailable" if graph not enabled
    - Performance: ~500-800ms (includes LLM entity matching)

    Note: Uses AI models, has cost (LLM for entity matching).
    """
    return await query_relationships_impl(
        graph_store,
        query,
        collection_name,
        num_results,
        threshold=threshold,
    )


@mcp.tool()
async def query_temporal(
    query: str,
    collection_name: str | None = None,
    num_results: int = 10,
    threshold: float = 0.35,
    valid_from: str | None = None,
    valid_until: str | None = None,
) -> dict:
    """
    Query how knowledge evolved over time (temporal reasoning on facts).

    **Best for:** Evolution queries (e.g., "How has my business strategy changed?")

    Args:
        query: Natural language query (e.g., "How has my business vision evolved?")
        collection_name: Scope to collection (if None, searches all)
        num_results: Max timeline items to return (default: 10, max: 50)
        threshold: Relevance filter 0.0-1.0 (default: 0.35, higher = stricter)
        valid_from: ISO 8601 date (return facts valid AFTER this date)
        valid_until: ISO 8601 date (return facts valid BEFORE this date)

    Returns:
        {"status": str, "query": str, "num_results": int, "timeline": list (sorted by valid_from, recent first)}
        Each item: {"fact": str, "relationship_type": str, "valid_from": str, "valid_until": str,
                   "status": str ("current" or "superseded"), "created_at": str, "expired_at": str}

    Best Practices (see server instructions: Knowledge Graph):
    - Tracks current vs superseded knowledge
    - Temporal filters can be combined for time windows
    - Returns status="unavailable" if graph not enabled
    - Performance: ~500-800ms (includes LLM temporal matching)

    Note: Uses AI models, has cost (LLM for temporal matching).
    """
    return await query_temporal_impl(
        graph_store,
        query,
        collection_name,
        num_results,
        threshold=threshold,
        valid_from=valid_from,
        valid_until=valid_until,
    )


def main():
    """Run the MCP server with specified transport."""
    import sys
    import asyncio
    import click

    # Configure logging when server starts (not at module import)
    configure_logging()

    @click.command()
    @click.option(
        "--port",
        default=3001,
        help="Port to listen on for SSE or Streamable HTTP transport"
    )
    @click.option(
        "--transport",
        type=click.Choice(["stdio", "sse", "streamable-http"]),
        default="stdio",
        help="Transport type (stdio, sse, or streamable-http)"
    )
    def run_cli(port: int, transport: str):
        """Run the RAG memory MCP server with specified transport."""
        # Ensure all required configuration is set up before starting
        ensure_config_or_exit()

        async def run_server():
            """Inner async function to run the server and manage the event loop."""
            try:
                if transport == "stdio":
                    logger.info("Starting server with STDIO transport")
                    await mcp.run_stdio_async()
                elif transport == "sse":
                    logger.info(f"Starting server with SSE transport on port {port}")
                    mcp.settings.host = "0.0.0.0"
                    mcp.settings.port = port
                    await mcp.run_sse_async()
                elif transport == "streamable-http":
                    logger.info(f"Starting server with Streamable HTTP transport on port {port}")
                    mcp.settings.port = port
                    mcp.settings.streamable_http_path = "/mcp"
                    await mcp.run_streamable_http_async()
                else:
                    raise ValueError(f"Unknown transport: {transport}")
            except KeyboardInterrupt:
                logger.info("Server stopped by user")
            except Exception as e:
                logger.error(f"Failed to start server: {e}", exc_info=True)
                raise

        try:
            asyncio.run(run_server())
        except KeyboardInterrupt:
            logger.info("Server interrupted")
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise

    run_cli()


def main_stdio():
    """Run MCP server in stdio mode (for Claude Desktop/Cursor)."""
    import sys
    sys.argv = ['rag-mcp-stdio', '--transport', 'stdio']
    main()


def main_sse():
    """Run MCP server in SSE mode (for MCP Inspector)."""
    import sys
    sys.argv = ['rag-mcp-sse', '--transport', 'sse', '--port', '3001']
    main()


def main_http():
    """Run MCP server in HTTP mode (for web integrations)."""
    import sys
    sys.argv = ['rag-mcp-http', '--transport', 'streamable-http', '--port', '3001']
    main()


if __name__ == "__main__":
    main()
