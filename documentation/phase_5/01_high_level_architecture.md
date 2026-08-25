# High Level Architecture: LangChain Commerce Agent

## Overview
Phase 5 focused on building the core "brain" of the AI Commerce Agent. This phase transitions the application from a traditional CRUD backend to an Agentic system that can autonomously reason, take actions, and interact with users using natural language.

## Architecture Pattern: ReAct Agent (LangGraph)
We implemented a **ReAct** (Reasoning and Acting) agent architecture using LangGraph.

1. **The LLM (Brain):** We utilized OpenAI's `gpt-4o-mini` model configured via LangChain. The LLM acts as the central router. It receives the user's message, analyzes the conversation history, and decides whether to respond directly or invoke a tool.
2. **The System Prompt (Guardrails):** A strict, foundational instruction set injected into every conversation. It defines the agent's persona (helpful commerce assistant) and strict behavioral rules (e.g., "Do not promise discounts", "Verify product IDs before adding to cart").
3. **Tools (Actuators):** LangChain `@tool` wrappers that expose our existing, safe backend Services (`ProductService`, `CartService`) to the LLM. 
4. **Stateful Memory (PostgreSQL):** We built a persistent conversational memory system in PostgreSQL to maintain session state across HTTP requests.

## The Execution Flow
1. **Request:** The frontend sends a `POST /chat` with a `message`, `session_id`, and `merchant_id`.
2. **State Retrieval:** `ChatService` loads all previous `ChatMessages` for the given session from PostgreSQL.
3. **Agent Invocation:** The user's new message is appended, and the entire state is passed to the LangGraph ReAct agent.
4. **Reasoning Loop:** 
   - The LLM may decide it needs information (e.g., calling `search_products`).
   - The Python backend executes the tool and returns the JSON result back to the LLM.
   - The LLM reasons over the result and formulates a final, human-readable response.
5. **Persistence:** The final agent response is saved back to PostgreSQL, and the string is returned to the user via the API.
