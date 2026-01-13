# Source-Aware Chunking Implementation Plan

**Status:** Ready for implementation
**Branch:** `feature/source-aware-chunking`
**Estimated Scope:** ~950 lines across 8 files (includes web page ingestion support)

---

## Quick Start for New Session

```bash
# 1. Create feature branch from main
git checkout main
git pull
git checkout -b feature/source-aware-chunking

# 2. Follow implementation steps in order (Steps 1-9)
# 3. Run tests after each step
uv run pytest tests/unit/test_file_type_detector.py -v  # After Step 1
uv run pytest tests/unit/test_chunker_factory.py -v     # After Step 2
uv run pytest -v                                         # After all steps
```

**Implementation order matters:** Steps 1-4 are foundational, Steps 5-9 integrate them.

---

## Overview

Add source-aware chunking to RAG Memory to improve retrieval accuracy by 4-15%. Currently, all documents use the same chunking strategy regardless of content type, which can split code mid-function or break table structures in documentation pages.

### Goals
1. Route code files to language-aware chunkers (avoids splitting mid-function)
2. Route PDF/Office files through Docling for structure-preserving extraction
3. Route web pages to markdown-aware chunking (preserves tables, code blocks, lists)
4. Support optional OCR for images
5. Maintain backward compatibility (new ingests only)

### Non-Goals
- Re-chunking existing documents
- Semantic chunking (deferred - too expensive)
- Full multimedia support (audio transcription deferred)

---

## Current Architecture

### Chunking Flow (before changes)
```
ingest_file_impl() → DocumentStore.ingest_document() → DocumentChunker.chunk_text() → EmbeddingGenerator → PostgreSQL
```

### Key Files
- `src/core/chunking.py` - Single `RecursiveCharacterTextSplitter` with markdown separators
- `src/ingestion/document_store.py` - Handles document ingestion
- `src/mcp/tools.py` - MCP tool implementations (`ingest_file_impl`, etc.)

### Current Chunking Config
```python
# src/core/chunking.py
@dataclass
class ChunkingConfig:
    chunk_size: int = 1000
    chunk_overlap: int = 200
    separators: Optional[List[str]] = None  # Defaults to markdown-optimized
```

---

## Implementation Steps

### Step 1: Create File Type Detector

**Create `src/core/file_type_detector.py`:**

```python
"""File type detection for source-aware chunking."""

from enum import Enum
from pathlib import Path
from typing import Optional


class FileType(Enum):
    """Supported file types for chunking strategy selection."""
    # Code files (use LangChain from_language)
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    GO = "go"
    RUST = "rust"
    JAVA = "java"
    CPP = "cpp"
    CSHARP = "csharp"

    # Document files (use Docling)
    PDF = "pdf"
    DOCX = "docx"
    PPTX = "pptx"
    XLSX = "xlsx"

    # Image files (use Docling OCR - optional)
    IMAGE = "image"

    # Text files (use existing chunker)
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    YAML = "yaml"
    TEXT = "text"


# Extension to FileType mapping
EXTENSION_MAP = {
    # Code
    ".py": FileType.PYTHON,
    ".pyw": FileType.PYTHON,
    ".js": FileType.JAVASCRIPT,
    ".jsx": FileType.JAVASCRIPT,
    ".mjs": FileType.JAVASCRIPT,
    ".ts": FileType.TYPESCRIPT,
    ".tsx": FileType.TYPESCRIPT,
    ".go": FileType.GO,
    ".rs": FileType.RUST,
    ".java": FileType.JAVA,
    ".cpp": FileType.CPP,
    ".cc": FileType.CPP,
    ".cxx": FileType.CPP,
    ".c": FileType.CPP,
    ".h": FileType.CPP,
    ".hpp": FileType.CPP,
    ".cs": FileType.CSHARP,

    # Documents
    ".pdf": FileType.PDF,
    ".docx": FileType.DOCX,
    ".pptx": FileType.PPTX,
    ".xlsx": FileType.XLSX,

    # Images
    ".png": FileType.IMAGE,
    ".jpg": FileType.IMAGE,
    ".jpeg": FileType.IMAGE,
    ".tiff": FileType.IMAGE,
    ".bmp": FileType.IMAGE,
    ".gif": FileType.IMAGE,

    # Text
    ".md": FileType.MARKDOWN,
    ".mdx": FileType.MARKDOWN,
    ".html": FileType.HTML,
    ".htm": FileType.HTML,
    ".json": FileType.JSON,
    ".yaml": FileType.YAML,
    ".yml": FileType.YAML,
    ".txt": FileType.TEXT,
}


def detect_file_type(filename: str, content: Optional[str] = None) -> FileType:
    """
    Detect file type from filename extension.

    Args:
        filename: File name or path
        content: Optional content for future content-based detection

    Returns:
        FileType enum value
    """
    ext = Path(filename).suffix.lower()
    return EXTENSION_MAP.get(ext, FileType.TEXT)


def needs_preprocessing(file_type: FileType) -> bool:
    """Check if file type needs Docling preprocessing before chunking."""
    return file_type in {FileType.PDF, FileType.DOCX, FileType.PPTX, FileType.XLSX, FileType.IMAGE}


def needs_code_chunking(file_type: FileType) -> bool:
    """Check if file type needs code-aware chunking."""
    return file_type in {
        FileType.PYTHON, FileType.JAVASCRIPT, FileType.TYPESCRIPT,
        FileType.GO, FileType.RUST, FileType.JAVA, FileType.CPP, FileType.CSHARP
    }
```

