# AI-Commerce-Agent — Phase 1 (First 50%) Engineering Review

## Review Status

- **Review basis:** current repository files, current tests, current Alembic migration, and verified local test execution on 2026-08-23.
- **Documentation scope:** backend foundation and current commerce data layer.
- **Application changes in this task:** none. This document is the only file created.
- **Current collected tests:** 86.
- **Current test result:** 85 passed, 1 failed, 1 warning.
- **Current failing test:** `backend/tests/test_merchant_service.py::test_list_merchants`; it sees 22 persisted merchants in the configured development database instead of only the two created by the test.
- **Current warning:** Starlette/httpx deprecation warning from the installed test client stack.
- **Current database state observed earlier:** the five commerce tables and `alembic_version` exist; the database has also accumulated test data from earlier API runs.
- **Honest completion estimate:** approximately **45–50% of the planned MVP foundation**, but not production-ready. The persistence foundation and basic merchant/product/inventory behavior exist; AI, checkout, payment, authorization, and operational hardening do not.

## Architecture Snapshot

```text
Client
  |
  v
FastAPI application
  |
  v
API routers
  |
  v
Service layer
  |
  v
Repository/data-access layer
  |
  v
SQLAlchemy 2.x
  |
  v
PostgreSQL
```

Future capabilities fit around this foundation:

```text
AI agent / tool calling
        |
        v
Commerce services and guardrails
        |
        v
Repositories and transactional database state

Catalog intelligence, recommendations, upselling, cross-selling,
campaign orchestration, checkout, orders, Razorpay, approvals,
audit events, and analytics are future layers.
```

## 1. Project Overview

### Problem

The project aims to help merchants increase revenue through conversational product discovery, recommendations, upselling, cross-selling, cart management, and eventually AI-assisted checkout. The backend must keep commerce facts authoritative even when an AI model is involved.

### Users and merchants

The intended users are:

- Customers shopping through a conversational interface.
- Merchants managing catalog, inventory, carts, orders, policies, and revenue opportunities.
- Operators or reviewers who will eventually approve sensitive agent actions.

A merchant owns products, inventory, and carts. A customer is currently represented only by a UUID on a cart; there is no customer table or identity system yet.

### Intended customer journey

1. Customer states a need in natural language.
2. An agent interprets intent and searches authoritative catalog data.
3. Backend services return real products, prices, and availability.
4. The customer receives recommendations and optional complementary products.
5. Products are placed into a cart.
6. Checkout calculates totals from database state.
7. Policies and guardrails check bounded actions.
8. A payment provider handles payment.
9. Orders, payment outcomes, agent actions, and audit events are persisted.

Only the early persistence and merchant API portions of that journey exist now.

### Current MVP scope

Implemented or substantially present:

- FastAPI application startup.
- Environment-based settings.
- PostgreSQL SQLAlchemy engine and sessions.
- Declarative models for merchant, product, inventory, cart, and cart item.
- Alembic migration for the five tables.
- Repositories for the five data objects.
- Merchant HTTP API.
- Merchant, product, and inventory service logic.
- Pydantic create/update/response schemas.
- Repository, service, schema, and merchant API tests.

Deliberately outside the current scope:

- LLM or LangChain/LangGraph agent execution.
- Semantic search, embeddings, vector storage, or RAG.
- Customers and authentication.
- Orders and order items.
- Payments or Razorpay integration.
- Promotions, campaigns, recommendations, analytics, approvals, and audit trails.
- Production deployment, observability, rate limiting, and authorization.

### Why backend first

The agent must not invent price, stock, product existence, payment status, or order totals. Building the database and service boundaries first gives future tools a controlled interface. This reduces the risk of granting an LLM unrestricted database access and makes later agent behavior testable against authoritative state.

### Success criteria

For this stage, success means:

- The service starts from a documented command.
- Configuration does not require committed secrets.
- Alembic can reproduce the schema.
- Core relationships and critical invariants are database-enforced.
- API, service, and repository responsibilities are separate.
- Tests are repeatable against an isolated test database.
- Future agent tools can call services without bypassing business rules.

The current implementation meets many structural criteria, but test isolation and production authorization remain incomplete.

## 2. Architectural Decisions

### Decision: FastAPI

**What we chose:** FastAPI with router functions, dependency injection, Pydantic schemas, and generated OpenAPI documentation.

**Why:** It provides typed request validation, straightforward dependency injection, low ceremony HTTP handlers, and a good Python ecosystem fit for a future AI layer.

**Alternatives:** Flask, Django REST Framework, or an async-only framework.

**Why alternatives were rejected:** Django would introduce more framework and ORM conventions than this modular monolith needs. Flask requires more validation and API wiring. An async-only design would not remove the need for database transaction discipline.

**Benefits:** Fast development, clear endpoint contracts, automatic 422 validation responses, testable route functions, and easy future tool/API integration.

**Drawbacks and tradeoffs:** FastAPI does not provide authentication, transaction policy, or business architecture automatically. The team must preserve service boundaries. Async endpoints would require an async SQLAlchemy stack; the current code uses synchronous SQLAlchemy.

**Consequence:** API routes should remain thin. They translate HTTP concerns and call services; they should not contain SQL or checkout workflows.

### Decision: PostgreSQL

**What we chose:** PostgreSQL as the source of truth for commerce state.

**Why:** The domain is relational and transactional: merchants own products, products own inventory, carts contain items, and financial values need consistent constraints.

**Alternatives:** SQLite, MongoDB, Redis, or a hosted search/document store.

**Why rejected:** SQLite is useful for small tests but does not represent production PostgreSQL features such as named enums and PostgreSQL UUID behavior. A document store weakens relational integrity. Redis is a cache/coordination tool, not the primary commerce ledger. The project explicitly excludes additional databases at this stage.

**Tradeoffs:** PostgreSQL costs more operationally than SQLite but provides transactions, constraints, indexes, and scalability. It adds local setup and credential management. It is the correct cost for authoritative commerce data.

### Decision: SQLAlchemy 2.x typed ORM

**What we chose:** `DeclarativeBase`, `Mapped`, `mapped_column`, `relationship`, `Session`, and `select()`.

**Why:** SQLAlchemy is mature, supports PostgreSQL deeply, and the 2.x typed style makes model contracts visible to Python tooling.

**Alternatives:** SQLModel, Django ORM, raw SQL, or another ORM.

**Why rejected:** The project already selected SQLAlchemy and must not introduce another ORM. Raw SQL would duplicate mapping and weaken composability. SQLModel would add a new abstraction without removing the need for separate API schemas.

**Benefits:** Explicit schema mapping, strong PostgreSQL support, parameterized queries, relationship definitions, and Alembic metadata integration.

