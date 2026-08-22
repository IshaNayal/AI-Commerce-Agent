# Detailed Technical Architecture — AI Growth & Agentic Commerce

 I would build the system as a **modular monolith** rather than microservices. This gives you clean separation between components without creating unnecessary deployment and debugging complexity.

The core architecture will be:

```text
┌──────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                 │
│                                                                      │
│  ┌─────────────────────┐              ┌──────────────────────────┐   │
│  │ Customer Interface  │              │ Merchant Dashboard       │   │
│  │                     │              │                          │   │
│  │ Chat / Shopping     │              │ Revenue Analytics        │   │
│  │ Product Cards       │              │ AI Recommendations       │   │
│  │ Cart                │              │ Approval Queue            │   │
│  │ Checkout            │              │ Audit Logs               │   │
│  └──────────┬──────────┘              └────────────┬─────────────┘   │
│             │                                      │                 │
└─────────────┼──────────────────────────────────────┼─────────────────┘
              │ HTTPS / REST / SSE                    │
              └──────────────────┬───────────────────┘
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         API LAYER                                    │
│                                                                      │
│                         FastAPI                                     │
│                                                                      │
│  /chat       /products       /cart       /orders                    │
│  /payments   /approvals     /analytics  /audit                     │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                                │
│                                                                      │
│ ┌────────────────┐ ┌────────────────┐ ┌───────────────────────────┐ │
│ │ Commerce       │ │ Revenue        │ │ Agent Orchestration       │ │
│ │ Service        │ │ Intelligence   │ │                           │ │
│ │                │ │                │ │ LangChain                 │ │
│ │ Catalog        │ │ Upsell         │ │ LLM                       │ │
│ │ Cart           │ │ Cross-sell     │ │ Prompt                    │ │
│ │ Orders         │ │ Recommendations│ │ Tool Calling              │ │
│ └───────┬────────┘ └───────┬────────┘ └─────────────┬─────────────┘ │
│         │                  │                        │               │
└─────────┼──────────────────┼────────────────────────┼───────────────┘
          │                  │                        │
          │                  │                        ▼
          │                  │              ┌───────────────────────┐
          │                  │              │      TOOL LAYER       │
          │                  │              │                       │
          │                  │              │ search_products()     │
          │                  │              │ get_product()         │
          │                  │              │ get_customer()        │
          │                  │              │ get_recommendations()  │
          │                  │              │ add_to_cart()          │
          │                  │              │ calculate_cart()       │
          │                  │              │ check_policy()         │
          │                  │              │ create_payment()       │
          │                  │              │ get_payment_status()   │
          │                  │              │ create_approval()      │
          │                  │              │ log_action()           │
          │                  │              └───────────┬───────────┘
          │                  │                          │
          ▼                  ▼                          ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       CONTROL LAYER                                  │
│                                                                      │
│                     POLICY / GUARDRAIL ENGINE                        │
│                                                                      │
│  Transaction Limits │ Discount Limits │ Retry Limits                │
│  Approval Rules     │ Campaign Limits │ Allowed Actions             │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │
                         ┌───────┴────────┐
                         ▼                ▼
                  ┌─────────────┐  ┌──────────────┐
                  │   APPROVAL  │  │   EXECUTION  │
                  │    QUEUE    │  │    ENGINE    │
                  └──────┬──────┘  └──────┬───────┘
                         │                │
                         └───────┬────────┘
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│                        INTEGRATION LAYER                             │
│                                                                      │
│                         Razorpay                                    │
│                                                                      │
│             Order Creation → Payment → Verification                 │
│                              ↓                                       │
│                       Success / Failure                              │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│                          DATA LAYER                                  │
│                                                                      │
│                        PostgreSQL                                   │
│                                                                      │
│ Products │ Customers │ Orders │ Cart │ Transactions                 │
│ Policies │ Approvals │ Agent Runs │ Audit Logs │ Revenue Events     │
│                                                                      │
│                  + Optional ChromaDB                                 │
│                  Semantic Product Search                             │
└──────────────────────────────────────────────────────────────────────┘
```