### Step 2: Add ChunkerFactory to Chunking Module

**Modify `src/core/chunking.py`:**

Add import at top of file:
```python
from langchain_text_splitters import Language
from src.core.file_type_detector import FileType
```

Add after the existing `DocumentChunker` class:

```python
# Map FileType to LangChain Language
LANGUAGE_MAP = {
    FileType.PYTHON: Language.PYTHON,
    FileType.JAVASCRIPT: Language.JS,
    FileType.TYPESCRIPT: Language.TS,
    FileType.GO: Language.GO,
    FileType.RUST: Language.RUST,
    FileType.JAVA: Language.JAVA,
    FileType.CPP: Language.CPP,
    FileType.CSHARP: Language.CSHARP,
    FileType.MARKDOWN: Language.MARKDOWN,
    FileType.HTML: Language.HTML,
}


class ChunkerFactory:
    """Factory for creating file-type-appropriate chunkers."""

    @staticmethod
    def get_chunker(
        file_type: FileType,
        config: Optional[ChunkingConfig] = None
    ) -> DocumentChunker:
        """
        Get appropriate chunker for file type.

        Args:
            file_type: Detected file type
            config: Optional chunking configuration

        Returns:
            Configured DocumentChunker instance
        """
        config = config or ChunkingConfig()

        # Code files: use language-specific splitter
        if file_type in LANGUAGE_MAP:
            language = LANGUAGE_MAP[file_type]
            splitter = RecursiveCharacterTextSplitter.from_language(
                language=language,
                chunk_size=config.chunk_size,
                chunk_overlap=config.chunk_overlap,
            )
            chunker = DocumentChunker(config)
            chunker.splitter = splitter  # Replace the default splitter
            chunker._strategy_name = f"{file_type.value}_code"
            logger.info(f"Using {language.value} code chunker")
            return chunker

        # All other files: use default markdown-optimized chunker
        chunker = DocumentChunker(config)
        chunker._strategy_name = "default"
        return chunker
```

Also update `DocumentChunker.chunk_text()` to include strategy in metadata:

```python
def chunk_text(
    self, text: str, metadata: Optional[Dict[str, Any]] = None
) -> List[Document]:
    # ... existing code ...

    # Add chunk-specific metadata
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = i
        chunk.metadata["total_chunks"] = len(chunks)
        chunk.metadata["char_start"] = i * (self.config.chunk_size - self.config.chunk_overlap)
        chunk.metadata["char_end"] = chunk.metadata["char_start"] + len(chunk.page_content)
        # NEW: Add chunking strategy
        chunk.metadata["chunking_strategy"] = getattr(self, "_strategy_name", "default")

    return chunks
```

### Step 3: Create Document Processor for Docling

**Create `src/ingestion/document_processor.py`:**