**Drawbacks:** ORM session state and lazy loading require discipline. Incorrect import paths can create duplicate metadata objects, as happened historically.

### Decision: Pydantic schemas separate from ORM models

**What we chose:** Separate `Create`, `Update`, and `Response` Pydantic models.

**Why:** HTTP contracts and persistence models evolve for different reasons. Pydantic validates external input; SQLAlchemy maps database state.

**Tradeoff:** There is some duplication, but that duplication is an intentional boundary. Pydantic cannot replace database constraints because other writers, race conditions, and migrations can bypass application validation.

### Decision: Alembic migrations

**What we chose:** Alembic with `backend/alembic/env.py` and a generated initial migration.

**Why:** Schema changes need reviewable, ordered, reproducible history across machines and environments.

**Alternatives:** `Base.metadata.create_all()` at startup or manually managed SQL.

**Why rejected:** `create_all()` does not model schema evolution safely and can hide drift. Manual SQL duplicates model definitions and is harder to review.

**Current caveat:** The root `alembic.ini` is configured with `%(here)s/backend/alembic` and `%(here)s/backend`; a stale `backend/alembic.ini` also exists and contains hard-coded development credentials. It should not be used as the project command configuration.

### Decision: Repository pattern

**What we chose:** Repositories encapsulate SQLAlchemy queries and persistence methods.

**Why:** Services and future agent tools should not know table query details. Repositories make data access replaceable and testable.

**Tradeoff:** More files and indirection for a small MVP. The benefit becomes significant once products, checkout, inventory reservation, and orders share queries.

**Current deviation:** Repositories call `commit()` themselves. That is simple for isolated CRUD tests but conflicts with the desired future service-controlled transaction boundary.

### Decision: Service layer

**What we chose:** Services sit between routes and repositories.

**Why:** Business rules such as merchant existence, active-state checks, SKU uniqueness, overselling prevention, and pagination limits do not belong in HTTP handlers or low-level repositories.

**Tradeoff:** Services add an abstraction layer but provide the correct location for future authorization, guardrails, and transaction orchestration.

### Decision: Dependency injection

**What we chose:** FastAPI `Depends(get_db)` for request sessions and constructor injection of `Session` into repositories/services.

**Why:** Session ownership is centralized, routes are testable, and repository objects do not create hidden sessions.

**Current caveat:** `get_db()` closes sessions but does not explicitly rollback in its exception path. API tests override it with rollback-only sessions; production transaction handling still needs refinement.

### Decision: UUID primary keys

**What we chose:** PostgreSQL UUID columns with Python `uuid4` defaults.

**Why:** IDs are difficult to guess, safe to generate across application instances, and suitable for future distributed components.

**Tradeoff:** UUIDs are larger and less locality-friendly than integers, so indexes and joins cost more storage/cache. This is acceptable at MVP scale. Time-ordered UUIDs could be reconsidered later if write locality becomes measurable.

### Decision: Decimal and NUMERIC money

**What we chose:** Python `Decimal` and PostgreSQL `Numeric(12, 2)` for product and cart-item prices.

**Why:** Financial values require exact decimal arithmetic. Binary floating-point can represent values such as `0.1` only approximately.

**Tradeoff:** Decimal arithmetic is slower and requires explicit rounding policy, but correctness dominates that cost for commerce.

### Decision: PostgreSQL enum for cart status

**What we chose:** Named `cart_status` enum with `ACTIVE`, `CHECKED_OUT`, and `ABANDONED` database labels.

**Why:** The database rejects invalid lifecycle states.

**Tradeoff:** Enum changes require migrations and are less flexible than a string or lookup table. For a small fixed state machine, the integrity benefit is worthwhile.

### Decision: Database-generated timestamps

**What we chose:** `server_default=func.now()` and `onupdate=func.now()` with timezone-aware `DateTime`.

**Why:** PostgreSQL is the shared clock and authoritative writer across application processes.

**Tradeoff:** Server defaults are less visible in newly constructed Python objects until flush/refresh, but they avoid machine clock differences.

### Decision: Foreign keys, constraints, and indexes

**What we chose:** Foreign keys, check constraints, unique constraints, and indexes for actual lookup paths.

**Why:** Application validation is not enough. Database invariants protect data regardless of caller.

**Tradeoff:** Constraints can reject writes and indexes increase storage/write cost. These are intentional costs for correctness and common merchant/product lookups.

### Decision: Transaction-isolated tests

**What we chose:** A connection-level transaction and SQLAlchemy session with `join_transaction_mode="rollback_only"`.

**Why:** Tests can call repository methods that commit without permanently changing the database.

**Current limitation:** Existing data in the development database remains visible. A dedicated test database is still the stronger solution.

## 3. Project Structure

```text
AI-Commerce-Agent/
├── alembic.ini
├── backend/
│   ├── alembic/
│   │   ├── env.py
│   │   ├── README
│   │   ├── script.py.mako
│   │   └── versions/
│   │       └── 739b5372ffff_create_commerce_schema.py
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/routes/
│   │   │   ├── health.py
│   │   │   └── merchants.py
│   │   ├── database/
│   │   │   ├── base.py
│   │   │   ├── session.py
│   │   │   └── dependencies.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── repositories/
│   │   ├── services/
│   │   └── agent/, integrations/, guardrails/, utils/
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── documentation/
└── pytest.ini
```

### Directory responsibilities

| Directory/file | Responsibility | Must not contain |
|---|---|---|
| `backend/app/main.py` | Application construction, lifespan, router registration, exception registration | SQL queries or business workflows |
| `api/routes` | HTTP paths, request parsing, status-code translation | ORM queries or agent decisions |
| `services` | Business rules and orchestration | HTTP response construction or engine creation |
| `repositories` | SQLAlchemy data access | FastAPI requests, payment logic, AI prompts |
| `models` | Relational mapping, relationships, database constraints | API-specific validation or HTTP behavior |
| `schemas` | External input/output validation and serialization | Database sessions or SQL queries |
| `database` | Base, engine, session factory, FastAPI dependency | Business rules |
| `alembic` | Migration environment and migration history | Runtime request handling |
| `tests` | Regression and contract verification | Production data setup assumptions |
| `utils` | Shared logging and exception handling utilities | Domain-specific persistence logic |
| `agent`, `integrations`, `guardrails` | Future extension points | Current claims of implemented behavior |

Separation matters because each layer has a different reason to change. A payment provider change should not require rewriting SQL queries; an API response change should not alter database constraints; an LLM prompt change should not bypass service rules.

## 4. Database Architecture

### Connection architecture

