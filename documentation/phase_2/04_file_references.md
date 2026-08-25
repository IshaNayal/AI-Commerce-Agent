# File References & Explanations (Phase 2)

Below is a breakdown of the critical files constructed during Phase 2 to implement the Data Layer.

## Models (`backend/app/models/`)
These files define the SQLAlchemy ORM mapping. They inherit from a declarative `Base`.

- `merchant.py`: Defines the `merchants` table. The root entity of our multi-tenant system.
- `product.py`: Defines the `products` table. Holds the catalog information (`name`, `sku`, `price`).
- `inventory.py`: Defines the `inventory` table. Contains a 1-to-1 relationship with `Product`. Includes a `CheckConstraint('quantity >= 0')` to enforce data integrity.
- `cart.py`: Defines the `carts` table. Tracks a user's active shopping session.
- `cart_item.py`: Defines the `cart_items` table. A many-to-one mapping back to the `Cart`, holding references to `Products` and desired quantities.
- `order.py`: Defines the `orders` table. Contains the final checkout metadata (`subtotal`, `status`, `currency`).
- `order_item.py`: Defines the `order_items` table. Snapshots the `CartItem` data (crucially capturing the `unit_price` at the time of purchase).
- `audit.py`: Defines the `audit_logs` table. Stores actions taken within the system, critical for tracking what the AI Agent does on behalf of a merchant.

## Alembic Migrations (`backend/alembic/`)
Alembic tracks the changes to the models above and generates SQL scripts to apply them to PostgreSQL.

- `alembic/env.py`: Configured to read our `DATABASE_URL` and load our `Base.metadata` so it can auto-generate diffs.
- `alembic/versions/739b5372ffff_create_commerce_schema.py`: The initial migration that created Merchants, Products, Inventory, Carts, and Cart Items.
- `alembic/versions/dedfbbd107e4_create_orders_and_order_items.py`: The second migration expanding the schema to include Orders and Order Items for checkout.
- `alembic/versions/568789fd964f_create_audit_logs.py`: The final migration in Phase 2, introducing the `audit_logs` table.

## Schemas (`backend/app/schemas/`)
These are Pydantic models used to validate incoming requests and outgoing responses. While technically bridging into Phase 3, they strictly define how the Data Layer communicates with the outside world.

- Example: `schemas/order.py` uses `model_config = ConfigDict(from_attributes=True)` to seamlessly parse the SQLAlchemy ORM object returned from the database into JSON.

## Database Connection (`backend/app/database/`)
- `session.py`: Sets up the `engine` and `sessionmaker`. 
  - *Key Detail:* We specifically configured `expire_on_commit=False` for testing sessions so that queried objects don't lazily reload and throw `InvalidRequestError` when accessed after a transaction commits.
