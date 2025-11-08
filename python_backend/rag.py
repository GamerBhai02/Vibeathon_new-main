"""Rudimentary RAG system using ChromaDB for document retrieval."""

import os

# Optional imports - gracefully handle missing dependencies
try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("Warning: chromadb and sentence-transformers not available. RAG features disabled.")
    print("To enable RAG features, install with: pip install -r requirements-full.txt")

# --- Configuration ---
CHROMA_DB_PATH = os.environ.get("CHROMA_DB_PATH", "./chroma_db")
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# --- ChromaDB Client ---
# Only initialize client when needed, not at module import
_client = None
_sentence_transformer_ef = None

def get_client():
    """Lazy initialization of ChromaDB client."""
    if not CHROMADB_AVAILABLE:
        raise RuntimeError("ChromaDB is not available. Install with: pip install -r requirements-full.txt")
    
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    return _client

def get_embedding_function():
    """Lazy initialization of embedding function."""
    if not CHROMADB_AVAILABLE:
        raise RuntimeError("ChromaDB is not available. Install with: pip install -r requirements-full.txt")
    
    global _sentence_transformer_ef
    if _sentence_transformer_ef is None:
        # Using a sentence-transformer model for embeddings
        _sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL_NAME
        )
    return _sentence_transformer_ef

# --- RAG System Class ---
class RAGSystem:
    """Manages document indexing and retrieval for a specific user."""

    def __init__(self, user_id: str):
        """Initializes the RAG system for a given user."""
        if not CHROMADB_AVAILABLE:
            raise RuntimeError("RAG features require chromadb and sentence-transformers. Install with: pip install -r requirements-full.txt")
        
        self.user_id = user_id
        self.collection_name = f"user_{user_id}_documents"
        self.collection = None  # Lazy-loaded
        
    def _ensure_collection(self):
        """Ensures the collection is initialized."""
        if self.collection is None:
            client = get_client()
            embedding_fn = get_embedding_function()
            self.collection = client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=embedding_fn
            )

    async def add_document(self, document_id: str, text: str, metadata: dict = None):
        """Adds or updates a document in the user's collection."""
        self._ensure_collection()
        if metadata is None:
            metadata = {}
        metadata["user_id"] = self.user_id
        
        # ChromaDB's add method handles updates if the ID already exists
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[document_id]
        )

    async def add_documents(self, texts: list, source: str):
        """Adds multiple documents to the user's collection."""
        self._ensure_collection()
        for i, text in enumerate(texts):
            document_id = f"{source}_{i}"
            metadata = {"user_id": self.user_id, "source": source}
            self.collection.add(
                documents=[text],
                metadatas=[metadata],
                ids=[document_id]
            )

    async def query(self, query_text: str, n_results: int = 5) -> str:
        """Queries the collection for relevant documents."""
        self._ensure_collection()
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where={"user_id": self.user_id} # Filter results for the specific user
        )
        
        # Combine the retrieved documents into a single context string
        context = "\n---\n".join(doc for doc in results["documents"][0])
        return context

    async def delete_document(self, document_id: str):
        """Deletes a document from the collection."""
        self._ensure_collection()
        self.collection.delete(ids=[document_id])
