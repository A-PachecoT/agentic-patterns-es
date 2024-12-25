from typing import TypedDict, Annotated, List, Dict
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

from tools.arxiv import search_papers, get_paper_by_id

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

## TOOLS ##


@tool
def search_arxiv(query: str, max_results: int = 5) -> str:
    """Search arXiv for papers matching the query."""
    logger.info(f"🔍 Searching arXiv for: {query}")

    results = search_papers(query, max_results)

    if not results:
        return "No papers found matching your query."

    response = "Here are the most relevant papers:\n\n"
    for i, paper in enumerate(results, 1):
        response += f"{i}. {paper['title']}\n"
        response += f"   Authors: {', '.join(paper['authors'])}\n"
        response += f"   Published: {paper['published'].strftime('%Y-%m-%d')}\n"
        response += f"   Summary: {paper['summary'][:200]}...\n"
        response += f"   URL: {paper['url']}\n"
        response += f"   Paper ID: {paper['paper_id']}\n\n"

    return response


@tool
def get_paper_details(paper_id: str) -> str:
    """Get detailed information about a specific arXiv paper."""
    logger.info(f"📄 Fetching details for paper: {paper_id}")

    paper = get_paper_by_id(paper_id)
    if "error" in paper:
        return f"Error fetching paper details: {paper['error']}"

    return f"""
Title: {paper['title']}
Authors: {', '.join(paper['authors'])}
Published: {paper['published'].strftime('%Y-%m-%d')}
Categories: {', '.join(paper['categories'])}
Primary Category: {paper['primary_category']}
DOI: {paper['doi'] or 'Not available'}
Journal Reference: {paper['journal_ref'] or 'Not available'}
Comment: {paper['comment'] or 'Not available'}

Abstract:
{paper['summary']}

PDF URL: {paper['url']}
"""


tools = [search_arxiv, get_paper_details]

## LLM SETUP ##

# Create the LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
)

# Create the prompt template
system_message = SystemMessage(
    content="""You are a helpful research assistant specialized in finding academic papers on arXiv. Your role is to:
    1. Understand user requests for research papers and scientific information
    2. Use the search_arxiv tool to find relevant papers based on the query
    3. Use get_paper_details when users want more information about a specific paper
    4. Respond in a clear, academic manner
    5. If the query is too vague, ask for clarification
    
    Important guidelines:
    - Focus on finding the most relevant papers for the user's query
    - Provide concise summaries of the findings
    - If results are too broad, suggest ways to narrow down the search
    - Help users formulate better search queries if needed
    - Always include links to the papers for further reading
    
    Example:
    User: "Find recent papers about transformer architectures"
    Action: Search for papers about transformer architectures, focusing on recent publications"""
)

llm_with_tools = llm.bind_tools(tools)

## GRAPH ##


# Define our state
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


# Node
def assistant(state: AgentState):
    """Agent that processes the user input and returns research information."""
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

research_graph = builder.compile()

## MEMORY CHECKPOINT ##

memory = MemorySaver()
research_graph_memory = builder.compile(checkpointer=memory)

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
        messages = [
            HumanMessage(
                content="Ayúdame a hacer mi tesis de LLM-based Agentic Design Patterns. Solo búscame papers sobre el patrón ReAct porfa."
            )
        ]
        result = research_graph_memory.invoke({"messages": messages}, config)

        # Print results
        for m in result["messages"]:
            if hasattr(m, "pretty_print"):
                m.pretty_print()
            else:
                print(m)