`backend/app/config.py` loads `DATABASE_URL` through Pydantic Settings from `backend/.env`, whose path is derived from the config file location. The value is required; credentials are not hard-coded by the application configuration.

`backend/app/database/session.py` creates one synchronous SQLAlchemy engine with `pool_pre_ping=True` and a `sessionmaker` configured with `autoflush=False` and `autocommit=False`. `get_db()` creates a session and closes it after the request.

The intended database is PostgreSQL, using the `postgresql+psycopg` dialect. The actual database name is determined by the local `DATABASE_URL`; historical project documentation refers to `ai_growth`. The URL itself is intentionally not reproduced here.

### Tables

#### `merchants`

| Column | Type | Rules |
|---|---|---|
| `id` | PostgreSQL UUID | Primary key, Python `uuid4` default |
| `name` | `VARCHAR(255)` | Required |
| `slug` | `VARCHAR(255)` | Required, unique, indexed |
| `email` | `VARCHAR(320)` | Required; `EmailStr` validates API input |
| `is_active` | Boolean | Required, Python default `True` |
| `created_at` | Timezone-aware timestamp | Required, PostgreSQL `now()` default |
| `updated_at` | Timezone-aware timestamp | Required, PostgreSQL default and update expression |

Relationships: one merchant has many products and many carts. Products use `delete-orphan`; carts do not currently use orphan deletion on the merchant relationship.

#### `products`

| Column | Type | Rules |
|---|---|---|
| `id` | PostgreSQL UUID | Primary key |
| `merchant_id` | PostgreSQL UUID | Required foreign key to `merchants.id`, `RESTRICT` |
| `name` | `VARCHAR(255)` | Required |
| `description` | Text | Nullable |
| `sku` | `VARCHAR(100)` | Required; unique within merchant |
| `price` | `NUMERIC(12,2)` | Required; database check `price >= 0` |
| `currency` | `VARCHAR(3)` | Required, Python default `INR` |
| `is_active` | Boolean | Required, Python default `True` |
| `created_at` / `updated_at` | Timezone-aware timestamp | PostgreSQL-generated |

Indexes: `merchant_id` and unique `(merchant_id, sku)`. The model also has a non-negative price check.

#### `inventory`

| Column | Type | Rules |
|---|---|---|
| `id` | PostgreSQL UUID | Primary key |
| `product_id` | PostgreSQL UUID | Required, foreign key to products, unique |
| `quantity` | Integer | Required, Python default 0, database check `>= 0` |
| `updated_at` | Timezone-aware timestamp | PostgreSQL-generated/update expression |

The unique product foreign key creates one inventory record per product. The current model does not include `reserved_quantity`, despite that being part of the broader original target design.

#### `carts`

| Column | Type | Rules |
|---|---|---|
| `id` | PostgreSQL UUID | Primary key |
| `merchant_id` | PostgreSQL UUID | Required foreign key to merchants, `RESTRICT` |
| `customer_id` | PostgreSQL UUID | Required UUID, no customer table yet |
| `status` | PostgreSQL enum `cart_status` | Required; active, checked out, or abandoned |
| `created_at` / `updated_at` | Timezone-aware timestamp | PostgreSQL-generated |

#### `cart_items`

| Column | Type | Rules |
|---|---|---|
| `id` | PostgreSQL UUID | Primary key |
| `cart_id` | PostgreSQL UUID | Required foreign key to carts, `CASCADE` |
| `product_id` | PostgreSQL UUID | Required foreign key to products, `RESTRICT` |
| `quantity` | Integer | Required, database check `> 0` |
| `unit_price` | `NUMERIC(12,2)` | Required, database check `>= 0` |
| `created_at` / `updated_at` | Timezone-aware timestamp | PostgreSQL-generated |

The current migration does not create a unique `(cart_id, product_id)` constraint, although the repository provides a lookup for that pair. Duplicate prevention is therefore incomplete at the database level.

## 5. Relationships and Delete Behavior

```text
Merchant
  |
  +--< Products
  |       |
  |       +--1 Inventory
  |
  +--< Carts
          |
          +--< CartItems >-- Product
```

Foreign keys:

- `products.merchant_id -> merchants.id`: `RESTRICT`. A merchant cannot be removed while products still refer to it. This protects catalog history and prevents accidental cascading deletion of the catalog.
- `carts.merchant_id -> merchants.id`: `RESTRICT`. Merchant deletion cannot silently erase customer cart state.
- `inventory.product_id -> products.id`: `CASCADE`. Inventory is dependent state with no meaning without its product. This is appropriate for the current MVP, but historical inventory ledgers would need a different lifecycle.
- `cart_items.cart_id -> carts.id`: `CASCADE`. Items are owned by the cart; deleting a cart removes its draft items.
- `cart_items.product_id -> products.id`: `RESTRICT`. A referenced product cannot be deleted while cart items retain it. This preserves cart references and prevents broken commerce history.

Without foreign keys, orphan rows, carts for nonexistent merchants, and inventory for nonexistent products could be written by any caller. Cascades must be limited to genuinely dependent draft data; they should not be used for orders, payments, or audit history.

## 6. Money Handling

The application uses `Decimal` in Python and `NUMERIC(12, 2)` in PostgreSQL. `float` uses binary representation, so operations such as adding ten-cent values can produce values that are mathematically surprising. That is unacceptable for totals, discounts, tax, and payment reconciliation.

`Decimal("999.99")` represents a decimal amount; PostgreSQL `NUMERIC` stores an exact decimal value subject to declared precision and scale. The current scale allows two fractional digits and up to twelve total digits. It is suitable for the MVP but should be matched to supported currencies and maximum order values before production.

A senior-level answer is: use exact decimal arithmetic for money, define rounding at business boundaries, calculate from database-authoritative prices, and persist the amount used for a transaction. Do not trust an LLM-generated amount or a client-provided cart total.

The current code captures `CartItem.unit_price` from `Product.price` at item creation. That supports historical price stability, but checkout/order totals are not implemented yet.

## 7. UUID Decision

UUIDs reduce sequential ID guessing and can be generated without a central sequence coordinator. This helps future services, imports, and distributed workers. They are not authorization: a UUID must still be checked against the authenticated principal and merchant scope.

Compared with integer/bigint IDs, UUIDs consume more index space and random UUIDs can reduce B-tree locality. Bigints are compact and fast but predictable and require coordinated allocation. At current MVP scale UUID storage is reasonable. If write volume makes random-index locality measurable, time-ordered UUIDs or another key strategy can be considered.

## 8. Timestamp Decision

`server_default=func.now()` lets PostgreSQL create the initial timestamp. `onupdate=func.now()` tells SQLAlchemy to include an update expression when the row is changed. Timezone-aware columns represent UTC-capable timestamps.

