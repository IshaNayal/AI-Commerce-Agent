# AI-Commerce-Agent

## Phase 1 Backend Foundation

The Phase 1 backend is a FastAPI application with Pydantic Settings, SQLAlchemy 2.x,
Alembic, and PostgreSQL configuration. Later commerce and agent features are not
implemented yet.

### Run locally

From the repository root in PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
Set-Location backend
uvicorn app.main:app --reload
```

Phase 1 expects PostgreSQL to be installed and running locally on port `5432`,
with the database and credentials configured in `backend/.env`.

The API is available at `http://127.0.0.1:8000`. The root endpoint, health check,
Swagger UI, and ReDoc are available at `/`, `/health`, `/docs`, and `/redoc`.

Run the tests from the repository root with:

```powershell
.venv\Scripts\python.exe -m pytest backend\tests -q
```

Alembic commands should be run from `backend`, for example:

```powershell
alembic upgrade head
```

An **agentic commerce platform** that uses AI to help merchants increase revenue through intelligent product discovery, upselling, cross-selling, conversational shopping, and AI-assisted checkout.

The system combines a **LangChain-based AI agent**, merchant product catalog, customer context, revenue intelligence, policy-based guardrails, human approval, Razorpay test-mode payments, and a complete audit trail.

The goal is not to build another shopping chatbot. The goal is to build an **AI agent that can reason about commerce and safely take bounded actions that can directly contribute to merchant revenue**.

---

## 1. Problem Statement

Traditional e-commerce requires customers to manually search products, compare options, add items to carts, and complete checkout.

At the same time, merchants have large amounts of product and transaction data but often do not have an intelligent system that can actively identify opportunities to increase revenue.

For example, a merchant may have:

* Customers purchasing running shoes but not sports socks
* Products with strong sales but low cross-sell rates
* Customers repeatedly purchasing complementary products
* Customers abandoning their checkout
* Products that could be bundled
* Opportunities for personalized recommendations

An AI agent can potentially identify these opportunities and act on them.

However, allowing an AI system to directly perform financial actions creates important safety concerns.

An unrestricted agent could:

* Give excessive discounts
* Create unauthorized payments
* Repeatedly retry transactions
* Launch expensive campaigns
* Make unexplained financial decisions

Therefore, the system must ensure that **every money-related action is explainable, bounded, gated, and auditable**.

---

# 2. Project Objective

The objective of this project is to build an **AI Commerce Agent** that can:

1. Understand customer shopping requests using natural language.
2. Search and understand a merchant's product catalog.
3. Recommend relevant products.
4. Identify upselling and cross-selling opportunities.
5. Build and manage a shopping cart.
6. Calculate order totals.
7. Analyze customer context when available.
8. Apply merchant-defined policies and limits.
9. Request human approval for sensitive actions.
10. Create payment orders using Razorpay Test APIs.
11. Handle payment failures gracefully.
12. Maintain a complete audit trail of agent decisions.
13. Provide merchants with revenue and agent-performance analytics.

---

# 3. Core Idea

The core workflow is:

```text
Customer
   ↓
Natural Language Request
   ↓
AI Commerce Agent
   ↓
Understand Intent
   ↓
Search Product Catalog
   ↓
Recommend Product
   ↓
Detect Upsell / Cross-sell Opportunity
   ↓
Build Cart
   ↓
Calculate Order
   ↓
Policy / Guardrail Check
   ↓
Human Approval if Required
   ↓
Razorpay Test Payment
   ↓
Payment Result
   ↓
Audit Trail
   ↓
Merchant Analytics
```

The system therefore combines:

**Conversational AI + Agentic Workflows + Recommendation + Commerce + Payments + Guardrails + Explainability**

---

# 4. Key Features

## 4.1 Conversational Shopping

Customers can interact with the merchant using natural language.

Example:

```text
Customer:
"I need running shoes under ₹5,000."
```

The AI agent understands:

```text
Intent:
Product search

Category:
Running Shoes

Maximum budget:
₹5,000
```

The agent then searches the merchant catalog and provides suitable recommendations.