---

# 1. Architectural Style

### Recommended architecture: Modular Monolith


```text
Next.js
   ↓
FastAPI
   ↓
Modular Application
   ├── Agent
   ├── Commerce
   ├── Recommendation
   ├── Guardrails
   ├── Payments
   ├── Approvals
   └── Audit
          ↓
     PostgreSQL
```

Each module has a clear responsibility.

Later, any module could theoretically be extracted into a service.

---

# 2. Complete Request Flow


Customer:

> "I need running shoes under ₹5,000."

### Step 1 — Frontend

Next.js sends:

```http
POST /api/chat
```

Payload:

```json
{
  "customer_id": "cust_123",
  "merchant_id": "merchant_001",
  "message": "I need running shoes under ₹5,000"
}
```

---

# 3. API Layer

FastAPI receives the request.

```text
POST /chat
      ↓
Authentication
      ↓
Request validation
      ↓
Conversation service
      ↓
Agent service
```

FastAPI should **not contain the agent's business logic directly**.

Instead:

```text
API Route
   ↓
Service
   ↓
Agent
```

This keeps the application maintainable.

---

# 4. Agent Orchestration Layer

The LangChain agent receives:

```text
User:
I need running shoes under ₹5,000.
```

The LLM determines:

```text
Intent:
product_search

Category:
running shoes

Max price:
5000
```

Then it decides to call:

```python
search_products(
    category="running shoes",
    max_price=5000
)
```

---

# 5. Tool Layer

The agent doesn't directly query PostgreSQL.

Instead:

```text
LLM
 ↓
search_products()
 ↓
CatalogService
 ↓
ProductRepository
 ↓
PostgreSQL
```

This is important.

The LLM should never have unrestricted database access.

---

# 6. Product Search Architecture

Initially:

```text
search_products()
        ↓
Catalog Service
        ↓
PostgreSQL
        ↓
Filtering
        ↓
Rank Results
```

For example:

```sql
SELECT *
FROM products
WHERE category = 'running shoes'
AND price <= 5000
AND stock > 0;
```

Later, semantic search can be added:

```text
User Query
     ↓
Embedding Model
     ↓
Vector Search
     ↓
ChromaDB
     ↓
Candidate Products
     ↓
Metadata Filtering
     ↓
Final Products
```

## eventual retrieval architecture :

```text
                 User Query
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
   Keyword/Metadata        Semantic Search
       Search                  ChromaDB
          │                     │
          └──────────┬──────────┘
                     ▼
                Candidate Set
                     ↓
                 Ranking
                     ↓
              Final Products
```

But **don't build the vector layer first**. PostgreSQL search is enough for your initial MVP.

---

# 7. Recommendation Engine

Once products are retrieved, the system can identify opportunities.

There are two separate concepts:

### Product relevance

> Is this product suitable for the customer?

### Revenue opportunity

> Is there a useful additional product the customer may purchase?

For example:

```text
Customer
   ↓
Running Shoes
   ↓
Frequently bought together
   ↓
Sports Socks
```

The recommendation service can calculate:

```text
co_purchase_rate =
customers_bought_both /
customers_bought_primary
```

For example:

```text
3,100 customers bought shoes

961 also bought socks

Co-purchase rate = 961 / 3100
                 ≈ 31%
```

The agent can then explain:

> "31% of customers who purchased this shoe also purchased these socks."

---

# 8. Agent Decision Layer

The agent receives the recommendation.

Possible output:

```json
{
  "action": "cross_sell",
  "product_id": "sock_123",
  "reason": "31% historical co-purchase rate",
  "expected_revenue": 499
}
```

But **this action is NOT executed yet.**

It goes through the control layer.

---

# 9. Guardrail / Policy Engine

This is one of the most important architectural components.

```text
Agent Decision
      ↓
Policy Engine
      ↓
Validate Action
```

Suppose:

```text
Requested discount = ₹300
Merchant limit = ₹200
```

Result:

```json
{
  "allowed": false,
  "reason": "Discount exceeds merchant limit",
  "requires_approval": true
}
```

The LLM cannot override this.

---

# 10. Policy Engine Design

Policies can be stored in PostgreSQL:

```text
merchant_policies

id
merchant_id
max_transaction_amount
max_discount_amount
max_payment_retries
max_campaign_budget
approval_threshold
```

Then create a deterministic policy engine.

Conceptually:

```python
def validate_action(action, policy):

    if action.type == "payment":
        if action.amount > policy.max_transaction_amount:
            return BLOCK

    if action.type == "discount":
        if action.discount > policy.max_discount_amount:
            return APPROVAL_REQUIRED

    return ALLOW
```

The important thing is:

> **LLM = probabilistic decision-maker**

> **Policy Engine = deterministic authority**

That separation makes the system much safer.

---

# 11. Human Approval Architecture

If the policy says approval is required:

```text
Agent
 ↓
Policy Engine
 ↓
APPROVAL_REQUIRED
 ↓
Approval Service
 ↓
PostgreSQL
 ↓
Merchant Dashboard
```

Merchant sees:

```text
┌─────────────────────────────────────┐
│ Approval Required                   │
├─────────────────────────────────────┤
│ Action: Cross-sell                  │
│ Product: Sports Socks               │
│ Discount: ₹150                      │
│ Expected Revenue: ₹12,500           │
│                                     │
│ Reason: 31% co-purchase rate        │
│                                     │
│ [ APPROVE ]        [ REJECT ]       │
└─────────────────────────────────────┘
```

Only approval changes the action state:

```text
PENDING
   ↓
APPROVED
   ↓
EXECUTING
   ↓
COMPLETED
```

Or:

```text
PENDING
   ↓
REJECTED
```

---

# 12. Cart Architecture

The cart should be controlled by your backend, not by the LLM.

```text
Agent
 ↓
add_to_cart(product_id, quantity)
 ↓
CartService
 ↓
PostgreSQL
```

Cart table:

```text
cart_items

id
cart_id
product_id
quantity
unit_price
subtotal
```

The backend calculates:

```text
subtotal
tax
discount
total
```

Never allow the LLM to simply say:

> "Total = ₹4,498"

and trust that value.

The backend calculates the actual amount.

---

# 13. Order Architecture

Once the customer confirms:

```text
Cart
 ↓
OrderService
 ↓
Create Order
 ↓
Freeze/record pricing
 ↓
Policy Check
 ↓
Payment
```

Order states:

```text
CREATED
   ↓
PENDING_PAYMENT
   ↓
PAID
```

Failure:

```text
PENDING_PAYMENT
   ↓
PAYMENT_FAILED
```

---

# 14. Razorpay Architecture

The payment system should be isolated in a dedicated service.

```text
PaymentService
       ↓
RazorpayClient
       ↓
Razorpay Test API
```

Never put Razorpay API calls inside your LangChain tool implementation itself.

Instead:

```text
LangChain Tool
     ↓
PaymentService
     ↓
RazorpayClient
     ↓
Razorpay
```

This gives you clean separation.

---

# 15. Payment Flow

```text
Customer confirms order
           ↓
Backend calculates final amount
           ↓
Policy Engine
           ↓
Approval if necessary
           ↓
Create Razorpay Order
           ↓
Customer Payment
           ↓
Razorpay Response
           ↓
Verify Payment
           ↓
Update Transaction
           ↓
Update Order
           ↓
Audit Event
```

---

# 16. Payment Failure Flow

Suppose Razorpay returns failure.

```text
Payment
   ↓
FAILED
   ↓
TransactionService
   ↓
Check retry count
   ↓
Retry allowed?
```

If yes:

```text
retry_count < max_retries
        ↓
      RETRY
```

If no:

```text
retry_count >= max_retries
        ↓
STOP
        ↓
Create fallback recommendation
        ↓
Audit
```

This demonstrates the required graceful failure behavior.

---

# 17. Audit Architecture

Every significant operation creates an event.

Example:

```text
AgentDecisionCreated
ProductSearched
RecommendationCreated
CartUpdated
PolicyChecked
ApprovalRequested
ApprovalGranted
PaymentCreated
PaymentSucceeded
PaymentFailed
FallbackTriggered
```

You can model this as:

```text
audit_logs

id
trace_id
session_id
actor
action
entity_type
entity_id
input
reason
policy_result
approval_status
execution_result
timestamp
```

---

# 18. Trace ID

This is a particularly useful addition.

One customer interaction gets:

```text
trace_id = "tr_8a92f"
```

Every action associated with that request uses the same trace ID:

```text
tr_8a92f
 ├── product_search
 ├── recommendation
 ├── cross_sell
 ├── policy_check
 ├── approval
 ├── payment
 └── payment_success
```

Now the merchant can open one transaction and see the **complete chain of reasoning and execution**.

---

# 19. Agent Memory

For the MVP, don't create complicated long-term memory.

Use three levels:

### Conversation state

```text
Current conversation
Current request
Current cart
```

### Customer context

```text
Previous purchases
Preferences
Relevant history
```

### Merchant context

```text
Policies
Catalog
Business rules
```

The agent can receive relevant context when needed.

---

# 20. LLM Context Architecture

Don't dump your entire database into the prompt.

Instead:

```text
User Query
   ↓
Agent
   ↓
Tool Call
   ↓
Relevant Data
   ↓
LLM
```

For example, instead of giving the LLM 10,000 products:

```text
search_products()
      ↓
Top 5 relevant products
      ↓
LLM
```

This reduces:

* token usage
* latency
* hallucination
* context size

---

# 21. Frontend Architecture

Next.js frontend can have:

```text
app/
│
├── customer/
│   ├── chat/
│   ├── products/
│   ├── cart/
│   └── checkout/
│
├── merchant/
│   ├── dashboard/
│   ├── approvals/
│   ├── recommendations/
│   ├── transactions/
│   └── audit/
│
└── api/
```

Customer UI:

```text
Chat
 ↓
Product Cards
 ↓
Cart
 ↓
Checkout
```

Merchant UI:

```text
Dashboard
 ↓
Revenue
 ↓
AI Opportunities
 ↓
Approvals
 ↓
Audit Logs
```

---

# 22. Backend Architecture

I'd structure your FastAPI application like this:

```text
backend/
│
└── app/
    │
    ├── main.py
    │
    ├── api/
    │   ├── routes/
    │   │   ├── chat.py
    │   │   ├── products.py
    │   │   ├── cart.py
    │   │   ├── orders.py
    │   │   ├── payments.py
    │   │   ├── approvals.py
    │   │   ├── analytics.py
    │   │   └── audit.py
    │   │
    │   └── dependencies.py
    │
    ├── agent/
    │   ├── agent.py
    │   ├── prompts.py
    │   ├── state.py
    │   └── tools/
    │       ├── catalog_tools.py
    │       ├── customer_tools.py
    │       ├── cart_tools.py
    │       ├── recommendation_tools.py
    │       ├── payment_tools.py
    │       └── approval_tools.py
    │
    ├── services/
    │   ├── catalog_service.py
    │   ├── customer_service.py
    │   ├── cart_service.py
    │   ├── order_service.py
    │   ├── recommendation_service.py
    │   ├── payment_service.py
    │   ├── approval_service.py
    │   └── audit_service.py
    │
    ├── guardrails/
    │   ├── policy_engine.py
    │   ├── rules.py
    │   └── validators.py
    │
    ├── integrations/
    │   └── razorpay/
    │       ├── client.py
    │       └── schemas.py
    │
    ├── database/
    │   ├── connection.py
    │   ├── models/
    │   ├── repositories/
    │   └── migrations/
    │
    ├── schemas/
    │   ├── product.py
    │   ├── cart.py
    │   ├── order.py
    │   ├── payment.py
    │   └── agent.py
    │
    └── config.py
```

---

# 23. Why separate Tools and Services?

This distinction is important.

### Tool