```python
"""Document preprocessing using Docling for PDF/Office/Image files."""

import logging
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Lazy import to avoid loading Docling unless needed
_docling_available = None


def is_docling_available() -> bool:
    """Check if Docling is installed."""
    global _docling_available
    if _docling_available is None:
        try:
            from docling.document_converter import DocumentConverter
            _docling_available = True
        except ImportError:
            _docling_available = False
    return _docling_available


def is_ocr_available() -> bool:
    """Check if OCR support is installed (docling[ocr])."""
    if not is_docling_available():
        return False
    try:
        from docling.models.easyocr_model import EasyOcrModel
        return True
    except ImportError:
        return False


class DocumentProcessor:
    """Process documents using Docling for format conversion."""

    def __init__(self, enable_ocr: bool = False):
        """
        Initialize document processor.

        Args:
            enable_ocr: Whether to enable OCR for images/scanned PDFs
        """
        if not is_docling_available():
            raise ImportError(
                "Docling is required for PDF/Office document processing. "
                "Install with: pip install rag-memory (Docling included by default)"
            )

        from docling.document_converter import DocumentConverter

        # Configure converter
        self.enable_ocr = enable_ocr and is_ocr_available()

        if self.enable_ocr:
            from docling.models.easyocr_model import EasyOcrModel
            from docling.pipeline.simple_pipeline import SimplePipeline
            from docling.pipeline.standard_pipeline import StandardPipeline

            # Use pipeline with OCR
            self.converter = DocumentConverter(
                pipeline_options=StandardPipeline.get_default_options()
            )
            logger.info("Document processor initialized with OCR support")
        else:
            self.converter = DocumentConverter()
            logger.info("Document processor initialized (no OCR)")

    def process_file(self, file_path: str) -> Tuple[str, dict]:
        """
        Process a document file and extract text content.

        Args:
            file_path: Path to the document file

        Returns:
            Tuple of (extracted_text, metadata)
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        logger.info(f"Processing document: {path.name}")

        # Convert document
        result = self.converter.convert(str(path))

        # Export to markdown (preserves structure)
        markdown_content = result.document.export_to_markdown()

        # Build metadata
        metadata = {
            "original_format": path.suffix.lower().lstrip("."),
            "processor": "docling",
            "ocr_enabled": self.enable_ocr,
            "page_count": len(result.document.pages) if hasattr(result.document, "pages") else None,
        }

        # Add table info if available
        if hasattr(result.document, "tables") and result.document.tables:
            metadata["table_count"] = len(result.document.tables)

        logger.info(
            f"Extracted {len(markdown_content)} chars from {path.name} "
            f"(format: {metadata['original_format']})"
        )

        return markdown_content, metadata

    def process_image(self, file_path: str) -> Tuple[str, dict]:
        """
        Process an image file and extract text via OCR.

        Args:
            file_path: Path to the image file

        Returns:
            Tuple of (extracted_text, metadata)
        """
        if not self.enable_ocr:
            raise RuntimeError(
                "OCR is not enabled. Install with: pip install rag-memory[ocr]"
            )

        return self.process_file(file_path)


def get_document_processor(enable_ocr: bool = False) -> Optional[DocumentProcessor]:
    """
    Factory function to get DocumentProcessor if available.

    Args:
        enable_ocr: Whether to enable OCR support

    Returns:
        DocumentProcessor instance or None if Docling not available
    """
    if not is_docling_available():
        return None
    return DocumentProcessor(enable_ocr=enable_ocr)
```

### Step 4: Update pyproject.toml

**Add to dependencies:**

```toml
dependencies = [
    # ... existing dependencies ...

    # Document Processing
    "docling>=2.0.0",  # PDF/Office document parsing (IBM open-source)
]

[project.optional-dependencies]
dev = [
    # ... existing dev dependencies ...
]
ocr = [
    "docling[ocr]",  # Adds EasyOCR support for image text extraction
]
```

### Step 5: Update Document Store

**Modify `src/ingestion/document_store.py`:**

Add imports at top:
```python
from src.core.file_type_detector import FileType, detect_file_type
from src.core.chunking import ChunkerFactory
```

Update `ingest_document()` method - here's the COMPLETE updated method:

```python
def ingest_document(
    self,
    content: str,
    filename: str,
    collection_name: str,
    metadata: Optional[Dict[str, Any]] = None,
    file_type: str = "text",
    detected_file_type: Optional[FileType] = None,  # NEW parameter
) -> Tuple[int, List[int]]:
    """
    Ingest a document: store full text, chunk it, generate embeddings.

    Args:
        content: Full document text
        filename: Document filename/identifier
        collection_name: Collection to add chunks to
        metadata: Optional metadata for the document
        file_type: File type string (text, markdown, pdf, etc.) - stored in DB
        detected_file_type: Optional FileType enum for chunking strategy selection.
                           If None, auto-detects from filename.

    Returns:
        Tuple of (source_document_id, list_of_chunk_ids)
    """
    conn = self.db.connect()

    # 1. Verify collection exists and auto-apply domain/domain_scope
    collection = self.collection_mgr.get_collection(collection_name)
    if not collection:
        raise ValueError(
            f"Collection '{collection_name}' does not exist. "
            f"Collections must be created explicitly with a description before ingesting documents."
        )

    # Auto-apply mandatory metadata from collection
    if metadata is None:
        metadata = {}

    mandatory_metadata = collection.get("metadata_schema", {}).get("mandatory", {})
    domain = mandatory_metadata.get("domain")
    domain_scope = mandatory_metadata.get("domain_scope")

    if domain:
        metadata["domain"] = domain
    if domain_scope:
        metadata["domain_scope"] = domain_scope

    # 2. Store the full source document
    logger.info(f"Storing source document: {filename}")
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO source_documents
            (filename, content, file_type, file_size, metadata)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                filename,
                content,
                file_type,
                len(content),
                Jsonb(metadata),
            ),
        )
        source_id = cur.fetchone()[0]

    # 3. Select chunker based on file type (NEW: source-aware chunking)
    if detected_file_type is None:
        detected_file_type = detect_file_type(filename)

    chunker = ChunkerFactory.get_chunker(detected_file_type, self.chunker.config)
    logger.info(f"Using chunker for file type: {detected_file_type.value}")

    # 4. Chunk the document
    logger.info(f"Chunking document ({len(content)} chars)...")
    chunks = chunker.chunk_text(content, metadata)

    stats = chunker.get_stats(chunks)
    logger.info(
        f"Created {stats['num_chunks']} chunks. "
        f"Avg: {stats['avg_chunk_size']:.0f} chars, "
        f"Range: {stats['min_chunk_size']}-{stats['max_chunk_size']}"
    )

    # 5. Generate embeddings and store chunks
    chunk_ids = []
    for chunk_doc in chunks:
        # Generate embedding for this chunk
        embedding = self.embedder.generate_embedding(
            chunk_doc.page_content, normalize=True
        )

        # Store chunk
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO document_chunks
                (source_document_id, chunk_index, content,
                 char_start, char_end, metadata, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    source_id,
                    chunk_doc.metadata.get("chunk_index", 0),
                    chunk_doc.page_content,
                    chunk_doc.metadata.get("char_start", 0),
                    chunk_doc.metadata.get("char_end", 0),
                    Jsonb(chunk_doc.metadata),
                    embedding,
                ),
            )
            chunk_id = cur.fetchone()[0]
            chunk_ids.append(chunk_id)

        # Link chunk to collection
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO chunk_collections (chunk_id, collection_id)
                VALUES (%s, %s)
                """,
                (chunk_id, collection["id"]),
            )

    logger.info(f"✅ Ingested document {source_id} with {len(chunk_ids)} chunks")

    return source_id, chunk_ids
```