This is more consistent across multiple application instances than trusting each host clock. It also gives database auditing a single time authority. The design still needs an explicit policy for immutable creation time, update triggers, and event timestamps before production audit requirements are introduced.

## 9. Product Design

A product belongs to exactly one merchant through `merchant_id`. SKU uniqueness is scoped to `(merchant_id, sku)` because two independent merchants may legitimately use the same internal SKU. Making SKU globally unique would create unnecessary coupling and complicate merchant onboarding.

The database check `price >= 0` and Pydantic `Field(ge=0)` serve different boundaries:

- Pydantic gives a fast, useful API error before a database round trip.
- PostgreSQL protects all writers, including scripts, migrations, future workers, and race conditions.

The service additionally checks merchant existence, merchant active status, and merchant-scoped SKU uniqueness. Concurrent requests can still race between a read-before-create check and the unique index; production code must catch `IntegrityError` and translate it safely.

## 10. Inventory Design

`product_id` is both a foreign key and unique, giving the MVP a one-to-one product/inventory relationship. This keeps the first model simple and makes lookup by product direct.

`quantity >= 0` exists in Pydantic, service logic, and PostgreSQL. Defense in depth matters because no single layer sees every write path.

The current implementation supports increase, decrease, and availability checks, but the read-modify-write path is not atomic. Two requests can read the same quantity and both approve a purchase. Future options include row-level locking with `SELECT ... FOR UPDATE`, an atomic conditional update such as decrement-where-quantity-is-sufficient, reservation columns, idempotency keys, and a transaction boundary spanning cart/order state. These are not implemented yet.

The original broad design mentioned `reserved_quantity`; the current model has only `quantity`. That is a documented scope gap, not an undocumented feature.

## 11. Cart Design

`CartStatus` is a database-backed lifecycle state:

- `ACTIVE`: mutable shopping cart.
- `CHECKED_OUT`: checkout completed or committed.
- `ABANDONED`: no longer expected to proceed.

An enum prevents arbitrary strings and makes invalid transitions visible. It also creates migration work whenever states change.

A cart belongs to a merchant and contains a UUID `customer_id`. There is no customer entity or authentication, so this field is an identifier only. Cart items reference a cart and product. `unit_price` captures the product price at insertion time rather than repeatedly reading current catalog price. That is necessary for historical and checkout correctness when a merchant changes price later.

Current gaps: no cart service, no cart API, no explicit cart/product merchant consistency check, no database unique constraint preventing duplicate cart items, and no order snapshot.

## 12. Pydantic Schemas

Current schema groups include merchant, product, inventory, cart, and cart item.

- `Create` contains required input for a new record.
- `Update` uses optional fields with `exclude_unset=True` semantics so omitted values remain unchanged.
- `Response` contains persisted identity and timestamps and uses `ConfigDict(from_attributes=True)` for ORM serialization.

Important validators include UUID parsing, `EmailStr`, `Decimal`, `Field(gt=0)` for positive quantities, and non-negative price/quantity fields. `email-validator` is a required runtime dependency because Pydantic `EmailStr` delegates actual validation to it.

Pydantic validation is an API boundary, not a substitute for PostgreSQL constraints. It can be bypassed by another writer and cannot prevent concurrent races.

Known schema issue: `CartItemResponse` declares `subtotal`, but the current `CartItem` ORM model has no `subtotal` attribute. That response should not be used until subtotal is explicitly computed or modeled.

## 13. Repository Layer

Repositories currently present:

- `MerchantRepository`: create, get by ID, get by slug, list, update, delete.
- `ProductRepository`: create, get by ID, get by merchant-scoped SKU, list by merchant, update, delete.
- `InventoryRepository`: create, get by ID, get by product, update, save, delete.
- `CartRepository`: create, get by ID, active cart by merchant/customer, list by merchant, update, delete.
- `CartItemRepository`: create using authoritative product price, get by ID, get by cart/product pair, list by cart, update, delete.

They use SQLAlchemy `select()` and a supplied `Session`. They should not accept FastAPI `Request`, construct engines, call payment providers, execute agent prompts, or decide policy workflows.

Current risk: repository methods generally commit independently. That makes simple CRUD easy, but a service that creates several records cannot guarantee all-or-nothing behavior if a later step fails. A future refactor should separate `flush` from `commit` and let the service own transaction scope.

Merchant scoping is explicit in product SKU and list queries and in active-cart lookup. It is not universal: cart-item creation does not verify cart/product merchant ownership, and no authentication context exists.

## 14. Service Layer

Implemented services:

- `MerchantService`: duplicate slug prevention, retrieval, listing, update slug collision checks, deletion. It currently has compatibility aliases for both `create_merchant`/`create`-style APIs.
- `ProductService`: merchant existence and active checks, SKU uniqueness, price validation, merchant-scoped lookup/listing, pagination limits, updates, and deletion.
- `InventoryService`: product existence/active checks, one-inventory enforcement, quantity validation, stock checks, increase/decrease, and overselling guard at the application read level.

The merchant API calls the service layer and maps `ValueError` to HTTP errors. Routes do not contain SQL.

Business rules should stay here because they combine multiple repositories and domain facts. The service layer should eventually own transaction boundaries, authorization context, inventory reservations, order creation, and idempotency.

Current gap: `CartRepository` and `CartItemRepository` exist, but no corresponding cart service or API is wired. That is a deliberate incomplete slice, not a feature to infer from repository presence.

## 15. Testing Architecture

`backend/tests/conftest.py` creates a connection-level transaction:

```python
connection = engine.connect()
transaction = connection.begin()

session = Session(
    bind=connection,
    join_transaction_mode="rollback_only",
)
```

The fixture yields the session, then closes it, rolls back, and closes the connection. This prevents repository methods that call `commit()` from permanently committing test data inside the outer transaction. It is useful for fast integration tests against a real PostgreSQL schema.

An autouse API fixture overrides FastAPI `get_db` with a rollback-only session. This was added after API tests polluted the development database. It protects future API runs but does not remove rows already present.

Current test categories:

| File | Collected tests |
|---|---:|
| `test_health.py` | 1 |
| `test_merchant_api.py` | 13 |
| `test_merchant_repository.py` | 5 |
| `test_merchant_service.py` | 9 |
| `test_product_repository.py` | 9 |
| `test_product_service.py` | 9 |
| `test_inventory.py` | 2 |
| `test_inventory_repository.py` | 9 |
| `test_inventory_service.py` | 10 |
| `test_cart_repository.py` | 9 |
| `test_cart_item_repository.py` | 9 |
| `test_schemas.py` | 2 |
| **Total** | **86** |

