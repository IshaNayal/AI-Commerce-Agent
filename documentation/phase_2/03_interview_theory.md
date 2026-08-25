# System Design Interview Theory: Data Layer

If evaluating this data layer from a Systems Design or Backend Engineering interview perspective, several theoretical concepts are actively demonstrated in the implementation.

## 1. Concurrency and Row-Level Locking
A classic interview question is: *"How do you handle two users trying to buy the last item in stock at the exact same time?"*
- **Our Implementation:** In `backend/app/repositories/inventory.py`, we implemented `get_by_product_id_for_update()`.
- **Theory:** This utilizes the `SELECT ... FOR UPDATE` SQL command. When User A begins checkout, PostgreSQL locks that specific inventory row. User B's checkout transaction will block and wait. If User A succeeds, the stock drops to 0. User B's transaction then resumes, sees stock is 0, and cleanly rolls back with an "Insufficient Inventory" exception. This prevents race conditions and overselling.

## 2. ACID Transactions
- **Atomicity:** The entire checkout process (verifying cart, deducting inventory, creating order, creating order items, updating cart status) happens within a single SQLAlchemy `Session`. If any step fails (e.g., inventory runs out), `db.rollback()` is called, and *none* of the changes persist. It is all-or-nothing.
- **Consistency:** We enforce consistency at the database level using constraints. For example, `CheckConstraint('quantity >= 0')` in the Inventory model prevents the database from ever accepting a negative stock value, even if a bug in the Python code tries to save one.
- **Isolation:** By using transactions and row-locks, concurrent database operations do not interfere with each other.
- **Durability:** Once `db.commit()` is called, PostgreSQL persists the checkout data to disk.

## 3. Database Indexing
- **Theory:** Indexes speed up read queries at the cost of slower writes and increased storage.
- **Our Implementation:** We proactively added indexes to frequently queried columns. For example:
  - `merchant_id` is indexed across almost all tables because multi-tenant architectures frequently filter by `WHERE merchant_id = X`.
  - `status` on `carts` and `orders` is indexed because we often query for "all pending orders" or "all active carts".

## 4. Multi-Tenancy Architecture
- **Theory:** SaaS applications must isolate data between different customers (tenants). There are three common approaches: Database-per-tenant, Schema-per-tenant, and Shared-Database/Shared-Schema.
- **Our Implementation:** We use **Shared-Database/Shared-Schema with a Tenant Discriminator**. 
  - Every table (Products, Orders, Carts) includes a `merchant_id` column.
  - All repository queries explicitly filter by `merchant_id` to ensure one merchant cannot read or write another merchant's data.
  - This approach is highly scalable and cost-effective, though it requires discipline in the codebase to never omit the `merchant_id` filter.
