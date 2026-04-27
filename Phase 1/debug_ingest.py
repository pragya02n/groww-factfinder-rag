"""
Debug version of Phase 1 Ingestion
No Rich, simple Print, extra logging
"""
import os
import re
import time
import requests
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from chromadb.utils import embedding_functions

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

def parse_sources(filepath):
    print(f"Parsing sources from: {filepath}")
    if not os.path.exists(filepath):
        print(f"ERROR: {filepath} not found.")
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    row_pattern = re.compile(
        r"\|\s*(\d+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*\[.*?\]\((https?://.*?)\)\s*\|"
    )
    sources = []
    for match in row_pattern.finditer(content):
        sources.append({
            "id": int(match.group(1)),
            "scheme": match.group(2).strip(),
            "doc_type": match.group(3).strip(),
            "url": match.group(4).strip(),
        })
    return sources

def scrape(url):
    print(f"  Crawling: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        print(f"    Status: {response.status_code}")
        if response.status_code != 200:
            return ""
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "button", "iframe", "noscript", "svg"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()
    except Exception as e:
        print(f"    ERROR scraping {url}: {e}")
        return ""

def main():
    base_dir = os.path.dirname(__file__)
    sources_path = os.path.join(base_dir, "..", "sources.md")
    sources = parse_sources(sources_path)
    if not sources:
        print("No sources found.")
        return

    documents = []
    print(f"Starting crawl of {len(sources)} sources...")
    for s in sources:
        text = scrape(s["url"])
        if text:
            print(f"    Got {len(text)} chars.")
            documents.append({**s, "content": text})
        time.sleep(1)

    if not documents:
        print("No content retrieved.")
        return

    print("Splitting into chunks...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = []
    for doc in documents:
        texts = splitter.split_text(doc["content"])
        print(f"  {doc['scheme']}: {len(texts)} chunks")
        for i, t in enumerate(texts):
            chunks.append({
                "id": f"src_{doc['id']}_chunk_{i}",
                "content": t,
                "metadata": {
                    "source_id": doc["id"],
                    "scheme": doc["scheme"],
                    "doc_type": doc["doc_type"],
                    "source_url": doc["url"],
                }
            })

    print(f"Initializing Vector Store with {len(chunks)} chunks...")
    db_path = os.path.join(base_dir, "chroma_db_debug")
    client = chromadb.PersistentClient(path=db_path)
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    collection = client.get_or_create_collection(name="groww_debug", embedding_function=ef)
    
    # Store in batches
    batch_size = 50
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        collection.add(
            ids=[c["id"] for c in batch],
            documents=[c["content"] for c in batch],
            metadatas=[c["metadata"] for c in batch]
        )
        print(f"  Added batch {i//batch_size + 1}")

    print("Indexing complete.")
    
    # Run user test query
    query = "What is the exit load for HDFC Top 100?"
    print(f"Running test query: {query}")
    results = collection.query(query_texts=[query], n_results=3)
    
    print("\n--- RETRIEVAL RESULTS ---")
    for i in range(len(results["ids"][0])):
        print(f"\nCHUNK {i+1} (Source: {results['metadatas'][0][i]['scheme']})")
        print(f"Content: {results['documents'][0][i][:400]}...")
        print(f"URL: {results['metadatas'][0][i]['source_url']}")

if __name__ == "__main__":
    main()
