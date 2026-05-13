import logging
from typing import Annotated

from fastmcp import FastMCP, Context
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(message)s")
logger = logging.getLogger("StoreMCP")
logger.setLevel(logging.INFO)

mcp = FastMCP("Justin's Vinyl Store")  # TODO: Name your store!


class PurchaseConfirmation(BaseModel):
    confirm: bool = Field(title="Confirm purchase", description="Approve this transaction?")


# In-memory product inventory: name -> {price, quantity}
INVENTORY = {
    "Radiohead": {"price": 20.0, "quantity": 10},
    "The Beatles": {"price": 25.0, "quantity": 5},
    "Pink Floyd": {"price": 22.0, "quantity": 8},
}

@mcp.tool
async def list_products() -> dict[str, dict[str, float | int]]:
    """List all available products with their prices and stock levels."""
    return INVENTORY 

@mcp.tool
async def buy_product(
    product_name: Annotated[str, "The name of the product to buy"],
    quantity: Annotated[int, "The quantity of the product to buy"],
    ctx: Context,
) -> str:
    """Buy a product from the store, reducing its inventory."""
    if(product_name not in INVENTORY):
        return f"Error: Product '{product_name}' not found."
    if(INVENTORY[product_name]['quantity'] < quantity):
        return f"Error: Not enough stock for '{product_name}'. Only {INVENTORY[product_name]['quantity']} left."
    else:
        product = INVENTORY[product_name]
        total = product["price"] * quantity

        # Ask the user to confirm before purchasing
        response = await ctx.elicit(
            message=f"Buy {quantity}x {product_name} for ${total:.2f}?",
            response_type=PurchaseConfirmation,
        )

        if response.action != "accept" or not response.data.confirm:
            return "Purchase cancelled."
        else:
            INVENTORY[product_name]['quantity'] -= quantity
            return f"Success: Purchased {quantity} of '{product_name}'."
 
@mcp.prompt 
async def custom_prompt() -> str:
    """Custom system prompt to guide the agent's behavior."""
    return (
        "You are a helpful assistant for Justin's Vinyl Store. "
        "Use the available tools to list products and process purchases. "
        "Always check inventory levels before confirming a purchase."
    )

@mcp.resource("resource://store_info")
async def store_info() -> dict[str, str]:
    """Provide general information about the store."""
    return {
        "name": "Justin's Vinyl Store",
        "location": "123 Music Lane, Melody City",
        "hours": "Mon-Sat 10am-8pm, Sun 12pm-6pm"
    }

if __name__ == "__main__":
    logger.info("Store MCP server starting (HTTP mode on port 8420)")
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8420)