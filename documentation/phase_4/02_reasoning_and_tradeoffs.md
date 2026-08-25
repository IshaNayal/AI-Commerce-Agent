# Reasoning and Trade-offs (Phase 4)

## 1. ChromaDB vs pgvector
- **Initial Plan:** We originally planned to use the `pgvector` extension inside PostgreSQL to keep all data (relational and vector) in a single database.
- **Pivot:** The local Windows PostgreSQL installation did not have `pgvector` compiled or available. Compiling C++ Postgres extensions on Windows is highly disruptive and error-prone.
- **Trade-off:** We pivoted to **ChromaDB**. 
  - **Pros:** It's written in Python/C++, runs natively as an embedded library (no separate Docker container needed), and integrates perfectly with LangChain.
  - **Cons:** It introduces a "Dual Write" problem. We now have two databases (Postgres and Chroma) that must be kept in sync. If the Postgres transaction commits but the Chroma write fails, the search index goes out of sync. For this prototype, we accept this risk and use a `try/except` block to fail gracefully, but a production system would use a message queue (like Kafka) or a CDC (Change Data Capture) tool like Debezium for reliable synchronization.

## 2. OpenAI Embeddings vs Local Models
- **Trade-off:** We chose OpenAI's `text-embedding-3-small` over a local model like `sentence-transformers/all-MiniLM-L6-v2`.
- **Reasoning:** 
  - **Pros:** OpenAI embeddings are highly capable, incredibly fast to generate via API, and require zero local GPU compute or massive PyTorch dependencies.
  - **Cons:** They cost money per token and introduce network latency. 
  - Since we are building an AI Commerce Agent that will heavily rely on OpenAI's GPT models anyway, standardizing on OpenAI for embeddings keeps the stack unified.

## 3. Hydration Strategy (Vector Search -> DB Lookup)
- **Trade-off:** We only store the `product_id` and `merchant_id` as metadata in ChromaDB. We do not store the product's `price`, `stock`, or `sku` in ChromaDB.
- **Reasoning:** Prices and stock levels change constantly. If we stored them in the vector database, we would have to re-index the vector every time an item is purchased. By only storing the immutable text (Name and Description) in ChromaDB, we can perform the semantic search to get the IDs, and then query Postgres (the source of truth) to get the real-time price and stock. This guarantees the customer never sees stale pricing data in search results.