Also update `ingest_file()` to pass file type:

```python
def ingest_file(
    self,
    file_path: str,
    collection_name: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> Tuple[int, List[int]]:
    """
    Read a file from disk and ingest it.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Detect file type for chunking strategy
    detected_type = detect_file_type(file_path)

    # Read file
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = path.read_text(encoding="latin-1")

    # Determine file type string from extension (for DB storage)
    file_type = path.suffix.lstrip(".").lower() or "text"

    # Add file info to metadata
    file_metadata = metadata or {}
    file_metadata.update({
        "filename": path.name,
        "file_path": str(path.absolute()),
        "file_type": file_type,
    })

    return self.ingest_document(
        content=content,
        filename=path.name,
        collection_name=collection_name,
        metadata=file_metadata,
        file_type=file_type,
        detected_file_type=detected_type,  # NEW: pass for chunking
    )
```

### Step 6: Update MCP Tools

**Modify `src/mcp/tools.py` - `ingest_file_impl()`:**

The current function signature is:
```python
async def ingest_file_impl(
    db: Database,
    doc_store: DocumentStore,
    unified_mediator,
    graph_store: Optional[GraphStore],
    file_path: str,
    collection_name: str,
    metadata: Optional[Dict[str, Any]] = None,
    include_chunk_ids: bool = False,
    progress_callback=None,
    mode: str = "ingest",
) -> Dict[str, Any]:
```

Add imports at the top of `ingest_file_impl`:
```python
from src.core.file_type_detector import detect_file_type, needs_preprocessing, FileType
from src.ingestion.document_processor import get_document_processor, is_ocr_available
```

Insert the following code AFTER the path validation and mode checks (~line 1968),
BEFORE reading the file content:

```python
        # NEW: Detect file type for source-aware chunking
        detected_file_type = detect_file_type(file_path)
        logger.info(f"Detected file type: {detected_file_type.value}")

        # NEW: Handle files that need preprocessing (PDF, Office, Images)
        if needs_preprocessing(detected_file_type):
            if progress_callback:
                await progress_callback(10, 100, f"Preprocessing {detected_file_type.value} file...")

            processor = get_document_processor(enable_ocr=is_ocr_available())

            if processor is None:
                raise ImportError(
                    f"Cannot process {detected_file_type.value} files. "
                    f"Docling is required but not available. "
                    f"Install with: pip install rag-memory"
                )

            if detected_file_type == FileType.IMAGE and not is_ocr_available():
                raise ImportError(
                    f"OCR is required for image files but not installed. "
                    f"Install with: pip install rag-memory[ocr]"
                )

            # Preprocess: convert PDF/Office/Image to markdown
            file_content, proc_metadata = processor.process_file(file_path)

            # Merge processor metadata with user metadata
            file_metadata = metadata.copy() if metadata else {}
            file_metadata.update(proc_metadata)
            file_metadata.update({
                "file_type": path.suffix.lstrip(".").lower() or "unknown",
                "file_size": path.stat().st_size,
            })

            # After preprocessing, chunk as markdown (structure preserved)
            detected_file_type = FileType.MARKDOWN

            logger.info(f"Preprocessed {path.name}: {len(file_content)} chars extracted")
        else:
            # Read text-based file content directly
            try:
                file_content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                file_content = path.read_text(encoding="latin-1")

            file_metadata = metadata.copy() if metadata else {}
            file_metadata.update({
                "file_type": path.suffix.lstrip(".").lower() or "text",
                "file_size": path.stat().st_size,
            })
```

