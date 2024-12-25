from typing import TypedDict, Annotated
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolExecutor, tools_condition, ToolNode
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
import os
import logging
import getpass
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from tools.weather import get_weather as fetch_weather, convert_celsius_to_fahrenheit

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

## TOOLS ##


@tool
def get_weather(city: str) -> str:
    """Get the weather for a specific city."""
    logger.info(f"🔧 Getting weather for: {city}")

    result = fetch_weather(city)
    if "error" in result:
        return f"Sorry, {result['error']}"

    temp_c = result["temperature"]
    temp_f = convert_celsius_to_fahrenheit(temp_c)
    condition = result["condition"]
    humidity = result["humidity"]

    return f"Weather in {city.title()}: {temp_c:.1f}°C ({temp_f:.1f}°F), {condition}, {humidity}% humidity"


@tool
def convert_to_celsius(fahrenheit: float) -> float:
    """Convert a temperature from Fahrenheit to Celsius."""
    return (fahrenheit - 32) * 5 / 9


tools = [get_weather, convert_to_celsius]

## LLM SETUP ##

# Create the LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
)

# Create the prompt template
system_message = SystemMessage(
    content="""You are a helpful weather assistant. Your role is to:
    1. Understand user requests for weather information
    2. Use the get_weather tool to fetch current conditions ONLY for the specific city mentioned
    3. Respond in a clear, friendly manner
    4. If no city is explicitly mentioned, ask the user which city they're interested in

    Important guidelines:
    - Only check weather for explicitly mentioned cities
    - The weather data is already provided in both Celsius and Fahrenheit
    - If a location is not found, politely inform the user and ask for clarification
    - If the user's language includes slang or informal terms for a city, translate it to the proper city name.
    
    Some examples of petitions:
    - "¿Cuántos grados hace en Lima?" -> tool call: get_weather("Lima")
    - "Hoy lloverá en Ayacucho?" -> tool call: get_weather("Ayacucho")
    """
)

llm_with_tools = llm.bind_tools(tools)

## GRAPH ##


# Define our state
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


# Node
def assistant(state: AgentState):
    """Agent that processes the user input and returns weather information."""
    messages = state["messages"]
    message = llm_with_tools.invoke([system_message] + messages)
    return {"messages": [message]}


# Define the graph
builder = StateGraph(AgentState)

# Add nodes
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

# Add edges
builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")

weather_graph = builder.compile()

## MEMORY CHECKPOINT ##

memory = MemorySaver()
weather_graph_memory = builder.compile(checkpointer=memory)

## LANGSMITH TRACE ##


def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set your OPENAI_API_KEY in a .env file")
    else:
        # Set up LangSmith tracing
        _set_env("LANGCHAIN_API_KEY")
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = "lang-sandbox"

        # Example usage
        config = {"configurable": {"thread_id": "1"}}
        messages = [HumanMessage(content="Está soleado hoy en Lima?")]
        result = weather_graph_memory.invoke({"messages": messages}, config)

        # Print results
        for m in result["messages"]:
            if hasattr(m, "pretty_print"):
                m.pretty_print()
            else:
                print(m)
