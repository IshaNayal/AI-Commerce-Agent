# Reasoning and Trade-offs

When designing the Database and Data Layer for the AI Commerce Agent, several technical choices were made to optimize for scalability, data integrity, and multi-tenancy.

## 1. Why PostgreSQL?
- **Trade-off:** PostgreSQL over NoSQL (e.g., MongoDB).
- **Reasoning:** E-commerce systems are highly transactional. We need strict **ACID** (Atomicity, Consistency, Isolation, Durability) guarantees, especially around inventory management and order creation. PostgreSQL provides robust transactional support, row-level locking (`SELECT ... FOR UPDATE`), and relational integrity. Furthermore, we can utilize `pgvector` later for Phase 4 (Product Retrieval) semantic search within the same database.

## 2. UUIDs as Primary Keys
- **Trade-off:** Using `UUIDv4` instead of auto-incrementing `INTEGER`.
- **Reasoning:** 
  - **Security:** Auto-incrementing IDs allow attackers to guess the size of a business (e.g., Order #100 vs #105) or easily scrape all data via simple iteration.
  - **Distributed Systems:** UUIDs allow clients or multiple database nodes to generate keys safely without coordinating with a central authority, preventing ID collisions.
  - **Downside:** UUIDs take up more disk space (16 bytes vs 4/8 bytes) and can fragment B-tree indexes, but for our scale, the security and distribution benefits vastly outweigh the storage cost.

## 3. Separating `Product` and `Inventory`
- **Trade-off:** Having an `inventory` table vs a `stock_quantity` column directly on the `products` table.
- **Reasoning:** 
  - E-commerce sites have high read-volume for product metadata (browsing) and high write-volume for inventory (checking out).
  - If they were combined, locking the product row to update the stock during a checkout would block read queries for the product page.
  - By separating them, we can lock the `Inventory` row to ensure atomic stock decrements without impacting the read performance of the `Product` catalog.

## 4. Denormalizing `unit_price` in `OrderItem`
- **Trade-off:** Storing `unit_price` redundantly in `order_items` instead of joining back to `products.price`.
- **Reasoning:** Products change prices over time (e.g., sales, inflation). An order represents a historical financial contract. If we solely referenced `products.price`, old orders would appear to change in value if the merchant later updated the product price. We *must* capture the price at the exact moment of checkout.

## 5. Soft Deletes vs Hard Deletes
- **Current State:** Most of our models currently allow hard deletes (e.g. deleting a `Cart`).
- **Reasoning:** Ephemeral data like Carts can be hard-deleted to save space. However, entities like Orders and Audit Logs are strictly append-only.
