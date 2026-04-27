"""
Phase 1: Knowledge Ingestion & Vectorization — Main Pipeline
=============================================================
Orchestrates the full Phase 1 pipeline:
  1. Load & crawl all 8 source URLs from sources.md
  2. Split content into chunks (500 chars, 50 overlap)
  3. Store in ChromaDB vector database with source metadata
  4. Run a verification query to confirm everything works

Usage:
    cd "Phase 1"
    python ingest.py
"""

import os
import sys
import json
import time

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.rule import Rule

from source_loader import load_all_sources
from text_splitter import split_documents
from vector_store import store_chunks, query_store

console = Console()


def run_pipeline():
    """Execute the full Phase 1 ingestion pipeline."""

    console.print(Panel.fit(
        "[bold white]Phase 1: Knowledge Ingestion & Vectorization[/bold white]\n"
        "[dim]Groww MF FAQ Assistant — RAG Pipeline[/dim]",
        border_style="cyan",
        padding=(1, 4),
    ))

    start_time = time.time()

    # ── Step 1: Load Sources ─────────────────────────────────────────────
    console.print(Rule("[bold cyan]Step 1: Source Loading[/bold cyan]"))
    console.print("[dim]Crawling 8 official HDFC/AMFI URLs from sources.md...[/dim]\n")

    sources_path = os.path.join(os.path.dirname(__file__), "..", "sources.md")
    documents = load_all_sources(sources_path)

    if not documents:
        console.print("[bold red]✗ No documents loaded. Aborting pipeline.[/bold red]")
        sys.exit(1)

    # ── Step 2: Text Splitting ───────────────────────────────────────────
    console.print(Rule("[bold cyan]Step 2: Text Splitting[/bold cyan]"))
    console.print("[dim]Recursive Character Splitter — chunk_size=500, overlap=50[/dim]\n")

    chunks = split_documents(documents)

    if not chunks:
        console.print("[bold red]✗ No chunks generated. Aborting pipeline.[/bold red]")
        sys.exit(1)

    # ── Step 3: Vector Store Ingestion ───────────────────────────────────
    console.print(Rule("[bold cyan]Step 3: Vector Store Ingestion[/bold cyan]"))
    console.print("[dim]Storing chunks in ChromaDB with source metadata...[/dim]\n")

    stats = store_chunks(chunks, reset=True)

    # ── Step 4: Verification ─────────────────────────────────────────────
    console.print(Rule("[bold cyan]Step 4: Verification[/bold cyan]"))
    console.print("[dim]Running test queries to confirm retrieval works...[/dim]\n")

    test_queries = [
        "What is the exit load for HDFC Top 100 Fund?",
        "What is the minimum SIP amount?",
        "What is the lock-in period for ELSS?",
    ]

    for query in test_queries:
        console.print(f"\n[bold yellow]Q:[/bold yellow] {query}")
        results = query_store(query, n_results=3)

        if results:
            for i, r in enumerate(results, 1):
                console.print(
                    f"  [green]{i}.[/green] [{r['metadata']['scheme']}] "
                    f"(dist: {r['distance']:.4f})"
                )
                preview = r["content"][:150].replace("\n", " ")
                console.print(f"     [dim]{preview}...[/dim]")
                console.print(f"     [blue]📎 {r['metadata']['source_url']}[/blue]")
        else:
            console.print("  [red]No results found[/red]")

    # ── Summary ──────────────────────────────────────────────────────────
    elapsed = time.time() - start_time

    console.print(Rule("[bold green]Pipeline Complete[/bold green]"))

    summary_table = Table(title="Phase 1 — Ingestion Summary", show_header=True)
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="green")

    summary_table.add_row("Sources crawled", str(len(documents)))
    summary_table.add_row("Total chunks", str(stats["total_chunks"]))
    summary_table.add_row("Avg chunk size",
                          f"{sum(len(c['content']) for c in chunks) / len(chunks):.0f} chars")
    summary_table.add_row("Vector DB location", stats["persist_dir"])
    summary_table.add_row("Collection name", stats["collection_name"])
    summary_table.add_row("Time elapsed", f"{elapsed:.1f}s")

    console.print(summary_table)

    # Save ingestion report as JSON
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "sources_crawled": len(documents),
        "total_chunks": stats["total_chunks"],
        "avg_chunk_size": round(sum(len(c['content']) for c in chunks) / len(chunks)),
        "documents": [
            {
                "id": d["id"],
                "scheme": d["scheme"],
                "doc_type": d["doc_type"],
                "url": d["url"],
                "content_length": len(d["content"]),
            }
            for d in documents
        ],
        "chunks_per_source": {},
    }

    for chunk in chunks:
        scheme = chunk["scheme"]
        report["chunks_per_source"][scheme] = report["chunks_per_source"].get(scheme, 0) + 1

    report_path = os.path.join(os.path.dirname(__file__), "ingestion_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    console.print(f"\n[dim]📄 Report saved to: {report_path}[/dim]")
    console.print("[bold green]✅ Phase 1 complete. Knowledge base is ready for Phase 2.[/bold green]\n")


if __name__ == "__main__":
    run_pipeline()
