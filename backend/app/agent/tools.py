from typing import Annotated
from uuid import UUID
from langchain_core.tools import tool
from sqlalchemy.orm import Session

from ..services.product_service import ProductService
from ..services.cart import CartService

def get_agent_tools(db: Session, merchant_id: UUID, cart_id: UUID | None):
    """
    Factory to generate tools bound to the current database session, merchant, and cart.
    """

    @tool
    def search_products(
        query: Annotated[str, "The search string to find products. Examples: 'running shoes', 'red socks', 'budget laptop'."],
    ) -> str:
        """Search for products in the merchant's catalog based on semantic meaning or keywords."""
        service = ProductService(db)
        # Search returns top 5
        products = service.search_products(query=query, merchant_id=merchant_id, top_k=5)
        
        if not products:
            return "No products found matching your search."
            
        result = "Found the following products:\n\n"
        for p in products:
            result += f"- ID: {p.id}\n  Name: {p.name}\n  Price: {p.currency} {p.price}\n  Description: {p.description}\n\n"
        return result

    @tool
    def get_product_details(
        product_id: Annotated[str, "The UUID of the product to retrieve."],
    ) -> str:
        """Get full details of a specific product using its ID."""
        service = ProductService(db)
        try:
            p_id = UUID(product_id)
        except ValueError:
            return "Invalid product ID format."
            
        p = service.get_by_id(p_id)
        if not p or p.merchant_id != merchant_id:
            return "Product not found."
            
        stock = p.inventory.quantity if p.inventory else 0
        return (
            f"Product Name: {p.name}\n"
            f"ID: {p.id}\n"
            f"SKU: {p.sku}\n"
            f"Price: {p.currency} {p.price}\n"
            f"Stock Available: {stock}\n"
            f"Description: {p.description}\n"
        )

    @tool
    def add_to_cart(
        product_id: Annotated[str, "The UUID of the product to add to the cart."],
        quantity: Annotated[int, "The number of items to add."],
    ) -> str:
        """Add a specific product to the customer's cart. You MUST have the exact product_id before calling this."""
        if not cart_id:
            return "Error: No active cart available to add items."
            
        try:
            p_id = UUID(product_id)
        except ValueError:
            return "Invalid product ID format."
            
        service = CartService(db)
        try:
            item = service.add_item(cart_id=cart_id, product_id=p_id, quantity=quantity)
            return f"Successfully added {quantity} of product {product_id} to cart. Total items in this cart line: {item.quantity}."
        except ValueError as exc:
            return f"Failed to add to cart: {str(exc)}"

    @tool
    def view_cart() -> str:
        """View the current contents and total of the customer's shopping cart."""
        if not cart_id:
            return "The cart is currently empty (no cart created)."
            
        service = CartService(db)
        try:
            cart = service.get_cart(cart_id=cart_id)
        except ValueError:
            return "Cart not found."
            
        if not cart.items:
            return "The cart is currently empty."
            
        result = "Current Cart Contents:\n\n"
        total = 0
        for item in cart.items:
            # item.product relation might not be eagerly loaded, but in our SQLAlchemy setup it usually is or lazy-loads
            p_name = item.product.name if item.product else "Unknown Product"
            p_price = item.product.price if item.product else 0
            line_total = item.quantity * p_price
            total += line_total
            result += f"- {p_name} (ID: {item.product_id})\n  Quantity: {item.quantity} | Unit Price: {p_price} | Line Total: {line_total}\n"
            
        result += f"\nGrand Total: {total}"
        return result

    return [search_products, get_product_details, add_to_cart, view_cart]
