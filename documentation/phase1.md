Phase 1 — Project Foundation

Project: AI Growth & Agentic Commerce
Track: AI Growth & Agentic Commerce
Phase: 1 — Project Foundation
Objective: Establish a clean, scalable backend foundation that can support the AI commerce agent, commerce APIs, guardrails, Razorpay test-mode integration, audit trails, and the frontend.

1. Phase Overview

Phase 1 is about creating the backend skeleton of the project. We are not building the AI agent, payment flow, recommendation engine, or frontend yet.

The purpose of this phase is to make sure that the project has:

A clean repository structure

A working FastAPI backend

Environment-variable management

Configuration management

PostgreSQL connectivity

SQLAlchemy setup

Pydantic schemas

Basic API routing

Logging

Error handling

Health checks

A test setup

Git/GitHub hygiene

At the end of Phase 1, the application should start successfully and expose a health endpoint.

2. Phase 1 Goal

The target architecture after Phase 1 is:

                    ┌─────────────────────┐
                    │      Client         │
                    │ Frontend / Postman  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      FastAPI        │
                    │       main.py       │
                    └──────────┬──────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
           API Routers     Services       Health
                │
                ▼
          Database Layer
                │
                ▼
           PostgreSQL

The AI agent, payment system, guardrails, and business services will be plugged into this foundation in later phases.

3. Technology Stack

Backend

Python 3.11+

FastAPI

Uvicorn

Pydantic

Pydantic Settings

Database

PostgreSQL

SQLAlchemy 2.x

Alembic

Development

Git

GitHub

.env

pytest

HTTPX

Optional but Recommended

Docker

Docker Compose

Ruff

Black

4. Why FastAPI?

FastAPI is a good fit because the project will eventually expose APIs for:

Products
Customers
Cart
Orders
Payments
AI Agent
Approvals
Audit Logs
Analytics

FastAPI also provides:

Automatic OpenAPI documentation

Type validation

Pydantic integration

Async support

Easy API testing

Good integration with Python AI/ML libraries

The AI layer can therefore remain in Python while the frontend communicates with the backend through REST APIs.

5. Why PostgreSQL?

The application contains transactional data such as:

Products
Customers
Orders
Cart Items
Transactions
Approvals
Policies
Audit Logs

This data needs reliable persistence and relationships.

PostgreSQL will be the source of truth for commerce and financial state.

The LLM must never be treated as the source of truth for:

Product prices

Inventory

Order totals

Payment status

Approval status

Transaction status

The agent will request actions through backend tools/services, while PostgreSQL stores the authoritative state.

6. Initial Repository Structure

Create the project with the following structure:

ai-growth-agent/
│
├── backend/
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       └── health.py
│   │   │
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── session.py
│   │   │   └── base.py
│   │   │
│   │   ├── models/
│   │   │   └── __init__.py
│   │   │
│   │   ├── schemas/
│   │   │   └── __init__.py
│   │   │
│   │   ├── services/
│   │   │   └── __init__.py
│   │   │
│   │   ├── agent/
│   │   │   └── __init__.py
│   │   │
│   │   ├── guardrails/
│   │   │   └── __init__.py
│   │   │
│   │   ├── integrations/
│   │   │   └── __init__.py
│   │   │
│   │   └── utils/
│   │       └── __init__.py
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_health.py
│   │
│   ├── requirements.txt
│   └── .env.example
│
├── data/
│
├── docs/
│
├── .gitignore
├── README.md
└── docker-compose.yml

7. Directory Responsibilities

backend/app/main.py

Application entry point.

Responsibilities:

Create FastAPI application

Register routers

Configure startup/shutdown behavior

Configure global middleware if needed

It should remain small.

backend/app/config.py

Centralized application configuration.

It will eventually contain:

DATABASE_URL
LLM API key
RAZORPAY key
RAZORPAY secret
environment
debug mode
allowed origins

Do not hard-code secrets anywhere in the source code.

