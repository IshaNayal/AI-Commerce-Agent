# Reasoning and Trade-offs (Phase 3)

When implementing the Service and API layers, several architectural and design decisions were made to prioritize maintainability and testability.

## 1. Thin Controllers vs. Fat Services
- **Trade-off:** Writing extra boilerplate to map HTTP requests to Service methods, rather than just putting the logic directly in the FastAPI route.
- **Reasoning:** If business logic lives in the FastAPI route, it becomes tightly coupled to the HTTP context. You cannot reuse that logic in a background worker (like Celery) or an internal CLI script without mocking an HTTP request. By keeping controllers thin, the `OrderService` can be easily imported and used by our upcoming LangChain Agent (Phase 5) without worrying about HTTP.

## 2. Exception Handling Strategy
- **Trade-off:** Services throw native Python exceptions (`ValueError`) instead of FastAPI's `HTTPException`.
- **Reasoning:** A Service should not know it is being executed in a web context. If a cart is empty during checkout, the `OrderService` raises a `ValueError("Cart is empty")`. The FastAPI controller catches this `ValueError` and translates it into a `400 Bad Request` `HTTPException`. This ensures the Service remains framework-agnostic.

## 3. Passing `db: Session` down the chain
- **Trade-off:** Injecting the database session into every Service and Repository manually via their constructors.
- **Reasoning:** 
  - **Pros:** It makes dependency injection and unit testing incredibly easy. We can pass a mock session or a rolled-back test session directly into the Service. It also allows a single HTTP request to share exactly one database transaction across multiple services.
  - **Cons:** It adds boilerplate to the constructors.
  - **Alternative rejected:** Using a global/thread-local database session (like Flask's `g` object), which obscures dependencies and makes async/testing much harder.

## 4. Pydantic for Validation
- **Trade-off:** Using separate Pydantic schemas (e.g., `ProductCreate`, `ProductResponse`) instead of exposing SQLAlchemy models directly to the API.
- **Reasoning:** 
  - Exposing DB models directly can lead to over-posting vulnerabilities (where a user sends `{"is_admin": true}` in a JSON payload and accidentally overwrites a protected database column).
  - Pydantic schemas create a strict, explicit contract for exactly what data is allowed in (Create/Update schemas) and exactly what data is allowed out (Response schemas).
