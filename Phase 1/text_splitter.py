"""
Text Splitter Module
====================
Implements a Recursive Character Text Splitter as specified in the architecture:
  - Chunk Size: 500 characters
  - Chunk Overlap: 50 characters

Each chunk retains full metadata (source URL, scheme name, doc type) for citation.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter
from rich.console import Console

console = Console()

# ── Architecture-specified settings ──────────────────────────────────────────
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
SEPARATORS = ["\n\n", "\n", ". ", ", ", " ", ""]


def create_splitter() -> RecursiveCharacterTextSplitter:
    """Create a RecursiveCharacterTextSplitter with the architecture settings."""
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=SEPARATORS,
        length_function=len,
        is_separator_regex=False,
    )


def split_documents(documents: list[dict]) -> list[dict]:
    """
    Split a list of loaded documents into smaller chunks, preserving metadata.

    Input: list of dicts from source_loader.load_all_sources()
        [{ "id", "scheme", "doc_type", "url", "content" }, ...]

    Output: list of dicts
        [{
            "chunk_id": "src_1_chunk_0",
            "source_id": 1,
            "scheme": "HDFC Top 100",
            "doc_type": "SID (Exit Load/Fees)",
            "source_url": "https://...",
            "content": "... chunk text ...",
            "chunk_index": 0,
            "total_chunks": N,
        }, ...]
    """
    splitter = create_splitter()
    all_chunks = []

    for doc in documents:
        # Split the content into chunks
        text_chunks = splitter.split_text(doc["content"])

        console.print(
            f"  [cyan]✂[/cyan]  {doc['scheme']}: "
            f"[dim]{len(doc['content']):,} chars → {len(text_chunks)} chunks[/dim]"
        )

        for i, chunk_text in enumerate(text_chunks):
            all_chunks.append({
                "chunk_id": f"src_{doc['id']}_chunk_{i}",
                "source_id": doc["id"],
                "scheme": doc["scheme"],
                "doc_type": doc["doc_type"],
                "source_url": doc["url"],
                "content": chunk_text,
                "chunk_index": i,
                "total_chunks": len(text_chunks),
            })

    console.print(
        f"\n[bold green]✓ Split {len(documents)} documents into "
        f"{len(all_chunks)} chunks[/bold green]"
    )
    console.print(
        f"  [dim]Settings: chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}[/dim]"
    )

    return all_chunks


# ── Quick test ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Test with sample data
    test_docs = [{
        "id": 1,
        "scheme": "Test Scheme",
        "doc_type": "Test Doc",
        "url": "https://example.com",
        "content": "A" * 1200,  # Should produce ~3 chunks
    }]
    chunks = split_documents(test_docs)
    for c in chunks:
        console.print(f"  {c['chunk_id']}: {len(c['content'])} chars")