backend/app/api/

Contains HTTP/API-level logic.

Example:

api/
└── routes/
    ├── health.py
    ├── products.py
    ├── customers.py
    ├── cart.py
    ├── orders.py
    ├── payments.py
    ├── agent.py
    ├── approvals.py
    └── audit.py

Only health.py is needed in Phase 1.

backend/app/database/

Contains database configuration.

Eventually:

database/
├── session.py
├── base.py
└── dependencies.py

backend/app/models/

SQLAlchemy database models.

Later:

Product
Customer
Order
OrderItem
Cart
CartItem
Transaction
Approval
Policy
AuditLog

Only the foundation is required in Phase 1.

backend/app/schemas/

Pydantic request/response schemas.

Example later:

ProductCreate
ProductResponse
OrderCreate
OrderResponse
PaymentResponse
AgentRequest
AgentResponse

backend/app/services/

Business logic.

This is extremely important.

Avoid putting business logic directly inside FastAPI route functions.

Correct:

API Route
   ↓
Service
   ↓
Database

Not:

API Route
   ↓
100 lines of business logic
   ↓
Database

backend/app/agent/

Reserved for LangChain/LangGraph agent implementation.

Later it will contain:

agent/
├── agent.py
├── tools.py
├── prompts.py
└── state.py

Do not implement the full agent in Phase 1.

backend/app/guardrails/

Reserved for deterministic policy enforcement.

Later:

guardrails/
├── policy_engine.py
├── rules.py
└── validators.py

backend/app/integrations/

External services.

Later:

integrations/
├── razorpay.py
└── llm.py

This keeps external-service code isolated.

8. Create the Python Environment

From the project root:

python -m venv .venv

Activate it on Windows PowerShell:

.venv\Scripts\Activate.ps1

You should see something similar to:

(.venv) PS C:\...\ai-growth-agent>

Verify:

python --version

9. Install Phase 1 Dependencies

Create:

backend/requirements.txt

Add:

fastapi
uvicorn[standard]
pydantic
pydantic-settings
sqlalchemy
psycopg[binary]
alembic
python-dotenv
pytest
httpx

Install:

pip install -r backend/requirements.txt

Verify FastAPI:

python -c "import fastapi; print(fastapi.__version__)"

Verify SQLAlchemy:

python -c "import sqlalchemy; print(sqlalchemy.__version__)"

10. Environment Variables

Create:

backend/.env.example

Add:

APP_NAME=AI Growth Agent
APP_ENV=development
DEBUG=true

DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/ai_growth

LLM_API_KEY=
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=

Do not commit the real .env file.

Create:

backend/.env

with your local values.

Example:

APP_NAME=AI Growth Agent
APP_ENV=development
DEBUG=true

DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/ai_growth

LLM_API_KEY=
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=

The API keys can remain empty during Phase 1.

11. .gitignore

Create a root .gitignore:

# Python
__pycache__/
*.py[cod]
*.pyo

# Virtual environment
.venv/
venv/

# Environment variables
.env
.env.*

# Exceptions
!.env.example

# Testing
.pytest_cache/
.coverage
htmlcov/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Build
dist/
build/
*.egg-info/

# Logs
*.log

# Local databases
*.db

Important:

.env

must never be pushed to GitHub.

12. Application Configuration

Create:

backend/app/config.py

Use Pydantic Settings.

Conceptually:

Environment Variables
        ↓
Pydantic Settings
        ↓
Application Config
        ↓
FastAPI / Database / Services

The configuration should expose:

app_name
app_env
debug
database_url
llm_api_key
razorpay_key_id
razorpay_key_secret

This prevents configuration from being scattered throughout the project.

13. Create the FastAPI Application

Create:

backend/app/main.py

The initial application should:

Import FastAPI

Create the application instance

Register the health router

Provide a root endpoint

Conceptual structure:

from fastapi import FastAPI