The historical progression of 9, 27, 36, 45, 62, and 73 tests is visible in session history, not as a reproducible repository artifact. The exact meaning of every historical checkpoint cannot be independently established from current files. Current verified status is 86 collected, 85 passing, 1 failing.

Test gap: use a dedicated `ai_growth_test` database or CI database. Do not run destructive cleanup against the development database. Migrations should be applied to the test database before tests.

## 16. Debugging Timeline

The following items combine repository evidence with historical implementation/debugging records. Items that are not represented by final code are explicitly historical.

### Problem: Wrong Base import

- **Symptom/error:** model or migration imports could not find the expected Base module.
- **Root cause:** the actual Base is in `backend/app/database/base.py`; an earlier attempted path treated it as if it were in another module.
- **Diagnosis:** inspect the package tree and import the concrete Base location.
- **Fix:** use the actual database package and relative model imports.
- **Lesson/prevention:** establish one canonical import path and verify `Base.metadata` before generating migrations.
- **Status:** Historical implementation/debugging decision; the final models use `..database.base`.

### Problem: Wrong config import

- **Symptom/error:** root-level imports could not find `app.config` or database settings.
- **Root cause:** mixed `app...` and `backend.app...` namespaces depending on working directory.
- **Fix:** normalize application internals to package-relative imports and make settings locate `backend/.env` from `__file__`.
- **Lesson:** test both `backend.app.main` from the repository root and `app.main` from `backend` if both commands are documented.

### Problem: Alembic configuration missing or pointing at the wrong directory

- **Symptom/error:** missing `script_location` or missing `alembic/env.py`.
- **Root cause:** an accidental root `alembic/` directory competed with the real `backend/alembic/` directory.
- **Fix:** keep the root `alembic.ini`, set `script_location = %(here)s/backend/alembic`, set `prepend_sys_path = %(here)s/backend`, and remove the accidental root directory when empty.
- **Lesson:** configuration location is part of the migration architecture; verify `alembic current` and `alembic heads` from the documented working directory.

### Problem: Alembic generated an empty migration

- **Symptom/error:** migration contained `pass`; database had only `alembic_version`.
- **Root cause:** Alembic imported `app.database.base.Base`, while model package imports created a separate `backend.app...` namespace and therefore a different metadata object.
- **Fix:** import `from app import models` before assigning `target_metadata`, then normalize model/package imports to relative imports.
- **Lesson:** successful model imports do not prove they are registered on the same Base. Verify exact table names before autogeneration.

### Problem: Orphaned PostgreSQL enum

- **Symptom/error:** `DuplicateObject: type "cart_status" already exists` while creating the first table.
- **Root cause:** a failed migration left the named enum type behind even though table creation rolled back. PostgreSQL DDL is transactional in this context, but enum/type creation behavior during the failed migration left an object that the next attempt encountered.
- **Fix:** the migration uses SQLAlchemy PostgreSQL `ENUM(..., create_type=False)` and `create(..., checkfirst=True)` before table creation; downgrade drops the type conditionally.
- **Lesson:** named PostgreSQL types deserve explicit migration handling and failure cleanup. Do not assume a failed migration leaves zero schema objects.
- **Status:** This is a migration-specific idempotence repair, not a model change.

### Problem: `EmailStr` dependency

- **Symptom/error:** `ModuleNotFoundError: No module named 'email_validator'` during schema collection.
- **Root cause:** Pydantic `EmailStr` has an optional runtime dependency.
- **Fix:** add `email-validator` to requirements and install it in `.venv`.
- **Prevention:** run imports/tests in the project interpreter after dependency changes.

### Problem: Cart schema/package export mismatch

- **Symptom/error:** `cannot import name 'CartCreate'`; `cart_item.py` was empty while `cart.py` contained cart-item classes.
- **Root cause:** schema classes were in the wrong module and package exports were duplicated.
- **Fix:** put cart classes in `cart.py`, cart-item classes in `cart_item.py`, and define clean package exports.

### Problem: Missing pytest imports

- **Symptom/error:** `NameError` for `pytest`, `ValidationError`, or `uuid4`.
- **Root cause:** test file used symbols without importing them.
- **Fix:** add the explicit imports.

### Problem: Product test merchant ID/syntax mismatch

- **Symptom/error:** missing `merchant_id` or invalid walrus expression syntax in a test.
- **Root cause:** `ProductCreate` requires ownership and the test used an invalid assignment expression inside a keyword argument.
- **Fix:** supply `merchant_id` and use a normal `uuid4()` import/call. Add `sku` to `ProductUpdate` because the service tests update SKU.

### Problem: `pytest` not recognized

- **Symptom/error:** PowerShell `CommandNotFoundException: pytest`.
- **Root cause:** the virtual environment's Scripts directory was not available on the current shell PATH.
- **Fix:** use `python -m pytest` or `.venv\Scripts\pytest.exe`; activate the environment for interactive work.

### Problem: Inventory service missing `save`

- **Symptom/error:** `AttributeError: InventoryRepository has no attribute save`.
- **Root cause:** stock increase/decrease mutated an entity and called a repository method that did not exist.
- **Fix:** add `save()` with add, commit, refresh behavior.

### Problem: Merchant service module/API mismatch

- **Symptom/error:** missing `merchant_service` module and later missing `create`/`get_by_id` methods.
- **Root cause:** implementation was in `merchant_services.py` with longer method names while tests imported the singular module and shorter names.
- **Fix:** add a compatibility module and aliases.

### Problem: Uvicorn root import failure

- **Symptom/error:** `ModuleNotFoundError: No module named 'app'` when running `backend.app.main:app` from the repository root.
- **Root cause:** mixed package import conventions.
- **Fix:** convert internal imports to relative imports and verify both launch contexts.

### Problem: API tests polluted the development database

- **Symptom/error:** API test interruption was followed by service list failure: expected 2 merchants, found 22.
- **Root cause:** module-level `TestClient` used production `get_db`; API repository commits persisted rows.
- **Fix:** autouse rollback-only FastAPI dependency override.
- **Remaining issue:** historical rows remain in the development database; a dedicated test database is required for clean repeatability.

### Problem: Starlette/httpx warning

- **Symptom:** `StarletteDeprecationWarning` says the installed TestClient integration uses a deprecated httpx path.
- **Status:** warning only; tests still execute. It has not been fixed.
- **Prevention:** revisit compatible FastAPI/Starlette/httpx versions or the project’s supported test-client stack after confirming upstream compatibility. Do not change dependencies casually.

## 17. Migration History and Commands

Relevant files:

- Root `alembic.ini`: selects `backend/alembic` and adds backend to the import path.
- `backend/alembic/env.py`: loads settings, imports models, assigns `Base.metadata`, and runs online/offline migrations.
- `backend/alembic/versions/739b5372ffff_create_commerce_schema.py`: creates the five tables and named enum.

Useful commands from the repository root:

```powershell
.\.venv\Scripts\alembic.exe current
.\.venv\Scripts\alembic.exe heads
.\.venv\Scripts\alembic.exe check
.\.venv\Scripts\alembic.exe revision --autogenerate -m "describe change"
.\.venv\Scripts\alembic.exe upgrade head
```

`current` reports the database revision. `heads` reports migration graph heads. `check` compares metadata against the database without generating a file. `revision --autogenerate` compares metadata to the connected schema. `upgrade head` applies revisions.

Do not use `Base.metadata.create_all()` as production schema authority. It cannot express reviewed upgrade/downgrade history and can make environments drift. Alembic migration files are the reproducible record.

## 18. Security Review

### Implemented

- Local `.env` is ignored by Git.
- `.env.example` contains placeholders.
- Application settings load the environment file without logging its value.
- SQLAlchemy uses parameterized expressions rather than string-built SQL.
- Pydantic validates UUIDs, emails, prices, and quantities at API/schema boundaries.
- Database constraints enforce key invariants.
- Product SKU lookups are merchant-scoped.
- Product, inventory, cart, and cart-item values are not sourced from an LLM.

### Not implemented

- Authentication.
- Authorization and role checks.
- Tenant isolation at the authenticated request boundary.
- Customer identity verification.
- Rate limiting.
- Audit trail.
- Secret manager integration.
- Payment webhook verification.
- Production database TLS/least-privilege configuration.

A UUID is not authorization. Merchant A must not be able to request Merchant B data merely because the ID is known; that enforcement must be added at the service boundary using authenticated principal and merchant context.

## 19. Failure Handling

Current handling includes:

- Pydantic 422 responses for malformed request data.
- Service `ValueError` for missing merchants/products, duplicate slugs/SKUs, inactive entities, invalid quantities, and overselling attempts.
- Merchant route translation of selected `ValueError` cases to HTTP 409.
- 404 responses for missing merchant API records.
- Database check constraints for non-negative price/quantity and positive cart-item quantity.
- Central unexpected exception handler returning a generic 500 response and logging the traceback.

Missing or incomplete handling:

- Consistent `IntegrityError` translation for concurrent duplicate writes.
- Explicit rollback on all production request exceptions.
- Structured domain error types.
- Cart-item merchant and cart-state validation.
- Atomic inventory reservation.
- Idempotent checkout/payment handling.
- Safe error mapping for foreign-key failures.
- Retry policy for transient database errors.

## 20. Performance and Scalability

Current positive choices:

- PostgreSQL connection pooling with `pool_pre_ping`.
- Indexes on merchant slug, product merchant ID, and merchant/SKU.
- Pagination parameters with bounds on merchant/product listings.
- SQLAlchemy `select()` queries.
- Direct lookup paths for product and inventory.

Current risks:

- Random UUID indexes cost more than sequential integer indexes.
- Repository commits on every operation prevent efficient multi-step transactions.
- Inventory read-modify-write can race.
- Relationship loading strategy is not explicitly tuned; future list endpoints should avoid N+1 queries.
- Cart-item creation queries product price but does not validate cart ownership or availability.
- No caching, search index, or read model exists; that is appropriate before measurement.

Scale only after measuring query latency, lock contention, pool exhaustion, and endpoint throughput. Future options include targeted eager loading, composite indexes based on actual plans, atomic inventory updates, read replicas, background jobs, and search infrastructure.

## 21. Observability

Current logging is basic Python logging configured by `configure_logging()`. The lifespan logs application start/stop. The exception handler logs unexpected API errors without returning internal details to callers.

Not present:

- Structured JSON logging.
- Request IDs/correlation IDs.
- Trace propagation.
- Database query metrics.
- Business metrics such as inventory failures or conversion.
- Central log aggregation.
- Alerting.

The current code should not log passwords, `DATABASE_URL`, customer identifiers unnecessarily, payment data, or full sensitive payloads. Add structured request/trace context before introducing agent and payment workflows.

## 22. Data Privacy

Current data includes merchant names/emails, product catalog information, customer UUID references, carts, prices, and inventory. Merchant email and customer identifiers are potentially personal or sensitive. Product prices and inventory can be commercially sensitive.

Credentials belong in environment variables or a secret manager, never logs or source control. Payment card data should not be stored by this application when Razorpay or another provider handles payment collection. Store provider references and verified payment outcomes, not card numbers or CVV.

There is currently no retention, deletion, consent, access logging, or customer privacy workflow.

## 23. Cost Tradeoffs

| Technology | Development cost | Infrastructure/operations | Why it fits now |
|---|---|---|---|
| FastAPI | Low to medium | Low for a single service | Typed APIs and future agent integration |
| PostgreSQL | Medium | Higher than SQLite, but standard relational DB operations | Correctness for commerce state |
| SQLAlchemy | Medium | Low runtime overhead when used carefully | Mature mapping and PostgreSQL support |
| Alembic | Low after setup | Low | Reproducible schema changes |
| Pydantic | Low | Low | Clear validation and serialization |
| Pytest | Low | Low | Fast regression feedback |

The expensive risks later are payment reliability, database contention, high-volume search, LLM calls, observability, and operational support. Adding Redis, vectors, queues, or microservices before those costs are demonstrated would increase complexity without current evidence.

## 24. Rebuild From Scratch

The following is a clean-room sequence, based on current architecture rather than a claim that every historical command is preserved.

### Step 1: Create the repository

**What:** create the root repository and Git ignore rules.

**Files:** `README.md`, `.gitignore`, `backend/`.

**Commands:**

```powershell
New-Item -ItemType Directory backend, documentation, docs
New-Item -ItemType File .gitignore, README.md
```

**Verify:** `Get-ChildItem -Force`.

**Common failure:** creating files under the wrong working directory. Confirm `$PWD`.