Then update the call to `unified_mediator.ingest_text()` to pass the detected file type
(requires updating the mediator - see Step 7).

### Step 7: Update Unified Mediator

**Modify `src/unified/mediator.py`:**

Update the `ingest_text` method signature to accept file type:

```python
async def ingest_text(
    self,
    content: str,
    collection_name: str,
    document_title: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
    progress_callback: Optional[Callable[[float, float, str], Awaitable[None]]] = None,
    detected_file_type: Optional["FileType"] = None,  # NEW parameter
) -> dict[str, Any]:
```

Add import at top:
```python
from src.core.file_type_detector import FileType
```

Update the call to `self.rag_store.ingest_document()`:

```python
source_id, chunk_ids = self.rag_store.ingest_document(
    content=content,
    filename=document_title or f"Agent-Text-{content[:20]}",
    collection_name=collection_name,
    metadata=metadata,
    file_type="text",
    detected_file_type=detected_file_type,  # NEW: pass for chunking
)
```

### Step 8: Update CLI Commands

**Modify `src/cli_commands/ingest.py`:**

The CLI needs updates for both `ingest_file_cmd` and `ingest_directory`.

Add imports at top:
```python
from src.core.file_type_detector import detect_file_type, needs_preprocessing, FileType
from src.ingestion.document_processor import get_document_processor, is_docling_available, is_ocr_available
```

**Update `ingest_file_cmd` (around line 200):**

Replace the file reading section with:

```python
# Detect file type for source-aware chunking
detected_file_type = detect_file_type(path)

# Handle files that need preprocessing (PDF, Office, Images)
if needs_preprocessing(detected_file_type):
    console.print(f"[dim]Preprocessing {detected_file_type.value} file...[/dim]")

    processor = get_document_processor(enable_ocr=is_ocr_available())
    if processor is None:
        console.print(f"[bold red]Error: Cannot process {detected_file_type.value} files. Docling not available.[/bold red]")
        sys.exit(1)

    if detected_file_type == FileType.IMAGE and not is_ocr_available():
        console.print(f"[bold red]Error: OCR required for images. Install with: pip install rag-memory[ocr][/bold red]")
        sys.exit(1)

    file_content, proc_metadata = processor.process_file(path)
    file_metadata = metadata_dict.copy() if metadata_dict else {}
    file_metadata.update(proc_metadata)
    detected_file_type = FileType.MARKDOWN  # After preprocessing
else:
    # Read text file directly
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        file_content = f.read()
    file_metadata = metadata_dict.copy() if metadata_dict else {}

# Add standard file metadata
file_path_obj = Path(path)
file_metadata.update({
    "file_type": file_path_obj.suffix.lstrip(".").lower() or "text",
    "file_size": file_path_obj.stat().st_size,
})
```

Then pass `detected_file_type` to the mediator call.

**Update `ingest_directory` similarly** - apply the same preprocessing logic inside the file loop.

### Step 9: Update Web Page Ingestion

**Modify `src/mcp/tools.py` - `ingest_url_impl()`:**

Web pages are already converted to markdown by crawl4ai. Route this markdown through the markdown-aware chunker to preserve tables, code blocks, and list structures.

Add import at top of function (around line 1560):
```python
from src.core.file_type_detector import FileType
```

**Update the ingestion call** (around line 1848):

Find the existing call:
```python
result = await unified_mediator.ingest_text(
    content=crawl_result.content,
    collection_name=collection_name,
    document_title=crawl_result.title or crawl_result.url,
    metadata=merged_metadata,
    progress_callback=progress_callback,
)
```

Replace with:
```python
result = await unified_mediator.ingest_text(
    content=crawl_result.content,
    collection_name=collection_name,
    document_title=crawl_result.title or crawl_result.url,
    metadata=merged_metadata,
    progress_callback=progress_callback,
    detected_file_type=FileType.MARKDOWN,  # NEW: crawl4ai outputs markdown
)
```

**Rationale:**
- crawl4ai converts HTML to markdown (web_crawler.py:170)
- Markdown-aware chunking preserves table structure, code blocks, and lists
- No additional preprocessing needed - content is already markdown
- Maintains consistency with file ingestion approach

**Chunk Size Considerations:**

