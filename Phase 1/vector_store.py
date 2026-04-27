"""
Vector Store Module
===================
Stores text chunks in ChromaDB with full source metadata enabled,
as specified in the architecture. Every chunk remembers:
  - source_url → for citation rendering
  - scheme → for filtering
  - doc_type → for context
  - chunk_id → for traceability
"""

import os
import chromadb
from chromadb.utils import embedding_functions
from rich.console import Console

console = Console()

# ── Paths ────────────────────────────────────────────────────────────────────
PERSIST_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
COLLECTION_NAME = "groww_mf_knowledge_base"


def get_embedding_function():
    """
    Create an embedding function using sentence-transformers.
    Uses 'all-MiniLM-L6-v2' — a fast, lightweight model ideal for RAG.
    """
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )


def get_or_create_collection(reset: bool = False):
    """
    Get or create the ChromaDB collection for our knowledge base.

    Args:
        reset: If True, delete existing collection and start fresh.
    """
    client = chromadb.PersistentClient(path=PERSIST_DIR)
    ef = get_embedding_function()

    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
            console.print("[yellow]⟳ Existing collection deleted for fresh ingestion[/yellow]")
        except Exception:
            pass  # Collection didn't exist

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},  # Cosine similarity for semantic search
    )

    return collection


def store_chunks(chunks: list[dict], reset: bool = True) -> dict:
    """
    Store all chunks in ChromaDB with source metadata.

    Args:
        chunks: Output from text_splitter.split_documents()
        reset: If True, clear existing data before inserting.

    Returns:
        Summary dict with stats.
    """
    collection = get_or_create_collection(reset=reset)

    # Prepare batch data
    ids = []
    documents = []
    metadatas = []

    for chunk in chunks:
        ids.append(chunk["chunk_id"])
        documents.append(chunk["content"])
        metadatas.append({
            "source_id": chunk["source_id"],
            "scheme": chunk["scheme"],
            "doc_type": chunk["doc_type"],
            "source_url": chunk["source_url"],
            "chunk_index": chunk["chunk_index"],
            "total_chunks": chunk["total_chunks"],
        })

    # ChromaDB has a batch limit; insert in batches of 100
    batch_size = 100
    for i in range(0, len(ids), batch_size):
        batch_end = min(i + batch_size, len(ids))
        collection.add(
            ids=ids[i:batch_end],
            documents=documents[i:batch_end],
            metadatas=metadatas[i:batch_end],
        )
        console.print(
            f"  [green]✓[/green] Stored batch {i // batch_size + 1}: "
            f"chunks {i + 1}–{batch_end}"
        )

    total = collection.count()
    console.print(f"\n[bold green]✓ Vector store ready — {total} chunks indexed[/bold green]")
    console.print(f"  [dim]Persist directory: {PERSIST_DIR}[/dim]")
    console.print(f"  [dim]Collection: {COLLECTION_NAME}[/dim]")

    return {
        "total_chunks": total,
        "persist_dir": PERSIST_DIR,
        "collection_name": COLLECTION_NAME,
    }


def query_store(query: str, n_results: int = 3) -> list[dict]:
    """
    Search the vector store for the top-N most relevant chunks.

    Args:
        query: The user's question.
        n_results: Number of results to return (default: 3 per architecture).

    Returns:
        List of dicts with chunk content, metadata, and distance score.
    """
    collection = get_or_create_collection(reset=False)

    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    formatted = []
    for i in range(len(results["ids"][0])):
        formatted.append({
            "chunk_id": results["ids"][0][i],
            "content": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i],
        })

    return formatted


# ── Quick test ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Test with sample data
    test_chunks = [
        {
            "chunk_id": "test_1",
            "source_id": 1,
            "scheme": "HDFC Top 100",
            "doc_type": "SID",
            "source_url": "https://example.com",
            "content": "HDFC Top 100 Fund is a large cap equity fund.",
            "chunk_index": 0,
            "total_chunks": 1,
        }
    ]
    store_chunks(test_chunks, reset=True)

    results = query_store("What is HDFC Top 100?")
    for r in results:
        console.print(f"\n[bold]{r['chunk_id']}[/bold] (distance: {r['distance']:.4f})")
        console.print(f"  {r['content'][:200]}")
        console.print(f"  Source: {r['metadata']['source_url']}")