### Step 2: Create the virtual environment

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
```

Verify with `python -c "import fastapi, sqlalchemy, alembic; print('imports ok')"`.

### Step 3: Create packages

Create `__init__.py` files under `backend/app`, `api`, `database`, `models`, `schemas`, `repositories`, `services`, `tests`, `agent`, `guardrails`, and `integrations`.

Verify with `Get-ChildItem backend\app -Recurse`.

### Step 4: Configure environment

Create `backend/.env.example` with placeholders and a local ignored `backend/.env` containing the real local URL. Never print the URL.

The URL shape is:

```text
postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE
```

Verify by importing settings, not by printing the secret: `python -c "from backend.app.config import settings; print(bool(settings.database_url))"`.

### Step 5: Create Base and sessions

Create `database/base.py`, `database/session.py`, and `database/dependencies.py`. Use one engine, one session factory, `pool_pre_ping=True`, and a generator dependency that closes sessions.

Verify with a `SELECT 1` query and then run a health test.

### Step 6: Create models

Create Merchant, Product, Inventory, Cart, and CartItem with UUID keys, typed SQLAlchemy fields, relationships, database checks, foreign keys, timestamps, numeric prices, and the named cart enum.

Verify with:

```powershell
python -c "from backend.app.database.base import Base; from backend.app import models; print(sorted(Base.metadata.tables))"
```

Expected table names: `cart_items`, `carts`, `inventory`, `merchants`, `products`.

### Step 7: Configure Alembic

Create root `alembic.ini` with:

```ini
[alembic]
script_location = %(here)s/backend/alembic
prepend_sys_path = %(here)s/backend
sqlalchemy.url =
```

Create `backend/alembic/env.py`, import settings, Base, and models before assigning `target_metadata`, then configure online/offline migration execution.

Verify `alembic current` and `alembic heads`.

### Step 8: Generate and inspect migration

```powershell
alembic revision --autogenerate -m "create commerce schema"
```

Inspect the generated file for all five tables, enum creation, foreign keys, checks, unique constraints, indexes, and reverse operations. Only then run `alembic upgrade head`.

Verify `alembic check`.

### Step 9: Create schemas

Implement separate create/update/response Pydantic classes. Add `email-validator` when using `EmailStr`. Verify invalid email, negative price, and non-positive quantity cases.

### Step 10: Create repositories

Inject `Session`; implement `select()` queries and CRUD methods. Verify merchant, product, inventory, cart, and cart-item tests. Prefer `flush()` over `commit()` once service-owned transactions are introduced.

### Step 11: Create services

Implement merchant, product, and inventory rules. Add cart service only when cart business rules are defined. Verify inactive entities, duplicate scoped identifiers, pagination, and stock checks.

### Step 12: Create API routes

Create health and merchant routes. Register them only after constructing the FastAPI app. Verify root, health, OpenAPI, and merchant endpoint behavior.

### Step 13: Create isolated tests

Use a dedicated test PostgreSQL database. Apply migrations to it. Use connection-level transactions and rollback-only sessions, and override FastAPI `get_db` for API tests.

### Step 14: Run verification

```powershell
.\.venv\Scripts\python.exe -m pytest -q
alembic check
alembic current
```

Expected clean-room result: all tests pass, no schema drift, and current revision equals head.

## 25. Rebuild the Database From Scratch

Use a dedicated database, not the development database:

```sql
CREATE DATABASE ai_growth_test;
```

Configure a test-only URL through an environment variable or test settings source. Do not put the password in this document or source control.

Then:

```powershell
alembic current
alembic heads
alembic revision --autogenerate -m "create commerce schema"
alembic upgrade head
alembic check
```

Verify tables and constraints through SQLAlchemy inspection. Verify the `cart_status` enum labels and foreign keys. Do not use `Base.metadata.create_all()` for production schema management. Do not stamp a revision unless the database schema is known to match it. If a migration fails, inspect the database for leftover named types before retrying.

## 26. Rebuild Testing From Scratch

1. Create `backend/tests/conftest.py`.
2. Configure a dedicated test database and apply Alembic migrations.
3. Build a rollback-only `db` fixture.
4. Add merchant repository tests.
5. Add product repository tests.
6. Add inventory repository tests.
7. Add cart and cart-item repository tests.
8. Add merchant/product/inventory service tests.
9. Add API tests with a dependency override and rollback.
10. Add schema validation tests.
11. Run focused files during development, then the full suite.

Commands:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest backend\tests\test_product_repository.py -q
.\.venv\Scripts\python.exe -m pytest backend\tests\test_merchant_api.py -q
alembic check
```

A clean test system should never depend on old rows in a development database. The current fixture protects future API runs but the existing database data must be handled outside automated destructive test setup.

## 27. Current State

### Completed

- FastAPI foundation and health route.
- Environment settings and ignored local environment file.
- PostgreSQL SQLAlchemy engine/session/base.
- Five mapped tables and relationships.
- Alembic migration and enum handling.
- Merchant API.
- Merchant/product/inventory services.
- Five repositories.
- Pydantic schemas.
- 86 collected tests covering most current slices.

### Partially completed

- Cart persistence exists, but cart service/API does not.
- Test isolation exists, but the configured database is not a clean dedicated test database.
- Error handling exists, but database exception translation is incomplete.
- Inventory safeguards exist, but updates are not concurrency-safe.
- Merchant scoping exists in selected queries, but authorization does not exist.

### Not started

- Authentication and authorization.
- Orders, payments, Razorpay, checkout idempotency.
- Agent orchestration and tool calling.
- Search/recommendations/RAG.
- Guardrails, approvals, audit, analytics.
- Production deployment and observability platform.

### Known technical debt and risks

- Stale `backend/alembic.ini` contains hard-coded credentials.
- Repository methods commit independently.
- Development data contaminates tests.
- `CartItemResponse.subtotal` is not backed by the ORM model.
- No database unique constraint for `(cart_id, product_id)`.
- Cart-item repository lacks business validation.
- Inventory writes can race.
- Current test baseline is 85/86, not fully green.
- Existing Starlette/httpx warning remains.

## 28. First 50% Checklist

- [ ] Explain the client-to-database architecture.
- [ ] Explain why the backend is authoritative over LLM output.
- [ ] Explain FastAPI router/service/repository separation.
- [ ] Explain environment-based settings.
- [ ] Explain why secrets are not committed.
- [ ] Explain PostgreSQL selection.
- [ ] Explain SQLAlchemy engine and session lifecycle.
- [ ] Explain `DeclarativeBase` and metadata.
- [ ] Explain Alembic `target_metadata`.
- [ ] Explain migration inspection before upgrade.
- [ ] Explain UUID primary keys.
- [ ] Explain Decimal and NUMERIC.
- [ ] Explain server timestamps.
- [ ] Explain merchant fields and slug uniqueness.
- [ ] Explain merchant-scoped product SKU.
- [ ] Explain product price constraints.
- [ ] Explain one-to-one inventory.
- [ ] Explain stock non-negativity.
- [ ] Explain concurrent inventory race conditions.
- [ ] Explain cart lifecycle enum.
- [ ] Explain captured cart-item unit price.
- [ ] Explain foreign-key delete behavior.
- [ ] Explain Pydantic Create/Update/Response schemas.
- [ ] Explain `from_attributes`.
- [ ] Explain EmailStr and `email-validator`.
- [ ] Explain repositories and `select()`.
- [ ] Explain why repositories should not own workflows.
- [ ] Explain service business rules.
- [ ] Explain current transaction-boundary limitations.
- [ ] Explain FastAPI dependency injection.
- [ ] Explain rollback-only testing.
- [ ] Use a dedicated test database.
- [ ] Run focused pytest files.
- [ ] Run full pytest.
- [ ] Run `alembic check`.
- [ ] Identify authentication as missing.
- [ ] Identify authorization as missing.
- [ ] Identify payment and audit as future work.

