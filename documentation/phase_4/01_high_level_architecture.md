# High Level Architecture: Product Retrieval (Semantic Search)

## Overview
Phase 4 focused on upgrading our standard product catalog to support semantic search. This allows our LangChain Agent (in Phase 5) to find products based on conceptual meaning (e.g., "footwear") rather than exact keyword matches (e.g., "shoes").

## Architecture Pattern: Embedded Vector Store
We integrated an embedded vector database alongside our primary relational database. 

1. **Relational Database (PostgreSQL):** Remains the absolute source of truth for the product catalog (pricing, SKU, availability).
2. **Vector Database (ChromaDB):** Acts as a highly optimized, secondary search index. It stores the mathematical representations (embeddings) of product descriptions.
3. **Synchronization (Service Layer):** The `ProductService` orchestrates keeping the two in sync. Whenever a product is created or updated in PostgreSQL, the `ProductService` intercepts the payload and passes it to the `VectorService` to update the corresponding vector in ChromaDB.

## The Search Flow
1. **Query:** User searches for "cheap lightweight running gear".
2. **Embedding:** `VectorService` calls the OpenAI API to convert the text query into a 1536-dimensional float vector.
3. **Vector Search:** ChromaDB compares this vector against all stored product vectors using Cosine Similarity, filtering strictly by the active `merchant_id`.
4. **Hydration:** ChromaDB returns a list of UUIDs (e.g., `[uuid1, uuid2]`). The `ProductService` takes these UUIDs and fetches the complete, up-to-date `Product` objects from PostgreSQL.
5. **Response:** The fully hydrated products are serialized to JSON and returned via the API.
