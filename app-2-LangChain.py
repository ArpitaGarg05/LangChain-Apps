# Building an agent that can help with:
# Order status
# Refund calculation
# Delivery estimate
# General no-tool questions

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
# Fake Database
ORDERS = {
    "ORD-001": {
        "status": "shipped",
        "city": "Delhi",
        "amount": 2000,
        "delivery_days": 2,
    },
    "ORD-002": {
         "status": "cancelled",
        "city": "Bangalore",
        "amount": 1500,
        "delivery_days": 0,
    },
    "ORD-003": {
        "status": "delivered",
        "city": "Delhi",
        "amount": 4000,
        "delivery_days": 0,
    },
    "ORD-004": {
         "status": "delivered",
        "city": "Mumbai",
        "amount": 2500,
        "delivery_days": 0,
    },
}

@tool
def get_order_status(order_id: str) -> str:
    """
    Get the current status of a customer order.
    Use this tool when the user asks about the status, shipment, cancellation, or delivery of a specific order.
    """

    order = ORDERS.get(order_id)

    if not order:
        return f"Order with id: {order_id} not found."
    return f"Order status is {order['status']}, City: {order['city']} & Amount: {order['amount']}"

@tool
def calculate_refund(order_id: str) -> str:
    """
    Calculate refund amount for a cancelled or returned order.
    Use this tool when the user asks about refund amount for a specific order.
    """

    order = ORDERS.get(order_id)

    if not order:
        return f"Order with id: {order_id} not found."
    
    if order['status'] == "cancelled":
        return f"Order with id: {order_id} has been cancelled, refund amount is {order['amount']}."
    
    if order['status'] == "delivered":
        return f"Order with id: {order_id} has been delivered, please initiate the return."
    
    if order['status'] == "shipped":
        return f"Order with id: {order_id} is in transit, return cannot be initiated before delivery."
    
@tool
def estimate_delivery_time(order_id: str) -> str:
    """
    Estimate delivery time for an order.
    Use this tool when the user asks about delivery time or when an order will arrive.
    """

    order = ORDERS.get(order_id)

    if not order:
        return f"Order with id: {order_id} not found."
    
    if order['status'] == "shipped":
        return f"Order {order_id} is expected to arrive in {order['delivery_days']} days."
    
    if order['status'] == "delivered":
        return f"Order {order_id} has already been delivered."
    
    if order['status'] == "cancelled":
        return f"Order {order_id} was cancelled."
    
    return f"Delivery estimate is not available for order {order_id}."
    

llm = ChatOpenAI(
    model='gpt-5.2',
    temperature=0
)

prompt = ChatPromptTemplate.from_messages(
    {
        (
            "System",
            """
            You are a helpful e-commerce support assistant.
            
            Rules:
            1. Use tools only when required.
            2. If the user asks about a specific order, use the relevant tool.
            3. If the user asks a general conceptual question, answer directly without tools.
            4. If order id is missing, ask the user for order id.
            5. Keep the final answer clear and beginner-friendly.
            """
        ),
        (
            "human", "{input}"
        ),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    }
)

tools = [
    get_order_status,
    calculate_refund,
    estimate_delivery_time
]

# An agent is required to make a tool call.
agent = create_tool_calling_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)

# Execute the agent
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    max_iterations=3, #agent will not make a call to a tool more than 3 times if it fails
)

result1 = agent_executor.invoke(
    {
        "input": "Please tell me the status of my order ORD_004."
    }
)
print(result1)

result2 = agent_executor.invoke(
    {
        "input": "Please tell me the delivery estimate of my order ORD_001."
    }
)
print(result2)

result3 = agent_executor.invoke(
    {
        "input": "Please tell me the status and refund amount of my order ORD_002."
    }
)
print(result3)