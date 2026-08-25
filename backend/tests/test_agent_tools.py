from uuid import uuid4
from backend.app.agent.tools import get_agent_tools

def test_agent_tools_factory(db):
    merchant_id = uuid4()
    cart_id = uuid4()
    
    tools = get_agent_tools(db, merchant_id, cart_id)
    
    # Check that we get a list of tools
    assert len(tools) == 4
    
    names = [t.name for t in tools]
    assert "search_products" in names
    assert "get_product_details" in names
    assert "add_to_cart" in names
    assert "view_cart" in names
