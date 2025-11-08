"""Rudimentary RAG system using ChromaDB for document retrieval."""

import chromadb
from chromadb.utils import embedding_functions
import os

# --- Configuration ---
CHROMA_DB_PATH = os.environ.get("CHROMA_DB_PATH", "./chroma_db")
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# --- ChromaDB Client ---
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

# --- Embedding Function ---
# Using a sentence-transformer model for embeddings
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL_NAME
)

# --- RAG System Class ---
class RAGSystem:
    """Manages document indexing and retrieval for a specific user."""

    def __init__(self, user_id: str):
        """Initializes the RAG system for a given user."""
        self.user_id = user_id
        self.collection_name = f"user_{user_id}_documents"
        self.collection = client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=sentence_transformer_ef
        )

    async def add_document(self, document_id: str, text: str, metadata: dict = None):
        """Adds or updates a document in the user's collection."""
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
        self.collection.delete(ids=[document_id])