---

# 5. AI Product Discovery

The agent can search products based on:

* Category
* Price
* Brand
* Features
* Customer requirements
* Availability
* Semantic similarity
* Previous customer behavior

Example:

```text
User:
"I need lightweight shoes for daily running."

Agent:
"I found 3 suitable products.

1. AeroRun X — ₹3,999
   Lightweight + breathable

2. Runner Pro — ₹4,499
   Extra cushioning

3. Sprint Lite — ₹3,499
   Lightweight + budget friendly"
```

---

# 6. Upselling

Upselling encourages a customer to purchase a higher-value or upgraded product.

Example:

```text
Customer selects:

Basic Running Shoes
₹2,999
```

The agent may recommend:

```text
Premium Running Shoes
₹3,799

Reason:
Better cushioning and durability.
```

The recommendation should be based on relevant product information rather than random promotion.

---

# 7. Cross-selling

Cross-selling recommends complementary products.

Example:

```text
Customer:
Running Shoes
₹3,999
```

Agent:

```text
Customers purchasing this product
frequently purchase:

Sports Socks
₹499

Would you like to add them?
```

The system can use historical purchase patterns or predefined merchant rules.

---

# 8. Revenue Opportunity Detection

The merchant dashboard can show opportunities identified by the AI.

Example:

```text
Revenue Opportunity

Product:
Running Shoes

Observed Pattern:
31% of customers purchasing this
product also purchase Sports Socks.

Recommended Action:
Cross-sell Sports Socks.

Expected Additional Revenue:
₹12,500

Status:
Awaiting merchant approval
```

This allows the system to move beyond simple product recommendations.

---

# 9. Merchant Policy Engine

The AI agent must operate within predefined merchant policies.

Example policy:

```text
Maximum transaction:
₹10,000

Maximum discount:
₹200

Maximum payment retries:
2

Maximum campaign budget:
₹5,000

High-value transactions:
Require approval
```

The LLM cannot bypass these rules.

---

# 10. Bounded AI Actions

The architecture follows:

```text
AI Decision
     ↓
Policy Engine
     ↓
Is Action Allowed?
     │
     ├── NO
     │    ↓
     │  Block
     │
     ├── APPROVAL REQUIRED
     │    ↓
     │  Human Approval
     │
     └── YES
          ↓
       Execute
```

This ensures that the AI does not have unrestricted control over financial operations.

---

# 11. Human-in-the-Loop

Certain actions require merchant approval.

For example:

```text
AI Recommendation

Campaign:
Running Shoes → Sports Socks

Discount:
₹150

Expected Revenue:
₹12,500

Policy:
✓ Within allowed limit

Status:
Approval required

[ APPROVE ]
[ REJECT ]
```

Only after approval does the system execute the action.

---

# 12. Razorpay Test Payment Integration

The system uses Razorpay's **test environment** to demonstrate the payment workflow.

The basic flow is:

```text
Customer
   ↓
Cart
   ↓
Order Creation
   ↓
Policy Check
   ↓
Razorpay Test Order
   ↓
Payment
   ↓
Success / Failure
```

No production financial transactions are required for the prototype.

---

# 13. Graceful Failure Handling

The system must demonstrate at least one failure scenario.

Example:

```text
Payment Attempt
       ↓
Payment Failed
       ↓
Check Retry Count
       ↓
Retry limit reached
       ↓
Do NOT retry indefinitely
       ↓
Suggest alternative action
```

The agent might respond:

```text
"The payment could not be completed.

I have reached the maximum retry limit,
so I will not retry automatically.

Recommended action:
Generate an alternative payment option."
```

The failure is then recorded in the audit trail.

---

# 14. Explainability

Every significant AI decision should have a reason.

Instead of:

```text
Recommendation:
Sports Socks
```

the system should provide:

```text
Recommendation:
Sports Socks

Reason:
31% of customers who purchased this
product also purchased Sports Socks.

Price:
₹499

Expected additional revenue:
₹499

Confidence:
0.84
```

This makes the agent's behavior understandable to merchants and judges.

