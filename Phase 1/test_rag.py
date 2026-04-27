import chromadb
from chromadb.utils import embedding_functions

try:
    print("Initializing ChromaDB...")
    client = chromadb.PersistentClient(path="./test_chroma")
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    print("Embedding function loaded. Initializing collection...")
    collection = client.get_or_create_collection(name="test_col", embedding_function=ef)
    print("Collection ready.")
    collection.add(ids=["1"], documents=["test document"])
    print("Document added.")
    results = collection.query(query_texts=["test"], n_results=1)
    print(f"Results: {results}")
except Exception as e:
    print(f"Error: {e}")
