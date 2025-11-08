"""RAG System with FAISS vector search"""
import numpy as np
from typing import List, Dict, Any
import os
import pickle
import hashlib

# Optional langchain imports
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
    except ImportError:
        # Fallback: simple text splitter
        RecursiveCharacterTextSplitter = None

# Optional FAISS import with fallback
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("⚠️  FAISS not available, using fallback search")

# Optional LangChain embeddings with fallback
try:
    from langchain.embeddings import OpenAIEmbeddings
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False


class RAGSystem:
    """Retrieval-Augmented Generation system using FAISS"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.index_path = f"./faiss_index_{user_id}"
        self.metadata_path = f"./faiss_metadata_{user_id}.pkl"
        self.embeddings = self._initialize_embeddings()
        self.index = None
        self.metadata = []
        self.load_index()
    
    def _initialize_embeddings(self):
        """Initialize embedding model"""
        # Try OpenRouter or Gemini for embeddings
        if EMBEDDINGS_AVAILABLE and os.getenv("OPENROUTER_API_KEY"):
            try:
                return OpenAIEmbeddings(
                    openai_api_base="https://openrouter.ai/api/v1",
                    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
                    model="text-embedding-ada-002",
                )
            except Exception as e:
                print(f"⚠️  Embedding initialization failed: {e}")
                return None
        # Always return None for deterministic fallback
        return None
    
    def _text_to_vector(self, text: str, dimension: int = 384) -> np.ndarray:
        """Convert text to vector using deterministic hashing (fallback)"""
        # Use SHA-256 hash of text to create deterministic vector
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Repeat hash to fill dimension
        repeated = hash_bytes * (dimension // len(hash_bytes) + 1)
        vector = np.frombuffer(repeated[:dimension], dtype=np.uint8).astype('float32')
        
        # Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector
    
    def load_index(self):
        """Load existing FAISS index or metadata"""
        try:
            if FAISS_AVAILABLE and os.path.exists(self.index_path):
                self.index = faiss.read_index(self.index_path)
                print(f"✓ Loaded FAISS index")
            
            if os.path.exists(self.metadata_path):
                with open(self.metadata_path, "rb") as f:
                    self.metadata = pickle.load(f)
                print(f"✓ Loaded {len(self.metadata)} documents")
        except Exception as e:
            print(f"No existing index found, will create new one: {e}")
            self.index = None
            self.metadata = []
    
    def save_index(self):
        """Save FAISS index and metadata to disk"""
        if FAISS_AVAILABLE and self.index:
            faiss.write_index(self.index, self.index_path)
        
        # Always save metadata for fallback search
        with open(self.metadata_path, "wb") as f:
            pickle.dump(self.metadata, f)
        print(f"✓ Saved index with {len(self.metadata)} documents")
    
    async def add_documents(
        self,
        texts: List[str],
        source: str,
    ) -> List[str]:
        """Add documents to index (FAISS or fallback)"""
        
        # Split texts into chunks
        chunks = []
        if RecursiveCharacterTextSplitter:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
            )
            for text in texts:
                chunks.extend(text_splitter.split_text(text))
        else:
            # Simple fallback splitting by sentences
            for text in texts:
                sentences = text.split('. ')
                current_chunk = ""
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) < 500:
                        current_chunk += sentence + ". "
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                        current_chunk = sentence + ". "
                if current_chunk:
                    chunks.append(current_chunk)
        
        # Generate embeddings (with fallback)
        dimension = 384
        if self.embeddings and EMBEDDINGS_AVAILABLE:
            try:
                embeddings = await self.embeddings.aembed_documents(chunks)
                embeddings_array = np.array(embeddings).astype('float32')
            except Exception as e:
                print(f"⚠️  Embedding failed, using deterministic fallback: {e}")
                embeddings_array = np.array([
                    self._text_to_vector(chunk, dimension) for chunk in chunks
                ]).astype('float32')
        else:
            # Deterministic fallback using hashing
            embeddings_array = np.array([
                self._text_to_vector(chunk, dimension) for chunk in chunks
            ]).astype('float32')
        
        # Create or update FAISS index (if available)
        if FAISS_AVAILABLE:
            if self.index is None:
                dimension = embeddings_array.shape[1]
                self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings_array)
        
        # Store metadata (always, for fallback search)
        start_id = len(self.metadata)
        vector_ids = []
        for i, chunk in enumerate(chunks):
            vector_id = f"vec_{start_id + i}"
            self.metadata.append({
                "id": vector_id,
                "content": chunk,
                "source": source,
                "vector": embeddings_array[i].tolist() if not FAISS_AVAILABLE else None,
            })
            vector_ids.append(vector_id)
        
        self.save_index()
        return vector_ids
    
    async def search(
        self,
        query: str,
        k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Search for similar documents (FAISS or fallback keyword search)"""
        
        if len(self.metadata) == 0:
            # No documents indexed yet
            return [{
                "content": f"No documents found for: {query}",
                "source": "System",
                "score": 0.0,
            }]
        
        k = min(k, len(self.metadata))
        
        # FAISS search (if available)
        if FAISS_AVAILABLE and self.index:
            # Generate query embedding
            dimension = self.index.d
            if self.embeddings and EMBEDDINGS_AVAILABLE:
                try:
                    query_embedding = await self.embeddings.aembed_query(query)
                    query_vector = np.array([query_embedding]).astype('float32')
                except Exception:
                    query_vector = np.array([self._text_to_vector(query, dimension)]).astype('float32')
            else:
                query_vector = np.array([self._text_to_vector(query, dimension)]).astype('float32')
            
            # Search
            distances, indices = self.index.search(query_vector, k)
            
            # Retrieve results
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.metadata):
                    result = self.metadata[idx].copy()
                    result.pop("vector", None)  # Remove vector from response
                    result["score"] = float(distances[0][i])
                    results.append(result)
            
            return results
        
        # Fallback: simple keyword search
        else:
            query_lower = query.lower()
            scored_docs = []
            
            for doc in self.metadata:
                content_lower = doc["content"].lower()
                # Simple keyword matching score
                score = sum(1 for word in query_lower.split() if word in content_lower)
                if score > 0:
                    scored_docs.append({
                        "content": doc["content"],
                        "source": doc["source"],
                        "score": float(score),
                    })
            
            # Sort by score and return top k
            scored_docs.sort(key=lambda x: x["score"], reverse=True)
            results = scored_docs[:k]
            
            # If no matches, return first k documents
            if not results:
                results = [
                    {
                        "content": doc["content"],
                        "source": doc["source"],
                        "score": 0.0,
                    }
                    for doc in self.metadata[:k]
                ]
            
            return results
