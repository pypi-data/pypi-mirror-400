#!/usr/bin/env python3
"""
MCP Token Counter - Analyze token consumption of RAG Memory MCP server.

This script analyzes the token usage of the MCP server by:
1. Counting tokens in server instructions (server_instructions.txt)
2. Extracting all @mcp.tool() functions from server.py
3. Counting tokens for each tool's signature and docstring
4. Generating detailed reports (console + markdown file)

Usage:
    python scripts/analyze_mcp_tokens.py
"""

import ast
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import tiktoken
except ImportError:
    print("Error: tiktoken not installed. Run: pip install tiktoken")
    sys.exit(1)


# Tool categorization mapping
TOOL_CATEGORIES = {
    "Ingestion": ["ingest_text", "ingest_file", "ingest_directory", "ingest_url", "analyze_website"],
    "Search": ["search_documents"],
    "Query": ["query_relationships", "query_temporal"],
    "Collection Management": [
        "list_collections",
        "create_collection",
        "delete_collection",
        "get_collection_metadata_schema",
        "update_collection_metadata",
    ],
    "Document Management": [
        "get_document_by_id",
        "update_document",
        "delete_document",
        "list_documents",
        "get_collection_info",
        "list_directory",
    ],
}


class MCPTokenCounter:
    """Analyze and report token consumption of MCP server."""

    def __init__(self):
        """Initialize token counter with tiktoken encoding."""
        self.encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
        self.base_path = Path(__file__).parent.parent
        self.server_py = self.base_path / "src/mcp/server.py"
        self.instructions = self.base_path / "src/mcp/server_instructions.txt"

        # Validate files exist
        if not self.server_py.exists():
            raise FileNotFoundError(f"server.py not found at: {self.server_py}")
        if not self.instructions.exists():
            raise FileNotFoundError(f"server_instructions.txt not found at: {self.instructions}")

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken."""
        return len(self.encoding.encode(text))

    def extract_mcp_tools(self) -> List[Dict]:
        """
        Extract all @mcp.tool() decorated functions from server.py using AST.

        Returns:
            List of tool metadata dicts with name, signature, docstring, tokens, etc.
        """
        # Read server.py
        server_code = self.server_py.read_text()
        tree = ast.parse(server_code)

        tools = []

        for node in ast.walk(tree):
            # Find function definitions (both sync and async)
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue

            # Check if function has @mcp.tool() decorator
            has_mcp_decorator = False
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Call):
                    if isinstance(decorator.func, ast.Attribute):
                        if decorator.func.attr == "tool":
                            has_mcp_decorator = True
                            break

            if not has_mcp_decorator:
                continue

            # Extract function details
            func_name = node.name
            is_async = isinstance(node, ast.AsyncFunctionDef)

            # Get docstring
            docstring = ast.get_docstring(node) or ""

            # Reconstruct signature (simplified - just get param info)
            params = []
            for arg in node.args.args:
                # Get parameter name
                param_name = arg.arg
                # Get type annotation if present
                if arg.annotation:
                    type_str = ast.unparse(arg.annotation)
                    params.append(f"{param_name}: {type_str}")
                else:
                    params.append(param_name)

            # Build signature string
            async_prefix = "async " if is_async else ""
            signature = f"{async_prefix}def {func_name}({', '.join(params)})"

            # Count tokens
            sig_tokens = self.count_tokens(signature)
            doc_tokens = self.count_tokens(docstring)
            total_tokens = sig_tokens + doc_tokens

            tools.append(
                {
                    "name": func_name,
                    "signature": signature,
                    "docstring": docstring,
                    "is_async": is_async,
                    "param_count": len(params),
                    "tokens": {"signature": sig_tokens, "docstring": doc_tokens, "total": total_tokens},
                }
            )

        return sorted(tools, key=lambda x: x["tokens"]["total"], reverse=True)

    def categorize_tools(self, tools: List[Dict]) -> Dict[str, List[Dict]]:
        """Group tools by category."""
        categorized = {category: [] for category in TOOL_CATEGORIES.keys()}

        for tool in tools:
            tool_name = tool["name"]
            # Find which category this tool belongs to
            for category, tool_names in TOOL_CATEGORIES.items():
                if tool_name in tool_names:
                    categorized[category].append(tool)
                    break

        return categorized

    def analyze(self) -> Dict:
        """
        Analyze MCP server token usage.

        Returns:
            Dict with all analysis data: tools, categories, totals, etc.
        """
        # Read server instructions
        instructions_text = self.instructions.read_text()
        instructions_tokens = self.count_tokens(instructions_text)

        # Extract and analyze tools
        tools = self.extract_mcp_tools()
        categorized = self.categorize_tools(tools)

        # Calculate totals
        total_tool_tokens = sum(t["tokens"]["total"] for t in tools)
        total_system_tokens = instructions_tokens + total_tool_tokens

        # Category totals
        category_totals = {}
        for category, cat_tools in categorized.items():
            category_totals[category] = sum(t["tokens"]["total"] for t in cat_tools)

        return {
            "instructions_tokens": instructions_tokens,
            "tools": tools,
            "categorized": categorized,
            "category_totals": category_totals,
            "total_tool_tokens": total_tool_tokens,
            "total_system_tokens": total_system_tokens,
            "tool_count": len(tools),
        }

    def create_ascii_bar(self, percentage: float, width: int = 20) -> str:
        """Create ASCII bar chart."""
        filled = int(percentage * width / 100)
        empty = width - filled
        return "█" * filled + "░" * empty

    def generate_console_report(self, data: Dict):
        """Generate and print formatted console report."""
        print("\n" + "═" * 75)
        print("║" + "  RAG Memory MCP Server - Token Analysis Report".center(73) + "║")
        print("═" * 75 + "\n")

        # System Overview
        print("📊 SYSTEM OVERVIEW")
        print("━" * 75)
        print(f"Server Instructions:        {data['instructions_tokens']:>6,} tokens")
        print(f"Tool Schemas ({data['tool_count']} tools):   {data['total_tool_tokens']:>6,} tokens")
        print("─" * 75)
        print(f"TOTAL CONTEXT:             {data['total_system_tokens']:>6,} tokens")

        # Context window utilization (Claude 4.5 models)
        claude_context = 200000  # Claude 4.5 Opus/Sonnet standard context window
        utilization = (data["total_system_tokens"] / claude_context) * 100
        print(f"Claude 4.5 Utilization:     {utilization:>6.1f}% of 200K window")
        print()

        # Per-tool breakdown
        print("📋 PER-TOOL TOKEN BREAKDOWN (sorted by total tokens)")
        print("━" * 75)
        print(
            f"{'#':<3} {'Tool Name':<30} {'Sig':<6} {'Doc':<7} {'Total':<7} {'%':<6}"
        )
        print("─" * 75)

        for i, tool in enumerate(data["tools"][:10], 1):  # Top 10
            name = tool["name"][:28]  # Truncate long names
            sig = tool["tokens"]["signature"]
            doc = tool["tokens"]["docstring"]
            total = tool["tokens"]["total"]
            pct = (total / data["total_tool_tokens"]) * 100

            print(f"{i:<3} {name:<30} {sig:<6} {doc:<7,} {total:<7,} {pct:>5.1f}%")

        if len(data["tools"]) > 10:
            print(f"... and {len(data['tools']) - 10} more tools")

        print()

        # Top 5 most expensive
        print("🏆 TOP 5 MOST TOKEN-EXPENSIVE TOOLS")
        print("━" * 75)

        for i, tool in enumerate(data["tools"][:5], 1):
            name = tool["name"]
            tokens = tool["tokens"]["total"]
            pct = (tokens / data["total_tool_tokens"]) * 100
            bar = self.create_ascii_bar(pct, width=30)

            print(f"{i}. {name:<25} {tokens:>5,} tokens  {bar} {pct:>5.1f}%")

        print()

        # Category breakdown
        print("📁 CATEGORY BREAKDOWN")
        print("━" * 75)

        for category, total in sorted(
            data["category_totals"].items(), key=lambda x: x[1], reverse=True
        ):
            tool_count = len(data["categorized"][category])
            pct = (total / data["total_tool_tokens"]) * 100
            bar = self.create_ascii_bar(pct, width=30)

            print(f"{category:<25} ({tool_count}): {total:>5,} tokens  {pct:>4.1f}%  {bar}")

        print()

        # Insights
        print("💡 INSIGHTS")
        print("━" * 75)

        # Context utilization insight
        if utilization < 20:
            print(f"✓ Total context fits well within Claude 4.5 200K window ({utilization:.1f}% utilization)")
        elif utilization < 50:
            print(f"⚠ Moderate context usage ({utilization:.1f}% of Claude 4.5 200K window)")
        else:
            print(f"⚠ High context usage ({utilization:.1f}% of Claude 4.5 200K window)")

        # Most expensive category
        top_category = max(data["category_totals"].items(), key=lambda x: x[1])
        cat_pct = (top_category[1] / data["total_tool_tokens"]) * 100
        print(f"✓ {top_category[0]} tools account for {cat_pct:.1f}% of tool token usage")

        # Most expensive tool
        top_tool = data["tools"][0]
        tool_pct = (top_tool["tokens"]["total"] / data["total_tool_tokens"]) * 100
        if tool_pct > 15:
            print(f"⚠ {top_tool['name']} alone uses {tool_pct:.1f}% of total tool context")
            print(f"→ Largest single tool - consider if all examples/details are needed")

        print()

    def generate_markdown_report(self, data: Dict) -> str:
        """Generate markdown report."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        md = []
        md.append("# RAG Memory MCP Server - Token Analysis Report\n")
        md.append(f"**Generated:** {timestamp}\n")
        md.append("---\n")

        # Executive Summary
        md.append("## Executive Summary\n")
        md.append(f"- **Total System Context**: {data['total_system_tokens']:,} tokens\n")
        md.append(f"- **Server Instructions**: {data['instructions_tokens']:,} tokens\n")
        md.append(f"- **Tool Schemas**: {data['total_tool_tokens']:,} tokens ({data['tool_count']} tools)\n")

        avg_per_tool = data["total_tool_tokens"] / data["tool_count"]
        md.append(f"- **Average per tool**: {avg_per_tool:.0f} tokens\n")

        claude_context = 200000  # Claude 4.5 Opus/Sonnet standard context
        utilization = (data["total_system_tokens"] / claude_context) * 100
        md.append(f"- **Claude 4.5 200K Utilization**: {utilization:.1f}%\n")
        md.append(f"- **Note**: 1M token context available in beta for Sonnet 4.5 (tier 4 API users)\n")
        md.append("\n")

        # Per-Tool Breakdown
        md.append("## Per-Tool Token Breakdown\n")
        md.append("| # | Tool Name | Signature | Docstring | Total | % of Tools |\n")
        md.append("|---|-----------|-----------|-----------|-------|------------|\n")

        for i, tool in enumerate(data["tools"], 1):
            name = tool["name"]
            sig = tool["tokens"]["signature"]
            doc = tool["tokens"]["docstring"]
            total = tool["tokens"]["total"]
            pct = (total / data["total_tool_tokens"]) * 100

            md.append(f"| {i} | {name} | {sig} | {doc:,} | {total:,} | {pct:.1f}% |\n")

        md.append("\n")

        # Top 5
        md.append("## Top 5 Most Token-Expensive Tools\n\n")
        for i, tool in enumerate(data["tools"][:5], 1):
            tokens = tool["tokens"]["total"]
            pct = (tokens / data["total_tool_tokens"]) * 100
            md.append(f"{i}. **{tool['name']}** - {tokens:,} tokens ({pct:.1f}%)\n")

        md.append("\n")

        # Category Analysis
        md.append("## Category Analysis\n\n")

        for category, cat_tools in sorted(
            data["categorized"].items(), key=lambda x: data["category_totals"][x[0]], reverse=True
        ):
            total = data["category_totals"][category]
            if total == 0:
                continue

            pct = (total / data["total_tool_tokens"]) * 100
            md.append(f"### {category} ({len(cat_tools)} tools, {total:,} tokens, {pct:.1f}%)\n\n")

            for tool in cat_tools:
                tokens = tool["tokens"]["total"]
                md.append(f"- **{tool['name']}**: {tokens:,} tokens\n")

            md.append("\n")

        # Detailed Tool Information
        md.append("## Detailed Tool Information\n\n")

        for tool in data["tools"]:
            md.append(f"### {tool['name']}\n\n")
            md.append(f"- **Type**: {'Async' if tool['is_async'] else 'Sync'}\n")
            md.append(f"- **Parameters**: {tool['param_count']}\n")
            md.append(f"- **Signature tokens**: {tool['tokens']['signature']}\n")
            md.append(f"- **Docstring tokens**: {tool['tokens']['docstring']:,}\n")
            md.append(f"- **Total tokens**: {tool['tokens']['total']:,}\n")
            md.append(f"\n**Signature:**\n```python\n{tool['signature']}\n```\n\n")

        return "".join(md)

    def save_markdown_report(self, markdown: str) -> Path:
        """Save markdown report to file."""
        # Create reports directory
        reports_dir = self.base_path / "reports"
        reports_dir.mkdir(exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_file = reports_dir / f"mcp_token_analysis_{timestamp}.md"

        # Write file
        report_file.write_text(markdown)

        return report_file


def main():
    """Run token analysis and generate reports."""
    try:
        counter = MCPTokenCounter()
        print("Analyzing MCP server token usage...")

        # Perform analysis
        data = counter.analyze()

        # Generate console report
        counter.generate_console_report(data)

        # Generate and save markdown report
        markdown = counter.generate_markdown_report(data)
        report_file = counter.save_markdown_report(markdown)

        print(f"📄 Detailed report saved to: {report_file.relative_to(counter.base_path)}")
        print()

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