The interface exposed to the LLM.

```python
search_products(...)
```

### Service

The actual application logic.

```python
CatalogService.search(...)
```

Architecture:

```text
LLM
 ↓
LangChain Tool
 ↓
Service
 ↓
Repository
 ↓
Database
```

This prevents your AI layer from becoming tightly coupled to your database.

---

# 24. Repository Layer

Database operations should ideally go through repositories.

```text
CatalogService
      ↓
ProductRepository
      ↓
SQLAlchemy
      ↓
PostgreSQL
```

For example:

```text
ProductRepository
├── get_by_id()
├── search()
├── get_by_category()
└── get_available_products()
```

The service layer contains business logic.

The repository layer handles persistence.

---

# 25. Data Flow: Product Recommendation

```text
Customer:
"Suggest running shoes under ₹5k."
             │
             ▼
        FastAPI /chat
             │
             ▼
       LangChain Agent
             │
             ▼
    search_products tool
             │
             ▼
       CatalogService
             │
             ▼
     ProductRepository
             │
             ▼
        PostgreSQL
             │
             ▼
      Candidate Products
             │
             ▼
 RecommendationService
             │
             ▼
   Ranked Recommendations
             │
             ▼
          Agent
             │
             ▼
        Customer UI
```

---

# 26. Data Flow: Cross-Sell

```text
Customer selects Product A
             ↓
RecommendationService
             ↓
Historical purchase data
             ↓
Calculate co-purchase patterns
             ↓
Product B identified
             ↓
Agent generates explanation
             ↓
Customer accepts
             ↓
Add Product B to cart
             ↓
Updated order value
```

---

# 27. Data Flow: Payment

```text
Customer confirms cart
             ↓
OrderService
             ↓
Calculate authoritative total
             ↓
PolicyEngine
             ↓
Approval?
      ┌──────┴──────┐
      │             │
     YES            NO
      │             │
Approval Queue      │
      │             │
Merchant approves   │
      └──────┬──────┘
             ↓
      PaymentService
             ↓
       RazorpayClient
             ↓
      Razorpay Test API
             ↓
      Payment Response
             ↓
 TransactionService
             ↓
 PostgreSQL
             ↓
 AuditService
```

---

# 28. Data Flow: Failure

```text
Razorpay
   ↓
Payment Failed
   ↓
PaymentService
   ↓
Transaction updated
   ↓
Retry policy checked
   ↓
 ┌───────────────┐
 │ Retry allowed?│
 └───────┬───────┘
       YES│       │NO
          ↓       ↓
        Retry    STOP
                  ↓
             Fallback
                  ↓
             Audit Log
                  ↓
             Customer
```

---

# 29. State Management

For important business objects, use explicit states.

### Order

```text
CREATED
   ↓
PENDING_PAYMENT
   ↓
PAID
```

Failure:

```text
PENDING_PAYMENT
   ↓
PAYMENT_FAILED
```

### Approval

```text
PENDING
 ↓
APPROVED
 ↓
EXECUTING
 ↓
COMPLETED
```

or:

```text
PENDING
 ↓
REJECTED
```

### Agent Task

```text
RECEIVED
 ↓
PLANNING
 ↓
TOOL_EXECUTION
 ↓
POLICY_CHECK
 ↓
WAITING_APPROVAL
 ↓
EXECUTING
 ↓
COMPLETED
```

This will also make your eventual audit trail much cleaner.

---

# 30. Observability

For a hackathon, you don't need an enormous observability stack.

At minimum, record:

```text
trace_id
session_id
agent_run_id
tool_name
tool_input
tool_output
latency
status
error
timestamp
```

This allows you to debug:

> Why did the agent recommend this product?

> Why was a payment blocked?

> Which tool failed?

> How long did the agent take?

---

# 31. Security Boundaries

The most sensitive boundary is:

```text
                  UNTRUSTED / PROBABILISTIC
                         │
                         ▼
                    LLM / Agent
                         │
                         ▼
                  TOOL INTERFACE
                         │
═════════════════════════╪════════════════════════
                  TRUST BOUNDARY
                         │
                         ▼
                 POLICY ENGINE
                         │
                         ▼
                  APPLICATION CODE
                         │
                         ▼
                 PAYMENT SERVICE
                         │
                         ▼
                    RAZORPAY
```

The LLM should **not** be trusted as the final authority for:

* payment amounts
* discounts
* transaction authorization
* retry limits
* merchant permissions

Those must be enforced deterministically by backend code.

---

# 32. Recommended Technology Mapping

```text
┌───────────────────────┬─────────────────────────┐
│ Component             │ Technology              │
├───────────────────────┼─────────────────────────┤
│ Frontend              │ Next.js                 │
│ UI                    │ React + Tailwind        │
│ Backend               │ FastAPI                 │
│ Language              │ Python                  │
│ Agent Framework       │ LangChain               │
│ LLM                   │ Tool-calling LLM        │
│ ORM                   │ SQLAlchemy              │
│ Validation            │ Pydantic                │
│ Database              │ PostgreSQL              │
│ Vector Search         │ ChromaDB (optional)     │
│ Embeddings            │ Sentence Transformers   │
│ Payments              │ Razorpay Test API       │
│ Analytics             │ Pandas                  │
│ Authentication        │ Clerk/Auth.js (optional)│
│ Frontend Deployment   │ Vercel                  │
│ Backend Deployment    │ Render/Railway          │
│ Version Control       │ Git/GitHub               │
└───────────────────────┴─────────────────────────┘
```

---

# 33. The Most Important Architecture Decision

The **LLM should not be the system**.

Instead:

```text
                ┌─────────────┐
                │     LLM     │
                │             │
                │ Reasoning   │
                │ Intent      │
                │ Tool choice │
                └──────┬──────┘
                       │
                       ▼
                ┌─────────────┐
                │    Tools    │
                └──────┬──────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Business Logic  │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Policy Engine   │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ External APIs   │
              └─────────────────┘
```

**LLM handles intelligence.
Backend handles truth.
Policy engine handles authority.
Razorpay handles payments.
Audit system handles accountability.**

That's the architecture I'd use for this project.

---

# 34. Final End-to-End Architecture

The complete system can therefore be summarized as:

```text
                         ┌──────────────┐
                         │   CUSTOMER   │
                         └──────┬───────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   NEXT.JS UI    │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │     FASTAPI     │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ LANGCHAIN AGENT │
                       │                 │
                       │ LLM + Prompt    │
                       │ Tool Calling    │
                       └────────┬────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
        Catalog Tools     Customer Tools      Cart Tools
              │                 │                 │
              └─────────────────┼─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │    SERVICES     │
                       │                 │
                       │ Commerce        │
                       │ Recommendation  │
                       │ Order           │
                       │ Payment         │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   POSTGRESQL    │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ POLICY ENGINE   │
                       │                 │
                       │ Limits          │
                       │ Permissions     │
                       │ Approval Rules  │
                       └────────┬────────┘
                                │
                     ┌──────────┴──────────┐
                     ▼                     ▼
              HUMAN APPROVAL         ALLOWED ACTION
                     │                     │
                     └──────────┬──────────┘
                                ▼
                       ┌─────────────────┐
                       │ PAYMENT SERVICE │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ RAZORPAY TEST   │
                       │      API        │
                       └────────┬────────┘
                                │
                         ┌──────┴──────┐
                         ▼             ▼
                      SUCCESS       FAILURE
                         │             │
                         └──────┬──────┘
                                ▼
                       ┌─────────────────┐
                       │  AUDIT SERVICE  │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │    MERCHANT     │
                       │    DASHBOARD    │
                       └─────────────────┘
```

### The implementation order should follow this architecture

**1. Foundation → 2. Database → 3. Catalog → 4. Services → 5. LangChain Agent → 6. Revenue Intelligence → 7. Guardrails → 8. Cart/Orders → 9. Razorpay → 10. Audit → 11. Dashboard → 12. Evaluation.**