---

# 15. Audit Trail

Every important action is logged.

Example:

```text
Timestamp:
2026-08-20 20:31:42

Agent:
Commerce Agent

Action:
Cross-sell recommendation

Product:
Sports Socks

Reason:
31% historical co-purchase rate

Expected Revenue:
₹499

Policy Check:
PASSED

Merchant Approval:
APPROVED

Payment:
SUCCESS
```

The audit system provides traceability from:

```text
Decision
   ↓
Reason
   ↓
Policy
   ↓
Approval
   ↓
Execution
   ↓
Result
```

---

# 16. Merchant Dashboard

The merchant gets a dashboard containing:

### Revenue

```text
Total Revenue
₹2,84,500
```

### AI-Generated Revenue

```text
AI Assisted Revenue
₹38,400
```

### Upsell Performance

```text
Upsell Conversions
127
```

### Cross-Sell Performance

```text
Cross-Sell Conversions
94
```

### Pending Approvals

```text
3
```

### Failed Transactions

```text
7
```

### Agent Actions

```text
Recommendations
Approvals
Payments
Failures
Blocked Actions
```

---

# 17. High-Level Architecture

```text
                         CUSTOMER
                            │
                            ▼
                  ┌───────────────────┐
                  │   Next.js Frontend│
                  │                   │
                  │ AI Shopping UI    │
                  │ Cart              │
                  │ Checkout          │
                  └─────────┬─────────┘
                            │
                            ▼
                  ┌───────────────────┐
                  │   FastAPI Backend │
                  └─────────┬─────────┘
                            │
                            ▼
                  ┌───────────────────┐
                  │ LangChain Agent   │
                  │                   │
                  │ Reasoning         │
                  │ Tool Selection    │
                  │ Decision Making   │
                  └─────────┬─────────┘
                            │
          ┌─────────────────┼──────────────────┐
          │                 │                  │
          ▼                 ▼                  ▼
   Catalog Tools      Customer Tools      Cart Tools
          │                 │                  │
          └─────────────────┼──────────────────┘
                            │
                            ▼
                     PostgreSQL
                            │
                            ▼
                 Revenue Intelligence
                            │
                            ▼
                    Policy Engine
                            │
                    ┌───────┴────────┐
                    │                │
                    ▼                ▼
              Human Approval    Direct Action
                    │                │
                    └───────┬────────┘
                            ▼
                    Razorpay Test API
                            │
                    ┌───────┴────────┐
                    ▼                ▼
                 SUCCESS           FAILURE
                    │                │
                    └───────┬────────┘
                            ▼
                       Audit Logger
                            │
                            ▼
                    Merchant Dashboard
```

---

# 18. Technology Stack

## Frontend

* Next.js
* React
* TypeScript
* Tailwind CSS

## Backend

* Python
* FastAPI
* Pydantic

## AI

* LangChain
* LLM with tool-calling capabilities

## Database

* PostgreSQL
* SQLAlchemy

## Product Search

Initial version:

* PostgreSQL filtering

Optional semantic search:

* ChromaDB
* Sentence Transformers

## Payments

* Razorpay Test APIs

## Data & Analytics

* Pandas
* NumPy

## Authentication

Optional:

* Clerk
* Auth.js

## Deployment

Possible deployment:

```text
Frontend → Vercel

Backend → Render / Railway

Database → PostgreSQL managed service
```

---

# 19. Agent Tools

The LangChain agent will interact with the application through controlled tools.

Possible tools:

```python
search_products()

get_product_details()

get_customer_history()

get_recommendations()

add_to_cart()

remove_from_cart()

calculate_cart_total()

check_inventory()

check_policy()

request_merchant_approval()

create_payment_order()

get_payment_status()

log_agent_action()
```

The agent does not directly manipulate the database or payment system.

---

# 20. Tool Execution Architecture

Instead of:

```text
LLM → Database
```

we use:

```text
LLM
 ↓
Controlled Tool
 ↓
Service Layer
 ↓
Database
```

For payments:

```text
LLM
 ↓
Payment Tool
 ↓
Policy Engine
 ↓
Human Approval
 ↓
Payment Service
 ↓
Razorpay
```

This separation is important for security and reliability.

---

# 21. Database Design

Initial database entities:

```text
Merchant
    │
    ├── Products
    │
    ├── Customers
    │
    ├── Orders
    │
    ├── Transactions
    │
    ├── Policies
    │
    └── Audit Logs
```

### Products

```text
id
merchant_id
name
description
category
price
stock
brand
features
```

### Customers

```text
id
name
email
preferences
created_at
```

### Orders

```text
id
customer_id
total_amount
status
created_at
```

### Transactions

```text
id
order_id
razorpay_order_id
amount
status
payment_method
created_at
```

### Policies

```text
id
merchant_id
max_discount
max_transaction
max_retries
campaign_budget
approval_required
```

### Audit Logs

```text
id
agent_action
reason
input_data
output_data
policy_result
approval_status
execution_result
timestamp
```

---

# 22. Example End-to-End Scenario

A customer enters:

```text
"I need running shoes under ₹5,000."
```

The request reaches the LangChain agent.

The agent determines:

```text
Intent:
Product Search

Category:
Running Shoes

Budget:
₹5,000
```

It calls:

```python
search_products(
    category="running shoes",
    max_price=5000
)
```

The catalog returns several products.

The agent recommends one.

The customer selects it.

The agent checks for cross-sell opportunities.

```text
Running Shoes
+
Sports Socks
```

The customer accepts.

The cart becomes:

```text
Running Shoes     ₹3,999
Sports Socks        ₹499
-------------------------
Total              ₹4,498
```

The agent checks the merchant policy.

```text
Maximum transaction = ₹10,000

₹4,498 < ₹10,000

✓ Allowed
```

The system creates a Razorpay test order.

Payment succeeds.

The audit log records:

```text
Recommendation
→ Cross-sell
→ Policy Check
→ Cart Update
→ Payment
→ Success
```

The merchant dashboard updates the revenue metrics.

---

# 23. Security & Safety Principles

The system follows several principles.

### Principle 1 — Least Privilege

The agent only gets access to tools it actually needs.

### Principle 2 — No Direct Payment Authority

The LLM cannot directly execute unrestricted payments.

### Principle 3 — Policy Enforcement

Every financial action passes through the policy engine.

### Principle 4 — Human Approval

Sensitive actions require merchant approval.

### Principle 5 — Auditability

Every important action is logged.

### Principle 6 — Retry Limits

Payment operations have strict retry limits.

### Principle 7 — Graceful Failure

The system must fail safely instead of repeatedly attempting actions.

---

# 24. Evaluation Metrics

The project should not be evaluated only on whether the chatbot works.

We will measure:

### Agent Metrics

* Tool-call accuracy
* Successful task completion
* Invalid tool calls
* Agent response latency

### Commerce Metrics

* Upsell conversion rate
* Cross-sell conversion rate
* Average order value
* Additional revenue generated

### Safety Metrics

* Policy violation rate
* Unauthorized action rate
* Approval compliance
* Maximum retry violations

### Payment Metrics

* Payment success rate
* Payment failure handling rate
* Successful fallback rate

### System Metrics

* API latency
* Error rate
* Tool execution success rate

---

# 25. Example Success Dashboard

```text
╔══════════════════════════════════════════╗
║          AI COMMERCE ANALYTICS           ║
╠══════════════════════════════════════════╣
║                                          ║
║ Total Revenue             ₹2,84,500      ║
║ AI Assisted Revenue         ₹38,400      ║
║                                          ║
║ Upsell Conversions              127      ║
║ Cross-sell Conversions            94      ║
║ Average Order Value           ₹1,842      ║
║                                          ║
║ Agent Tasks Completed          1,248      ║
║ Successful Payments              936      ║
║ Failed Payments                   42      ║
║ Blocked Actions                   18      ║
║ Pending Approvals                  3      ║
╚══════════════════════════════════════════╝
```

The actual values will come from your test dataset and experiments.

---

