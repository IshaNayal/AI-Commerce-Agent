# High Level Architecture: Commerce Backend

## Overview
Phase 3 focused on building the core business logic and exposing it via a RESTful API. This phase bridges the gap between the raw Database Layer (Phase 2) and the outside world (Frontend/AI Agents).

## Architecture Pattern: 3-Tier Architecture
We strictly adhered to a standard 3-Tier Architecture, mapping perfectly to FastAPI's paradigm:

1. **Controllers (API Routes):**
   - Located in `backend/app/api/routes/`.
   - **Responsibility:** Handle HTTP requests, parse inputs via Pydantic, authenticate/authorize, call the appropriate Service, and return HTTP responses or raise HTTP exceptions.
   - **Rule:** Controllers are "thin". They contain zero business logic.

2. **Service Layer (Domain Logic):**
   - Located in `backend/app/services/`.
   - **Responsibility:** The "brain" of the application. This is where business rules live (e.g., "Cannot checkout an empty cart", "Deduct inventory when an order is placed").
   - **Rule:** Services are "fat". They orchestrate calls between different repositories, manage database transactions, and throw standard Python exceptions (`ValueError`, `RuntimeError`)—never HTTP exceptions.

3. **Data Access Layer (Repositories):**
   - Located in `backend/app/repositories/`.
   - **Responsibility:** Encapsulate all raw SQLAlchemy queries (`select`, `add`, `delete`).
   - **Rule:** Repositories only talk to the database. They do not know about HTTP or complex cross-domain business rules.

## Dependency Flow
`Request` -> `Router` -> `Service` -> `Repository` -> `Database`

By keeping this flow unidirectional and strictly segregated, we ensure that if we decide to swap out FastAPI for a different framework (or trigger logic via a CLI/Cron job instead of HTTP), the `Service` and `Repository` layers remain 100% untouched.