app = FastAPI(
    title="AI Growth & Agentic Commerce API",
    version="0.1.0"
)

@app.get("/")
def root():
    return {
        "message": "AI Growth & Agentic Commerce API"
    }

Later, routers will be separated into their own files.

14. Health Check Endpoint

Create:

backend/app/api/routes/health.py

The endpoint:

GET /health

should return:

{
  "status": "ok"
}

A better response can eventually include:

{
  "status": "ok",
  "service": "ai-growth-agent",
  "environment": "development"
}

15. Register the Health Router

In main.py:

FastAPI
   ↓
include_router()
   ↓
health router

The resulting endpoint should be:

GET http://localhost:8000/health

16. Run the Backend

From the backend directory:

uvicorn app.main:app --reload

Expected output:

Uvicorn running on http://127.0.0.1:8000

Open:

http://127.0.0.1:8000

You should receive the root response.

Then:

http://127.0.0.1:8000/health

Expected:

{
  "status": "ok"
}

17. FastAPI Swagger Documentation

FastAPI automatically provides:

http://localhost:8000/docs

You should see:

AI Growth & Agentic Commerce API

GET /
GET /health

Also verify:

http://localhost:8000/redoc

This will be useful later for demonstrating the backend APIs.

18. PostgreSQL Setup

You have two options.

Option A — Local PostgreSQL

Install PostgreSQL locally and create:

Database:
ai_growth

Example:

Host: localhost
Port: 5432
Database: ai_growth
User: postgres
Password: <your-password>

Then:

DATABASE_URL=postgresql+psycopg://postgres:<password>@localhost:5432/ai_growth

Option B — Docker

Recommended if you want a reproducible development environment.

Create:

docker-compose.yml

Conceptually:

services:

  postgres:
    image: postgres:16
    container_name: ai_growth_postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: ai_growth
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:

Start:

docker compose up -d

Check:

docker ps

You should see the PostgreSQL container running.

19. SQLAlchemy Database Engine

Create:

backend/app/database/session.py

Responsibilities:

DATABASE_URL
      ↓
SQLAlchemy Engine
      ↓
Session Factory
      ↓
Database Dependency

The engine will connect to PostgreSQL.

The session factory will provide database sessions to FastAPI routes/services.

20. Database Base

Create:

backend/app/database/base.py

The SQLAlchemy declarative base will eventually be used by all models.

Conceptually:

Base
 │
 ├── Merchant
 ├── Product
 ├── Customer
 ├── Order
 ├── OrderItem
 ├── Transaction
 ├── Policy
 ├── Approval
 └── AuditLog

Phase 1 does not require implementing all these models.

21. Database Dependency

Eventually routes will use:

FastAPI Route
      ↓
get_db()
      ↓
SQLAlchemy Session
      ↓
Service
      ↓
Database

This ensures database sessions are properly created and closed.

22. Alembic Setup

Initialize Alembic:

alembic init alembic

This creates:

alembic/
├── versions/
├── env.py
├── script.py.mako
└── README

Alembic will handle database migrations.

Why migrations matter:

Instead of manually changing the database every time the schema changes:

Model change
    ↓
Migration
    ↓
Database schema update

Later, for example:

alembic revision --autogenerate -m "create product table"

and:

alembic upgrade head

23. Basic Error Handling

Do not allow random Python exceptions to become confusing API responses.

Eventually use consistent responses such as:

{
  "error": {
    "code": "PRODUCT_NOT_FOUND",
    "message": "Product does not exist"
  }
}

For Phase 1, establish the structure for centralized exception handling.

Potential future errors:

PRODUCT_NOT_FOUND
CUSTOMER_NOT_FOUND
INSUFFICIENT_STOCK
INVALID_CART
ORDER_NOT_FOUND
PAYMENT_FAILED
POLICY_VIOLATION
APPROVAL_REQUIRED

24. Logging

Add application logging.

At minimum, log:

