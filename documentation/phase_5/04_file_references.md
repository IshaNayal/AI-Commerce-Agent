# File References & Explanations (Phase 5)

Below is a breakdown of the critical files constructed during Phase 5 to implement the LangChain Commerce Agent.

## Agent Core
- `backend/app/agent/tools.py`
  - **Purpose:** Defines the capabilities of the agent.
  - **Key Structure:** Contains the `get_agent_tools(db, merchant_id, cart_id)` factory function. It returns a list of Langchain `@tool` decorated functions. Notice how the type hints (`Annotated[str, "description"]`) and docstrings are highly detailed; this is intentional, as LangChain uses these strings directly to teach the LLM *how* and *when* to use the tools.

- `backend/app/agent/commerce_agent.py`
  - **Purpose:** The brain of the system.
  - **Key Structure:** 
    - Defines the `SYSTEM_PROMPT`.
    - Initializes the `ChatOpenAI` LLM.
    - Uses `langgraph`'s `create_react_agent()` to bind the LLM and the tools into an executable graph.
    - Exposes the `chat()` method which handles fetching history from the DB, running the LLM, and saving the final response back to the DB.

## Database & Memory (PostgreSQL)
- `backend/app/models/chat.py`
  - **Purpose:** Defines the SQLAlchemy schema for Conversational Memory.
  - **Key Tables:** 
    - `ChatSession`: Links a conversation to a `merchant_id` and a `cart_id`.
    - `ChatMessage`: Stores individual turns of the conversation (`user` or `assistant`), linked to the session.

- `backend/app/repositories/chat.py` & `backend/app/services/chat_service.py`
  - **Purpose:** Standard repository/service pattern to encapsulate reading and writing chat messages to the database.

## API Integration
- `backend/app/api/routes/chat.py`
  - **Purpose:** Exposes the agent to the frontend.
  - **Key Structure:** A single `POST /chat` endpoint. It accepts a message, retrieves or creates a database `ChatSession`, delegates the reasoning to the `CommerceAgent`, and returns the agent's text response.