# 26. Project Development Phases

## Phase 1 — Foundation

* Repository setup
* Backend setup
* Frontend setup
* PostgreSQL setup
* Environment configuration

## Phase 2 — Commerce Data

* Product model
* Customer model
* Order model
* Transaction model
* Merchant policy model
* Seed data

## Phase 3 — Catalog

* Product search
* Product details
* Filtering
* Optional semantic retrieval

## Phase 4 — LangChain Agent

* Agent setup
* System prompt
* Tool definitions
* Tool execution
* Conversation handling

## Phase 5 — Revenue Intelligence

* Upsell detection
* Cross-sell detection
* Product recommendation
* Revenue opportunity calculation

## Phase 6 — Cart & Orders

* Add to cart
* Remove from cart
* Cart totals
* Order creation

## Phase 7 — Guardrails

* Transaction limits
* Discount limits
* Retry limits
* Approval gates
* Policy validation

## Phase 8 — Razorpay

* Test order creation
* Payment flow
* Payment status
* Failure handling

## Phase 9 — Auditability

* Agent decision logs
* Tool-call logs
* Policy logs
* Payment logs
* Approval logs

## Phase 10 — Dashboard

* Revenue analytics
* AI-generated revenue
* Recommendations
* Approvals
* Audit trail

## Phase 11 — Evaluation

* Test dataset
* Agent evaluation
* Revenue metrics
* Safety metrics
* Failure testing

## Phase 12 — Final Demo

* UI polish
* Architecture diagram
* Demo scenario
* Failure scenario
* Presentation
* Documentation

---

# 27. Project Timeline

For a **solo developer**:

| Phase              | Estimated Time |
| ------------------ | -------------: |
| Foundation         |      0.5–1 day |
| Database + catalog |       1–2 days |
| Product search     |          1 day |
| LangChain agent    |       1–2 days |
| Upsell/cross-sell  |       1–2 days |
| Cart/order system  |          1 day |
| Guardrails         |          1 day |
| Razorpay           |       1–2 days |
| Audit trail        |      0.5–1 day |
| Dashboard          |       1–2 days |
| Evaluation         |          1 day |
| Polish/demo        |       1–2 days |

**Strong hackathon version: ~9–12 days**

A more polished version can take **12–15 days**.

---

# 28. Future Enhancements

After the MVP is stable, possible additions include:

* AI buyer mode
* Voice commerce
* Hinglish shopping assistant
* Personalized recommendations
* Campaign orchestration
* Semantic product search
* Customer segmentation
* Dynamic bundles
* A/B testing
* Multi-agent architecture
* Advanced revenue forecasting

These should **not** be built before the core workflow works.

---

# 29. What Makes This Project Different?

This project is not simply:

```text
User → Chatbot → Product Recommendation
```

Instead, it is:

```text
User
 ↓
AI Agent
 ↓
Reasoning
 ↓
Tools
 ↓
Revenue Opportunity
 ↓
Policy Validation
 ↓
Human Approval
 ↓
Payment
 ↓
Audit
 ↓
Measurable Revenue Impact
```

The important distinction is **actionability**.

The AI does not merely tell the merchant:

> "You should cross-sell socks."

It can move through the controlled commerce workflow required to actually **execute and measure the action**.

---

# 30. Final Vision

The final system should demonstrate:

> **An AI agent that can understand customer intent, discover products, increase cart value through intelligent upselling/cross-selling, safely execute commerce actions through Razorpay test APIs, respect merchant-defined financial boundaries, request human approval when necessary, handle failures gracefully, and provide a complete explanation and audit trail for every important action.**

The ultimate goal is to demonstrate a shift from:

```text
Traditional E-Commerce

Customer → Website → Checkout → Payment
```

to:

```text
Agentic Commerce

Customer
   ↓
AI understands intent
   ↓
AI discovers products
   ↓
AI recommends
   ↓
AI increases basket value
   ↓
AI checks safety policies
   ↓
Human approves when needed
   ↓
AI executes transaction
   ↓
AI observes result
   ↓
AI explains everything
```


