# High Level Architecture: Database and Data Layer

## Overview
Phase 2 focused on designing and implementing the foundational data layer for the AI Commerce Agent. The primary responsibility of this layer is to define the physical database schema, manage database migrations, and map relational data to Python objects using an ORM.

## Architecture Pattern: Repository & Data Mapper
We implemented a strict separation of concerns using the **Repository Pattern** and the **Data Mapper Pattern** (via SQLAlchemy).

1. **SQLAlchemy Models (Data Mapper):** 
   - Files in `backend/app/models/` represent the exact schema of the database tables.
   - These models are "dumb"—they contain no business logic, only data definitions, foreign keys, and SQL constraints (like `CheckConstraint`).
   - This ensures that the domain layer is decoupled from the specific SQL dialects, but we still leverage the database for data integrity.

2. **Alembic (Migration Management):**
   - We use Alembic to track state changes in our models and generate versioned migration scripts (`backend/alembic/versions/`).
   - This ensures that deploying the application to new environments (staging, production) reliably applies schema changes without manual SQL intervention.

## Entity Relationship Map
The core entities map directly to our domain:

- **Merchant**: The core tenant. Everything in the system (Products, Carts, Orders, Audits) belongs to a Merchant.
- **Product**: Represents a sellable item, containing metadata like SKU, Name, and Price.
- **Inventory**: Separated from Product to allow high-concurrency stock tracking without locking the primary Product metadata row.
- **Cart & CartItem**: Ephemeral state representing a customer's shopping session.
- **Order & OrderItem**: Immutable, historical records of a completed checkout.
- **AuditLog**: An append-only ledger tracking all AI and system actions for explainability and compliance.

By strictly segregating these entities (e.g. keeping `Cart` mutable but `Order` immutable), we ensure the system can handle complex workflows like abandoned cart recovery without corrupting historical financial data.
