from typing import Any
import uuid

import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings

from backend.app.config import settings

class VectorService:
    """
    Manages semantic search using ChromaDB.
    """
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./.chroma")
        
        # We need an OpenAI API key in settings
        api_key = getattr(settings, "OPENAI_API_KEY", None)
        if api_key:
            self.embeddings = OpenAIEmbeddings(openai_api_key=api_key, model="text-embedding-3-small")
        else:
            self.embeddings = None
            
        # Get or create a collection for products
        self.collection = self.client.get_or_create_collection(
            name="products",
            metadata={"hnsw:space": "cosine"}
        )

    def _get_embedding(self, text: str) -> list[float]:
        if not self.embeddings:
            # Fallback if no OpenAI key, return a zero vector (just for testing logic)
            return [0.0] * 1536
        return self.embeddings.embed_query(text)

    def index_product(self, product: Any) -> None:
        """
        Convert product metadata to an embedding and store it in ChromaDB.
        """
        # Create a rich text representation for the embedding
        desc = getattr(product, 'description', '') or ''
        text = f"Name: {product.name}\nDescription: {desc}"
        
        embedding = self._get_embedding(text)
        
        self.collection.upsert(
            documents=[text],
            embeddings=[embedding],
            metadatas=[{"merchant_id": str(product.merchant_id)}],
            ids=[str(product.id)]
        )

    def semantic_search(self, query: str, merchant_id: uuid.UUID, top_k: int = 5) -> list[uuid.UUID]:
        """
        Search for products matching the query.
        Returns a list of product UUIDs.
        """
        embedding = self._get_embedding(query)
        
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
            where={"merchant_id": str(merchant_id)}
        )
        
        if not results["ids"] or not results["ids"][0]:
            return []
            
        return [uuid.UUID(doc_id) for doc_id in results["ids"][0]]