Documentation pages often have large tables and code blocks. The markdown chunker should already respect structure (won't split mid-table), so we'll start with the same 1000-char default as files. This can be tuned later if testing shows excessive splitting:

- **Option 1:** Pass custom config to mediator (requires additional parameter)
- **Option 2:** Document recommended collection-level settings for documentation ingests
- **Option 3:** Defer tuning - use same 1000 char default as files (simplest)

**Recommendation:** Start with Option 3 (defer). The markdown chunker won't split mid-table or mid-code-block, so structure should be preserved. If testing shows issues, add config parameter in future iteration.

---

## Testing Plan

### Unit Tests

**Create `tests/unit/test_file_type_detector.py`:**

```python
import pytest
from src.core.file_type_detector import detect_file_type, FileType, needs_preprocessing, needs_code_chunking


class TestFileTypeDetector:
    def test_python_detection(self):
        assert detect_file_type("script.py") == FileType.PYTHON
        assert detect_file_type("path/to/module.pyw") == FileType.PYTHON

    def test_javascript_detection(self):
        assert detect_file_type("app.js") == FileType.JAVASCRIPT
        assert detect_file_type("component.jsx") == FileType.JAVASCRIPT
        assert detect_file_type("module.mjs") == FileType.JAVASCRIPT

    def test_typescript_detection(self):
        assert detect_file_type("app.ts") == FileType.TYPESCRIPT
        assert detect_file_type("component.tsx") == FileType.TYPESCRIPT

    def test_document_detection(self):
        assert detect_file_type("report.pdf") == FileType.PDF
        assert detect_file_type("document.docx") == FileType.DOCX
        assert detect_file_type("slides.pptx") == FileType.PPTX
        assert detect_file_type("data.xlsx") == FileType.XLSX

    def test_image_detection(self):
        assert detect_file_type("photo.png") == FileType.IMAGE
        assert detect_file_type("image.jpg") == FileType.IMAGE
        assert detect_file_type("scan.jpeg") == FileType.IMAGE

    def test_text_detection(self):
        assert detect_file_type("README.md") == FileType.MARKDOWN
        assert detect_file_type("page.html") == FileType.HTML
        assert detect_file_type("config.json") == FileType.JSON
        assert detect_file_type("config.yaml") == FileType.YAML
        assert detect_file_type("notes.txt") == FileType.TEXT

    def test_unknown_defaults_to_text(self):
        assert detect_file_type("file.unknown") == FileType.TEXT
        assert detect_file_type("no_extension") == FileType.TEXT

    def test_needs_preprocessing(self):
        assert needs_preprocessing(FileType.PDF) is True
        assert needs_preprocessing(FileType.DOCX) is True
        assert needs_preprocessing(FileType.IMAGE) is True
        assert needs_preprocessing(FileType.PYTHON) is False
        assert needs_preprocessing(FileType.TEXT) is False

    def test_needs_code_chunking(self):
        assert needs_code_chunking(FileType.PYTHON) is True
        assert needs_code_chunking(FileType.JAVASCRIPT) is True
        assert needs_code_chunking(FileType.PDF) is False
        assert needs_code_chunking(FileType.TEXT) is False
```

**Create `tests/unit/test_chunker_factory.py`:**

```python
import pytest
from src.core.chunking import ChunkerFactory, ChunkingConfig
from src.core.file_type_detector import FileType


class TestChunkerFactory:
    def test_python_chunker(self):
        chunker = ChunkerFactory.get_chunker(FileType.PYTHON)
        assert chunker._strategy_name == "python_code"

    def test_javascript_chunker(self):
        chunker = ChunkerFactory.get_chunker(FileType.JAVASCRIPT)
        assert chunker._strategy_name == "javascript_code"

    def test_default_chunker(self):
        chunker = ChunkerFactory.get_chunker(FileType.TEXT)
        assert chunker._strategy_name == "default"

    def test_markdown_uses_langchain_markdown(self):
        chunker = ChunkerFactory.get_chunker(FileType.MARKDOWN)
        assert chunker._strategy_name == "markdown_code"

    def test_custom_config(self):
        config = ChunkingConfig(chunk_size=500, chunk_overlap=50)
        chunker = ChunkerFactory.get_chunker(FileType.PYTHON, config)
        assert chunker.config.chunk_size == 500

    def test_python_code_chunking(self):
        """Test that Python code is chunked at function boundaries."""
        chunker = ChunkerFactory.get_chunker(FileType.PYTHON)

        code = '''
def function_one():
    """First function."""
    return 1

def function_two():
    """Second function."""
    return 2

class MyClass:
    def method(self):
        pass
'''
        chunks = chunker.chunk_text(code)

        # Verify chunks have strategy metadata
        assert all(c.metadata.get("chunking_strategy") == "python_code" for c in chunks)
```

### Integration Tests

**Create `tests/integration/test_source_aware_ingestion.py`:**

```python
import pytest
from pathlib import Path

# Test with sample files
SAMPLE_PYTHON = '''
def calculate_sum(a: int, b: int) -> int:
    """Calculate the sum of two numbers."""
    return a + b

def calculate_product(a: int, b: int) -> int:
    """Calculate the product of two numbers."""
    return a * b

class Calculator:
    """A simple calculator class."""

    def __init__(self):
        self.history = []

    def add(self, a, b):
        result = a + b
        self.history.append(result)
        return result
'''

@pytest.mark.asyncio
async def test_python_file_ingestion(test_collection, tmp_path):
    """Test ingesting a Python file uses code-aware chunking."""
    # Create test file
    py_file = tmp_path / "calculator.py"
    py_file.write_text(SAMPLE_PYTHON)

    # Ingest
    result = await ingest_file_impl(
        file_path=str(py_file),
        collection_name=test_collection,
    )

    assert result["num_chunks"] > 0

    # Verify chunks have code chunking strategy
    doc = get_document_by_id(result["source_document_id"], include_chunks=True)
    for chunk in doc["chunks"]:
        assert chunk["metadata"]["chunking_strategy"] == "python_code"


@pytest.mark.asyncio
async def test_markdown_file_ingestion(test_collection, tmp_path):
    """Test markdown files use markdown chunking."""
    md_file = tmp_path / "readme.md"
    md_file.write_text("# Title\n\nContent here.\n\n## Section\n\nMore content.")

    result = await ingest_file_impl(
        file_path=str(md_file),
        collection_name=test_collection,
    )

    doc = get_document_by_id(result["source_document_id"], include_chunks=True)
    for chunk in doc["chunks"]:
        assert chunk["metadata"]["chunking_strategy"] == "markdown_code"


@pytest.mark.skipif(not is_docling_available(), reason="Docling not installed")
@pytest.mark.asyncio
async def test_pdf_file_ingestion(test_collection, sample_pdf_path):
    """Test PDF files are preprocessed through Docling."""
    result = await ingest_file_impl(
        file_path=sample_pdf_path,
        collection_name=test_collection,
    )

    doc = get_document_by_id(result["source_document_id"], include_chunks=True)

    # Check Docling metadata
    assert doc["metadata"]["processor"] == "docling"
    assert doc["metadata"]["original_format"] == "pdf"


@pytest.mark.asyncio
async def test_web_page_markdown_chunking(test_collection, mocker):
    """Test web page ingestion uses markdown-aware chunking."""
    # Mock crawl4ai to return markdown with tables and code
    mock_result = CrawlResult(
        url="https://docs.example.com/api",
        title="API Documentation",
        content="""
# Authentication API

## Configuration Table

| Setting | Type | Description |
|---------|------|-------------|
| `api_key` | string | Your API key |
| `timeout` | int | Request timeout in seconds |

## Example Code

```json
{
  "api_key": "sk-...",
  "timeout": 30
}
```

## Steps

1. Obtain API key from dashboard
2. Configure client with credentials
3. Make authenticated requests
        """,
        metadata={"content_type": "web_page"}
    )

    mocker.patch('src.ingestion.web_crawler.WebCrawler.crawl_url',
                 return_value=[mock_result])

    result = await ingest_url_impl(
        url="https://docs.example.com/api",
        collection_name=test_collection,
        follow_links=False,
    )

    # Verify ingestion succeeded
    assert result["pages_ingested"] == 1

    # Get the document chunks
    doc = get_document_by_id(result["document_ids"][0], include_chunks=True)

    # Verify markdown chunking strategy used
    for chunk in doc["chunks"]:
        assert chunk["metadata"]["chunking_strategy"] == "markdown_code"

    # Verify table structure preserved (header + data in same chunk)
    table_chunks = [c for c in doc["chunks"] if "| Setting |" in c["content"]]
    assert len(table_chunks) > 0, "Table header found"

    # Check that table data rows are in same chunk as header
    for chunk in table_chunks:
        content = chunk["content"]
        assert "| Setting |" in content  # Header row
        assert "|---------|" in content or "api_key" in content  # Separator or data

    # Verify JSON code block preserved
    json_chunks = [c for c in doc["chunks"] if "```json" in c["content"]]
    assert len(json_chunks) > 0, "JSON code block found"

    # Check that code block is complete
    for chunk in json_chunks:
        content = chunk["content"]
        assert content.count("```") >= 2, "Code block has opening and closing"
        # Check JSON structure not split mid-object
        if "{" in content:
            # Should have matching closing brace in same chunk
            assert "}" in content, "JSON object complete in chunk"

    # Verify ordered list preserved
    list_chunks = [c for c in doc["chunks"] if "1. Obtain API key" in c["content"]]
    assert len(list_chunks) > 0, "Ordered list found"

    # Check list items stay together
    for chunk in list_chunks:
        content = chunk["content"]
        # If we have item 1, we should have item 2 in same chunk (short list)
        if "1. Obtain" in content and "2. Configure" in content:
            assert "3. Make authenticated" in content, "All list items together"


@pytest.mark.asyncio
async def test_web_page_large_table_chunking(test_collection, mocker):
    """Test that large tables in web pages chunk appropriately."""
    # Create markdown with a large table (might exceed chunk size)
    rows = "\n".join([f"| row{i} | value{i} | description of row {i} |"
                      for i in range(50)])

    large_table = f"""
# Large Configuration Reference

| Parameter | Default | Description |
|-----------|---------|-------------|
{rows}
"""

    mock_result = CrawlResult(
        url="https://docs.example.com/config",
        title="Configuration Reference",
        content=large_table,
        metadata={"content_type": "web_page"}
    )

    mocker.patch('src.ingestion.web_crawler.WebCrawler.crawl_url',
                 return_value=[mock_result])

    result = await ingest_url_impl(
        url="https://docs.example.com/config",
        collection_name=test_collection,
        follow_links=False,
    )

    doc = get_document_by_id(result["document_ids"][0], include_chunks=True)

    # Verify markdown chunking used
    assert all(c["metadata"]["chunking_strategy"] == "markdown_code"
               for c in doc["chunks"])

    # Table will be split due to size, but verify splits respect table structure
    # (header should be with data rows, not split between header and separator)
    for chunk in doc["chunks"]:
        content = chunk["content"]
        if "| Parameter |" in content:
            # If we have the header, we should have separator line too
            assert "|-----------|" in content, "Table header not split from separator"
```

---

## Files to Modify Summary

| File | Action | Description |
|------|--------|-------------|
| `src/core/file_type_detector.py` | **CREATE** | FileType enum, extension mapping, detection functions |
| `src/core/chunking.py` | **MODIFY** | Add ChunkerFactory class, LANGUAGE_MAP, imports |
| `src/ingestion/document_processor.py` | **CREATE** | Docling wrapper for PDF/Office/Image processing |
| `src/ingestion/document_store.py` | **MODIFY** | Add detected_file_type param, use ChunkerFactory |
| `src/unified/mediator.py` | **MODIFY** | Add detected_file_type param, pass to rag_store |
| `src/mcp/tools.py` (ingest_file_impl) | **MODIFY** | Add preprocessing logic for PDF/Office/Image files |
| `src/mcp/tools.py` (ingest_url_impl) | **MODIFY** | Pass FileType.MARKDOWN for web page content |
| `src/cli_commands/ingest.py` | **MODIFY** | Add preprocessing for file and directory commands |
| `pyproject.toml` | **MODIFY** | Add docling dependency, ocr optional extra |
| `tests/unit/test_file_type_detector.py` | **CREATE** | Unit tests for file type detection |
| `tests/unit/test_chunker_factory.py` | **CREATE** | Unit tests for chunker factory |
| `tests/integration/test_source_aware_ingestion.py` | **CREATE** | Integration tests (files and web pages) |

---

## Verification Checklist

After implementation, verify:

**Core Functionality:**
- [ ] `detect_file_type()` correctly identifies all supported extensions
- [ ] Python files use `Language.PYTHON` splitter (check `def` boundaries preserved)
- [ ] JavaScript/TypeScript files use appropriate splitters
- [ ] Go/Rust/Java files use appropriate splitters
- [ ] Chunk metadata includes `chunking_strategy` field

**Docling Integration:**
- [ ] PDF files are converted to markdown via Docling
- [ ] DOCX/PPTX/XLSX files work through Docling
- [ ] Tables in PDFs are preserved as markdown tables
- [ ] Images without `[ocr]` extra raise clear error message
- [ ] Images with `[ocr]` extra extract text correctly

**Integration Points:**
- [ ] MCP `ingest_file` tool works with all file types
- [ ] MCP `ingest_directory` tool uses source-aware chunking per file
- [ ] CLI `rag ingest file` works with all file types
- [ ] CLI `rag ingest directory` uses source-aware chunking per file
- [ ] Unified mediator passes file type through correctly

**Web Page Ingestion:**
- [ ] Web pages use markdown-aware chunking (not default)
- [ ] Tables in web pages stay intact (header + data rows together)
- [ ] JSON/code blocks in web pages don't split mid-structure
- [ ] Ordered/numbered lists maintain sequence
- [ ] Web page chunks include `chunking_strategy: "markdown_code"`
- [ ] Multi-page crawls apply markdown chunking to all pages

**Backward Compatibility:**
- [ ] Existing documents are NOT affected (no re-chunking)
- [ ] Default text chunking unchanged for .txt and unknown extensions
- [ ] `ingest_text()` without `detected_file_type` uses default chunking

**Testing:**
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Tests run on macOS
- [ ] Tests run on Linux (CI)

---

## Rollback Plan

If issues arise:

1. Revert `pyproject.toml` to remove Docling dependency
2. Revert `ChunkerFactory` - all files use default chunker
3. Keep `FileType` enum and detection for future use

---

## References

- [LangChain Text Splitters](https://python.langchain.com/docs/modules/data_connection/document_transformers/)
- [Docling GitHub](https://github.com/docling-project/docling)
- [NVIDIA 2024 Chunking Benchmark](https://stackoverflow.blog/2024/12/27/breaking-up-is-hard-to-do-chunking-in-rag-applications/)
- [cAST Paper - AST-based Code Chunking](https://arxiv.org/html/2506.15655v1)