## 29. Senior Interview Questions

### Why PostgreSQL?

**Ideal answer:** Commerce state is relational and transactional. PostgreSQL gives foreign keys, checks, unique constraints, numeric money, enums, and reliable transactions. A document store or cache would not replace those guarantees.

**Why asked:** Tests data modeling and consistency judgment.

**Follow-up:** How would you scale reads? Answer with measurement-led indexes, replicas, caching, and search only when justified.

### Why FastAPI?

**Ideal answer:** It provides typed request validation, dependency injection, OpenAPI, and a productive Python API surface compatible with future AI tooling.

**Follow-up:** Why not async SQLAlchemy now? Because the current workload and code are synchronous; switching stacks without a measured need adds complexity.

### Why SQLAlchemy 2.x typed ORM?

**Ideal answer:** It provides mature PostgreSQL mapping and explicit typed models with modern `select()` APIs and Alembic metadata.

**Follow-up:** What is the session identity map and why does it matter? It makes transaction/session lifecycle correctness essential.

### Why repository and service layers?

**Ideal answer:** Repositories isolate persistence mechanics; services enforce business rules and coordinate transactions. This prevents API handlers and future agent tools from bypassing domain rules.

**Follow-up:** What is wrong with repositories committing? It prevents larger service workflows from being atomic; future code should let services own commit/rollback.

### Why UUID instead of bigint?

**Ideal answer:** UUIDs are harder to guess and can be generated across instances, at the cost of larger, less locality-friendly indexes.

**Follow-up:** Are UUIDs authorization? No.

### Why Decimal instead of float?

**Ideal answer:** Binary float cannot exactly represent many decimal fractions. Decimal plus PostgreSQL NUMERIC preserves monetary correctness, with explicit rounding policy.

### Why database constraints and Pydantic validation?

**Ideal answer:** Pydantic improves client feedback; database constraints protect every writer and enforce invariants under concurrency.

### Why server timestamps?

**Ideal answer:** PostgreSQL provides one authoritative clock across application instances and avoids host-clock differences.

### Why Alembic instead of `create_all()`?

**Ideal answer:** Alembic provides reviewed, ordered, reproducible schema evolution. `create_all()` is not a migration history.

### How are database tests isolated?

**Ideal answer:** A dedicated database plus connection-level transaction and rollback-only session. API dependencies are overridden. Existing development data must never be assumed absent.

### What happens when two customers buy the last item?

**Ideal answer:** A read-check-write implementation can oversell. Use a transaction with row lock or an atomic conditional update, then persist reservation/order state and handle retries/idempotency.

### Why CASCADE here but RESTRICT there?

**Ideal answer:** Cascade only for dependent draft data such as cart items. Restrict deletion when the child preserves business history or should prevent accidental data loss.

### How prevent merchant A reading merchant B data?

**Ideal answer:** Authenticate the request, derive merchant context from authorization, and require every service/repository query to include that scope. IDs alone are insufficient.

### How would you make checkout idempotent?

**Ideal answer:** Require an idempotency key, persist request/result state, use a transaction and unique key, and make payment/order transitions retry-safe.

### Where does authentication go?

**Ideal answer:** FastAPI dependencies establish the principal; services receive authorized merchant/customer context and enforce object-level access. It is not implemented currently.

## 30. Final Architectural Review

### Done well

- Clear intended layering.
- PostgreSQL is treated as commerce source of truth.
- Typed SQLAlchemy 2.x models are explicit.
- Money uses Decimal/NUMERIC.
- Critical invariants are represented in the database.
- Alembic metadata discovery was corrected and verified.
- Merchant/product/inventory behavior has meaningful tests.
- API tests now have rollback isolation for future runs.

### Over-engineered or premature

- Compatibility aliases and duplicate service module naming add temporary complexity.
- Some extensive inline explanatory comments do not belong in production model files.
- The future architecture discusses many systems that are not yet needed.

### Under-engineered

- Test database isolation.
- Service-owned transactions.
- Concurrent inventory updates.
- Authorization and merchant tenant enforcement.
- Cart business rules and cart-item uniqueness.
- Database exception translation.
- Structured observability.

### Keep unchanged for now

- PostgreSQL.
- FastAPI.
- SQLAlchemy 2.x.
- Alembic as schema authority.
- Decimal/NUMERIC.
- Database constraints and foreign keys.
- Thin API routes and service boundary.

### Priorities

- **P0:** Stop using development data as the test database; establish a dedicated migrated test database. Add authentication/authorization before exposing multi-merchant data.
- **P1:** Move commit/rollback ownership to services; handle `IntegrityError`; make inventory decrement atomic; finish cart validation and uniqueness.
- **P1:** Remove or neutralize stale hard-coded credential configuration in `backend/alembic.ini` before production use.
- **P2:** Add orders, payment state machine, webhook verification, idempotency, audit events, and structured request tracing.
- **P2:** Add product/inventory/cart API contracts only after service semantics are stable.
- **P3:** Optimize indexes, caching, search, and UUID locality from measurements.

### What not to change yet

Do not add microservices, Redis, Kafka, Kubernetes, vector search, or an LLM agent until the transactional commerce boundaries, authorization, and test database are reliable. Those technologies solve later scale or capability problems and would obscure current correctness gaps.

## Phase 1 Completion Verdict

The first foundation is **substantially implemented but not complete or production-ready**. The current repository demonstrates a credible FastAPI/PostgreSQL/SQLAlchemy/Alembic data-layer direction and has broad tests, but the verified baseline is `85 passed, 1 failed, 1 warning`. The failure is caused by persisted development test data, which is itself an important test architecture defect.

The honest status is approximately **45–50% of the planned MVP**: the relational foundation and early merchant/catalog/inventory behavior exist; the agent, secure tenant boundary, checkout, order/payment consistency, auditability, concurrency guarantees, and operational readiness remain.

Before starting the remaining 50%, establish a clean dedicated test database, remove stale credential-bearing configuration, define service-owned transaction boundaries, fix cart consistency/response gaps, and design authentication/authorization. Only then should agent tools be allowed to invoke commerce actions.
