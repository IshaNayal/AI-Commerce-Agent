# System Design Interview Theory: Agentic Workflows

If discussing Phase 5 in an AI/ML or Backend Systems design interview, these are the core theoretical concepts applied.

## 1. Tool-Calling (Function Calling) LLMs
- **Theory:** Modern LLMs (like GPT-4) are fine-tuned to detect when a user's request requires external information or action. Instead of generating a raw text response, the LLM outputs a structured JSON object requesting to execute a specific function (e.g., `{"name": "search_products", "arguments": {"query": "shoes"}}`). The backend executes the function and returns the result to the LLM.
- **Our Implementation:** We defined four explicit tools (`search_products`, `get_product_details`, `add_to_cart`, `view_cart`). LangChain handles the complex translation between Python function signatures (using Pydantic/Type Hints) and the JSON Schema expected by the OpenAI API.

## 2. In-Context Learning & Prompt Engineering
- **Theory:** The behavior of a foundation model is heavily dictated by its system prompt. Proper prompt engineering bounds the agent's behavior and prevents catastrophic actions.
- **Our Implementation:** We explicitly instruct the agent via the `SYSTEM_PROMPT` to verify product IDs before adding them to carts, to refuse to offer discounts, and to briefly explain its reasoning. This establishes a baseline level of "Safety by Design" before executing any backend code.

## 3. Stateful AI Systems (Conversational Memory)
- **Theory:** LLMs are inherently stateless. To hold a conversation, the entire history of the chat must be re-sent to the LLM on every turn. 
- **Our Implementation:** We use PostgreSQL to implement a "Memory" architecture. The `ChatService` loads `ChatMessages` and formats them into LangChain `HumanMessage` and `AIMessage` objects. As conversations grow extremely long, this context window can exceed token limits. In a future iteration, we would need to implement a "sliding window" or "summary memory" to truncate older messages.

## 4. Multi-Tenant Security in AI
- **Theory:** When building AI for SaaS, the most critical vulnerability is the AI accessing data belonging to a different tenant. 
- **Our Implementation:** We completely abstracted the `merchant_id` away from the LLM. The Langchain tools act as a proxy. When the LLM calls `search_products(query="shoes")`, the backend Python closure silently injects the `merchant_id` of the authenticated user into the `ProductService.search_products` call. The LLM is structurally isolated and cannot perform cross-tenant data leaks.
