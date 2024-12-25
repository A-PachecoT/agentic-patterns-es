from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

## TOOLS ##


def multiply(a: int, b: int) -> int:
    """
    Multiply a by b
    Args:
        a: int
        b: int
    Returns:
        int: a * b
    """
    return a * b


def divide(a: int, b: int) -> int:
    """
    Divide a by b
    Args:
        a: int
        b: int
    """
    return a / b


def add(a: int, b: int) -> int:
    """
    Add a and b
    Args:
        a: int
        b: int
    Returns:
        int: a + b
    """
    return a + b


def subtract(a: int, b: int) -> int:
    """
    Subtract b from a
    Args:
        a: int
        b: int
    Returns:
        int: a - b
    """
    return a - b


def exponent(a: float, b: float) -> float:
    """
    Exponent a to the power of b
    Args:
        a: float - the base number
        b: float - the exponent (can be fractional for roots)
    Returns:
        float: a**b
    """
    return a**b


tools = [multiply, divide, add, subtract, exponent]

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

llm_with_tools = llm.bind_tools(tools)


## GRAPH ##

from langgraph.graph import MessagesState
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


# System message
system_message = SystemMessage(
    content="""
    You are a helpful assistant with tools to perform basic arithmetic operations.
    You will be given a mathematical expression and you will need to calculate the result.
    You will use the tools to perform the calculations.
    ALWAYS use the correct order of operations.
    1. Parentheses
    2. Exponents
    3. Multiplication and Division (from left to right)
    4. Addition and Subtraction (from left to right)

    Note:
    Square roots is not a tool, but you can use the exponent tool to calculate the square root of a number.
    Example: Square root of 16 is 4, because exponent(16, 0.5) = 4
    """
)


# Node
def assistant(state: MessagesState):
    message = llm_with_tools.invoke([system_message] + state["messages"])
    return {"messages": [message]}


from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode
from IPython.display import display, Image

# Define the graph
builder = StateGraph(MessagesState)

# Add nodes
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

# Add edges: They determine how the control flow moves
builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")

react_graph = builder.compile()

# Display the graph
# display(Image(react_graph.get_graph(xray=True).draw_mermaid_png()))

# Save the graph image
graph_image = react_graph.get_graph(xray=True).draw_mermaid_png()
with open("calculator_graph.png", "wb") as f:
    f.write(graph_image)
# display(Image(graph_image))


## MEMORY CHECKPOINT ##

from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
react_graph_memory = builder.compile(checkpointer=memory)

# Specify a thread

config = {"configurable": {"thread_id": "1"}}

# Specify the input
messages = [HumanMessage(content="Dime la raíz cuadrada de (1234+47^2)/123")]


# Run the graph
result = react_graph_memory.invoke({"messages": messages}, config)

# Pretty print the result
# Json:
# import json

# print("\nResult:")
# print(json.dumps({"messages": [msg.dict() for msg in result["messages"]]}, indent=2))

# Pretty print:
for m in result["messages"]:
    m.pretty_print()

## LANGSMITH TRACE ##

import os, getpass


def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")


_set_env("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "lang-sandbox"