Application startup
Application shutdown
API errors
Database errors
Important business events
Agent actions
Payment events

Do not log:

API keys
Passwords
Payment secrets
Sensitive credentials

Later the audit system will provide business-level traceability, while application logs provide technical debugging information.

These are different concepts.

25. Testing Setup

Create:

backend/tests/test_health.py

The first test should verify:

GET /health

returns:

HTTP 200

and:

{
  "status": "ok"
}

Run:

pytest

Expected:

1 passed

26. Phase 1 API Contract

At the end of Phase 1:

GET /

Purpose:

Verify that the API is running.

Response:

{
  "message": "AI Growth & Agentic Commerce API"
}

GET /health

Purpose:

Health check.

Response:

{
  "status": "ok"
}

27. Phase 1 Architecture

The complete Phase 1 architecture should look like:

                    ┌─────────────────────┐
                    │       Client        │
                    │ Browser / Postman   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      FastAPI        │
                    │                     │
                    │      main.py        │
                    └──────────┬──────────┘
                               │
                     ┌─────────┴─────────┐
                     │                   │
                     ▼                   ▼
                API Router          Configuration
                     │                   │
                     │                   ▼
                     │              Environment
                     │               Variables
                     │
                     ▼
                Services
                     │
                     ▼
              SQLAlchemy
                     │
                     ▼
                PostgreSQL

28. What We Are NOT Building in Phase 1

Do not start these yet:

❌ LangChain Agent
❌ RAG
❌ Vector Database
❌ Upselling model
❌ Cross-selling engine
❌ Razorpay integration
❌ Payment retry system
❌ Guardrail engine
❌ Human approval UI
❌ Merchant dashboard
❌ Customer frontend
❌ Fine-tuning
❌ Multi-agent architecture

They belong to later phases.

The purpose of Phase 1 is to create the foundation on which those components can be added cleanly.

29. Phase 1 Definition of Done

Phase 1 is complete only when all of the following are working:

Project

Git repository initialized

.gitignore created

Virtual environment created

Project structure created

README created

Backend

FastAPI installed

FastAPI application starts

Uvicorn works

/ endpoint works

/health endpoint works

Swagger /docs works

ReDoc /redoc works

Configuration

.env created locally

.env.example created

Secrets excluded from Git

Pydantic Settings configured

Database

PostgreSQL running

Database created

SQLAlchemy installed

Database engine configured

Session factory configured

Database dependency structure created

Alembic initialized

Testing

pytest installed

Health endpoint test written

Test passes

Code Quality

No hard-coded secrets

No unnecessary global state

Routes separated from business logic

Clear folder structure

Application starts without errors

30. Phase 1 Final Test

Run these commands.

Start database

docker compose up -d

Activate environment

.venv\Scripts\Activate.ps1

Start API

cd backend
uvicorn app.main:app --reload

Test health

Open:

http://localhost:8000/health

Expected:

{
  "status": "ok"
}

Test Swagger

Open:

http://localhost:8000/docs

Expected:

GET /
GET /health

Run tests

pytest

Expected:

1 passed

31. Git Commit

Once everything passes:

git status

Then:

git add .

Commit:

git commit -m "feat: initialize backend foundation"

Push:

git push origin main

32. Final Phase 1 Deliverable

At the end of Phase 1, your GitHub repository should contain:

ai-growth-agent/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/
│   │   ├── database/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── agent/
│   │   ├── guardrails/
│   │   └── integrations/
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
│
├── data/
├── docs/
├── docker-compose.yml
├── .gitignore
└── README.md

And the following should work:

                   PHASE 1 COMPLETE
                         │
                         ▼
                ┌─────────────────┐
                │    FastAPI      │
                └────────┬────────┘
                         │
                ┌────────▼────────┐
                │   PostgreSQL    │
                └────────┬────────┘
                         │
                ┌────────▼────────┐
                │   Health Check  │
                │       ✓         │
                └─────────────────┘