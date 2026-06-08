# Agent with memory
# normal llm call is stateless.

# MessagePlaceholder(variable_name="chat_history")

# Q1: my order-id is ORD-102.
# R1: okay

# chat_history = [(Q1, R1)]

# Q2: Track it. -> input will be (chat_history + Q2)
# R2: Order in transit.

# chat_history = [(Q1, R1), (Q2, R2)]
# Q3: some new query -> input: (chat_history + Q3)
# R3: ...

# chat_history = [(Q1, R1), (Q2, R2), (Q3, R3)]

# now for next query like 
# Q4: query: chat_history + Q4
# R4: ...

# no more memory available in context window
# so new chat_history will be
# chat_history = [(Q2, R2), (Q3, R3), (Q4, R4)] : remove the message from beginning.


from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.messages import AIMessage, HumanMessage

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

tools = [get_order_status]

llm = ChatOpenAI(
    model='gpt-5.2',
    temperature=0
)

prompt = ChatPromptTemplate.from_messages([
    (
        "System",
        """
        You are a helpful customer support agent.
        
        Rules:
        -If the user gives an order id, remember it for this conversation.
        -If the user asks a follow-up like 'Track it' or 'where is it', use the order id from chat history.
        -Use tools when order status is required.
        -If no order id is available, politely ask the user for order id.
        """
    ),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    # optional is true because there will be no chat history available sometimes such as while beginning a chat
    
    ("human", "{input}"),

    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = create_tool_calling_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools
)

# For the first agent execution, chat history will be empty
chat_history = []

def ask_agent(user_query: str):
    response = agent_executor.invoke(
        {
            "input": user_query,
            "chat_history": chat_history
        }
    )

    answer = response["output"]

    # Append user query and response in the chat_history
    chat_history.append(HumanMessage(content=user_query))
    chat_history.append(AIMessage(content=answer))

    return answer

print("\nTurn 1.")
user_query = "My order-id is ORD-002."

print("User query: ", user_query)
print("AI response: ", ask_agent(user_query))

print("\nTurn 2.")
user_query = "Track it."

print("User query: ", user_query)
print("AI response: ", ask_agent(user_query))