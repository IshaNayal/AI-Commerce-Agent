# System Design Interview Theory: Semantic Search

If discussing Phase 4 in a Backend Engineering or Machine Learning Systems design interview, these are the core theoretical concepts applied.

## 1. Vector Embeddings
- **Theory:** Neural networks can represent complex objects (words, sentences, images) as dense arrays of floating-point numbers (vectors). The distance between two vectors in a high-dimensional space represents their semantic similarity.
- **Our Implementation:** We take a product's name and description and pass it through OpenAI's embedding model. "Running Shoes" and "Athletic Footwear" will result in vectors that are mathematically very close to each other, even though they share no common characters.

## 2. Cosine Similarity vs. Euclidean Distance
- **Theory:** When comparing two vectors to see how similar they are, you can measure the straight-line distance between their endpoints (Euclidean Distance / L2) or the angle between them (Cosine Similarity). Cosine similarity is generally preferred for text embeddings because it measures the *orientation* of the vectors regardless of their magnitude (length of the text).
- **Our Implementation:** When initializing the ChromaDB collection, we explicitly configured the metric space: `metadata={"hnsw:space": "cosine"}`.

## 3. Metadata Filtering (Pre-filtering vs Post-filtering)
- **Theory:** In a multi-tenant SaaS application, searching across *all* vectors and then discarding results that belong to the wrong tenant (Post-filtering) is highly inefficient and dangerous (you might get 5 results, discard all 5, and return nothing to the user). Pre-filtering pushes the `merchant_id` constraint deep into the vector search algorithm so it only searches within the correct tenant's space.
- **Our Implementation:** We store the `merchant_id` in ChromaDB's metadata payload during indexing. When querying, we pass a `where` clause (`where={"merchant_id": str(merchant_id)}`). ChromaDB handles this efficiently.

## 4. The Dual-Write Problem
- **Theory:** In distributed systems, writing to two distinct data stores (PostgreSQL and ChromaDB) within the same API request without distributed transactions (Two-Phase Commit) leads to inconsistency if the network fails halfway through.
- **Our Implementation:** We used a local `try/except` block to attempt a "best effort" synchronization. In a real-world system design interview, you should suggest using the **Outbox Pattern**. (Write the product update and an 'index_event' to Postgres in a single transaction. A background worker then reads the 'index_event' and safely, idempotently updates ChromaDB).
