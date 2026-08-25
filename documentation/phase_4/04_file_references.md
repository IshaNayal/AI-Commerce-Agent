# File References & Explanations (Phase 4)

Below is a breakdown of the critical files constructed during Phase 4 to implement Semantic Product Retrieval.

## Services
- `backend/app/services/vector_service.py`
  - **Purpose:** Encapsulates all interactions with ChromaDB and OpenAI Embeddings.
  - **Key Methods:** 
    - `index_product()`: Takes a SQLAlchemy `Product` object, formats its name and description into a single string, requests an embedding, and upserts it into the local Chroma file-system database (`./.chroma`).
    - `semantic_search()`: Takes a natural language query, embeds it, and performs a nearest-neighbor vector search in Chroma, filtering by `merchant_id`. Returns a list of `UUIDs`.

- `backend/app/services/product_service.py`
  - **Changes Made:** 
    - Injected `VectorService` into the constructor.
    - Updated `create()` and `update()` methods to automatically call `vector_service.index_product()` after a successful database commit.
    - Added a `search_products()` method that queries the vector database for IDs, and then fetches the actual product rows from PostgreSQL to return hydrated data.

## API Routes
- `backend/app/api/routes/products.py`
  - **Changes Made:** Added a new `GET /products/search` endpoint.
  - **Routing Note:** This route had to be placed *before* the `GET /products/{product_id}` route in the file. If it were placed after, FastAPI would attempt to parse the string "search" as a UUID and throw a 422 Validation Error.

## Testing
- `backend/tests/test_product_search.py`
  - **Purpose:** Verifies the semantic search pipeline.
  - **Key Detail:** We used `pytest`'s `monkeypatch` to mock the OpenAI embedding generation (`mock_get_embedding`). If the test string contained "shoes", it returned a dummy vector. This ensures the automated test suite runs blazingly fast without requiring internet access or spending OpenAI API credits.
