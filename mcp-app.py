from mcp.server.fastmcp import FastMCP
import json

mcp = FastMCP("Ecommerce Chat Support System MCP Server")

# FAKE DATABASE
ORDERS = {
    "ORD-1001": {
        "customer_name": "Priya",
        "status": "Delivered",
        "expected_delivery": "Delivered 12 days ago",
        "amount": 3499,
        "payment_status": "Paid",
        "cancellable": False,
        "delivered": True,
        "days_since_delivery": 12,
    },
    "ORD-1002": {
        "customer_name": "Mukul",
        "status": "Shipped",
        "expected_delivery": "Delivery in 5 days",
        "amount": 2500,
        "payment_status": "Paid",
        "cancellable": True,
        "delivered": False,
        "days_since_delivery": 0,
    },
    "ORD-1003": {
        "customer_name": "Rishi",
        "status": "Delivered",
        "expected_delivery": "Delivered 3 days ago",
        "amount": 1599,
        "payment_status": "",
        "cancellable": True,
        "delivered": True,
        "days_since_delivery": 3,
    },
    "ORD-1004": {
        "customer_name": "Riya",
        "status": "Cancelled",
        "expected_delivery": "",
        "amount": 499,
        "payment_status": "",
        "cancellable": True,
        "delivered": False,
        "days_since_delivery": 0,
    },
}

# FAKE Return Policy DOC
RETURN_POLICY = """
Return and Refund Policy:

1. Products can be returned within 7 days of delivery.
2. Product must be unused and in original packaging.
3. Refund is processed only after return pickup and quality check.
4. Orders that are already out for delivery cannot be cancelled.
5. Shipped orders can be cancelled only before they are out for delivery.
6. Delivered orders cannot be cancelled, but they may be eligible for return.
"""

# Resource to return the order data -> Provide the link to the resource.
@mcp.resource("store://orders/{order_id}") # wrong sample link
def get_order_details(order_id: str) -> str:
    """This function returns the order details for the given order id from database."""

    order = ORDERS.get(order_id)
    if not order:
        return "Order with given order-id not found."
    
    # return the order details in json format instead of object format.
    return json.dumps(order)

# Resource to fetch the resource -> Provide the link to the resource.
@mcp.resource("store://policy/returns") # wrong sample link
def get_return_policy() -> str:
    """Returns the return policy."""

    return RETURN_POLICY

@mcp.tool()
def get_order_status(order_id: str) -> str:
    """Tool to return the order status for given order id."""

    order = ORDERS.get(order_id)

    if not order:
        return "Order with given order-id not found."
    
    return f"Order with id {order_id} is {order['status']}"

@mcp.tool()
def calculate_refund(order_id: str) -> str:
    """Tool to calculate refund of the given order id."""

    order = ORDERS.get(order_id)

    if not order:
        return "Order with given order-id not found."
    
    if order['status'] == "Delivered":
        return f"Order already delivered. Please proceed with return of the product if eligible."
    if order["status"] == "Cancelled":
        return f"Order with given order id was cancelled. Therefore no refund available."
    if order["status"] == "Shipped":
        return f"Order with given order id is in transit, refund amount will be {order['amount']}."
    
    return f"Refund amount will be {order['amount']}"

@mcp.tool()
def cancel_order(order_id: str) -> str:
    """Tool to check if an order with given order id is eligible for cancellation."""

    order = ORDERS.get(order_id)

    if not order:
        return "Order with given order-id not found."
    
    if order['status'] == "Delivered":
        return "Order with given order id already delivered. It cannot be cancelled"
    if order["status"] == "Cancelled":
        return "Order with given order id was already cancelled."
    if order["status"] == "Shipped":
        return "Order with given order id is in transit, it may be eligible for cancellation."
    return "Order can be cancelled."

@mcp.prompt(title="Customer Support Reply")
def customer_support_reply(order_id: str, customer_message: str) -> str:
    """Creates a reusable prompt for customer support scenarios."""
    return f"""
    You are a polite and practical e-commerce customer support assistant.
    
    Customer message:
    {customer_message}

    Order-id:
    {order_id}
    
    Instructions:
    1. First check the order status using the available tool.
    2. If the customer asks for refund, check refund eligibility.
    3. If the customer asks for cancellation, cancel only if the order is cancellable.
    4. Do not promise refund unless refund eligibility is confirmed.
    5. Keep the response short, clear and helpful.
    """

if __name__ == "__main__":
    # mcp.run(transport="stdio")
    print(get_order_status("ORD-1001"))
    print(calculate_refund("ORD-1002"))