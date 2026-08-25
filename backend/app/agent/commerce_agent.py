from uuid import UUID
from typing import List

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from sqlalchemy.orm import Session

from backend.app.config import settings
from .tools import get_agent_tools

SYSTEM_PROMPT = """You are a helpful, intelligent Commerce Assistant for an online store.
Your goal is to help customers find products, answer questions, provide recommendations, and help them add items to their cart.

# Guardrails & Instructions
1. Use the `search_products` tool to find products before recommending them. Never invent or hallucinate products.
2. If the user wants to add an item to the cart, you must first know the exact product ID. Use `search_products` to find it if you don't have it.
3. Once you have the product ID, use the `add_to_cart` tool.
4. You can use the `view_cart` tool to check what the customer already has in their cart to prevent duplicate suggestions or to inform them of their total.
5. Do NOT promise discounts unless specifically authorized by a tool (which you currently do not have).
6. Be polite, concise, and persuasive. If a customer buys shoes, you might proactively suggest matching socks if available.
7. Always explain your reasoning briefly when recommending a product (e.g., "I recommend this because you mentioned you need something lightweight").
"""

class CommerceAgent:
    def __init__(self, db: Session, merchant_id: UUID, cart_id: UUID | None):
        self.db = db
        self.merchant_id = merchant_id
        self.cart_id = cart_id
        
        # Initialize LLM
        api_key = getattr(settings, "OPENAI_API_KEY", None)
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set.")
            
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2,
            openai_api_key=api_key
        )
        
        # Get bound tools
        self.tools = get_agent_tools(self.db, self.merchant_id, self.cart_id)
        
        # Create ReAct agent graph
        self.agent_executor = create_react_agent(
            self.llm,
            self.tools,
            state_modifier=SystemMessage(content=SYSTEM_PROMPT)
        )

    def chat(self, user_message: str, session_id: UUID) -> str:
        """
        Send a message to the agent using PostgreSQL for conversational memory.
        """
        from backend.app.services.chat_service import ChatService
        chat_service = ChatService(self.db)
        
        # 1. Save user message to DB
        chat_service.add_message(session_id, "user", user_message)
        
        # 2. Fetch history from DB
        db_history = chat_service.get_history(session_id)
        
        # 3. Convert DB history to LangChain messages
        messages = []
        for msg in db_history:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                messages.append(AIMessage(content=msg.content))
                
        # 4. Invoke Agent
        result = self.agent_executor.invoke({"messages": messages})
        final_message = result["messages"][-1]
        
        # 5. Save assistant response to DB
        chat_service.add_message(session_id, "assistant", final_message.content)
        
        return final_message.content
