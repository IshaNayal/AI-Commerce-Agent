# System Design Interview Theory: Backend Logic & APIs

If evaluating the Commerce Backend from a Backend Engineering interview perspective, here are the theoretical concepts actively demonstrated in Phase 3.

## 1. RESTful API Design
- **Theory:** Representational State Transfer (REST) relies on standard HTTP methods applied to resource-based URLs.
- **Our Implementation:**
  - **Resource Naming:** Nouns, not verbs (e.g., `POST /products`, not `POST /create_product`).
  - **Hierarchy:** Nested resources for relationships where appropriate (e.g., `GET /products/merchants/{id}` to get a merchant's products, or `POST /carts/{id}/items` to add an item to a specific cart).
  - **HTTP Status Codes:** Proper utilization of semantics. 
    - `201 Created` for `POST`.
    - `204 No Content` for `DELETE`.
    - `404 Not Found` for invalid IDs.
    - `409 Conflict` for state violations (e.g., trying to create a merchant that already exists).

## 2. Dependency Injection (Inversion of Control)
- **Theory:** Components should receive their dependencies from the outside, rather than creating them internally. This makes code modular, reusable, and testable.
- **Our Implementation:** FastAPI's `Depends()` system is heavily utilized. The `get_db` generator yields a database session, which is injected into the controller. The controller then injects this session into the `Service`, which injects it into the `Repository`. When writing Pytest tests, we override the `get_db` dependency to inject a specialized test database session.

## 3. Domain-Driven Design (DDD) Concepts
- **Theory:** Software should be modeled around the business domain, with strict boundaries protecting domain invariants.
- **Our Implementation:** 
  - **Aggregates:** A `Cart` and its `CartItems` act as an aggregate. You don't interact with `CartItems` in isolation; you interact with them *through* the `CartService` (e.g., `cart_service.add_item(cart_id)`). This guarantees that adding an item to a cart respects the rules of the cart (e.g., ensuring the cart is in an `ACTIVE` status).
  - **Domain Services:** The checkout logic in `OrderService.checkout()` encapsulates complex cross-domain interactions (validating the Cart, deducting Inventory, generating the Order).

## 4. Idempotency (Future Proofing)
- **Theory:** An operation is idempotent if performing it multiple times yields the same result as performing it once.
- **Our Implementation Context:** While standard `PUT` and `DELETE` routes in our API are naturally idempotent, operations like `POST /orders/checkout/{cart_id}` are trickier. Because we change the cart status to `CHECKED_OUT` inside the same database transaction that creates the order, a second attempt to checkout the exact same cart will instantly fail with a `ValueError("Cart is already checked out")`. This prevents accidental double-charging if a user clicks the "Buy" button twice.
