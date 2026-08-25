# File References & Explanations (Phase 3)

Below is a breakdown of the critical files constructed during Phase 3 to implement the Service Layer and the API Routes.

## Services (`backend/app/services/`)
These contain the core business rules of the application.

- `merchant_services.py`: Manages merchant creation, retrieval, and updates.
- `product_service.py`: Handles catalog management (creating products, listing by merchant). Ensures products are correctly tied to their owning merchant.
- `inventory_service.py`: Encapsulates stock logic. Contains methods to safely check, increase, and decrease stock. Crucially, it provides a `reserve_stock` method that uses row-level locking for safe concurrent checkout.
- `cart.py` (CartService): Manages the shopping session. Enforces rules like preventing inactive products from being added to a cart, or preventing items from different merchants in the same cart.
- `order_service.py`: The most complex service. Contains the `checkout()` method which executes an atomic transaction to validate a cart, lock inventory, deduct stock, capture historical prices, create the order, and transition the cart status.
- `audit_service.py`: A simple append-only service used to write to the audit log.

## API Routers (`backend/app/api/routes/`)
These files map HTTP requests to the Services above.

- `merchants.py`: Exposes CRUD operations for Merchants (`/merchants`).
- `products.py`: Exposes endpoints for managing the catalog, including retrieving all products for a specific merchant (`/products/merchants/{id}`).
- `inventory.py`: Exposes specific stock adjustment endpoints (`/inventory/product/{id}/increase`).
- `carts.py`: Exposes endpoints to manage the active shopping session and manipulate nested cart items (`/carts/{id}/items`).
- `orders.py`: Exposes the checkout endpoint (`POST /orders/checkout/{cart_id}`) and order retrieval.

## Main Application (`backend/app/main.py`)
- The entry point of the FastAPI application.
- All routers from `api/routes/` are imported and registered here via `app.include_router()`.
- Global exception handlers are registered to map internal application errors to standardized JSON HTTP responses.
