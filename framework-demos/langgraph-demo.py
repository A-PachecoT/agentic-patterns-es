from typing import TypedDict, Annotated
from typing_extensions import TypedDict
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


# Define our state
class GraphState(TypedDict):
    topic: str
    fact: str | None


# Define the nodes
def generate_fact(state: GraphState) -> GraphState:
    """Generate an interesting fact about the topic."""
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0.7,
    )

    prompt = PromptTemplate.from_template(
        "Tell me a short interesting fact about {topic}. Keep it under 100 words."
    )

    response = llm.invoke(prompt.format_prompt(topic=state["topic"]))
    return {"topic": state["topic"], "fact": response.content}


def print_fact(state: GraphState) -> GraphState:
    """Print the generated fact."""
    print(f"\nTopic: {state['topic']}")
    print(f"Fact: {state['fact']}\n")
    print("-" * 50)
    return state


def main():
    # Create the graph
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("generate_fact", generate_fact)
    workflow.add_node("print_fact", print_fact)

    # Add edges
    workflow.set_entry_point("generate_fact")
    workflow.add_edge("generate_fact", "print_fact")
    workflow.add_edge("print_fact", END)

    # Compile the graph
    app = workflow.compile()

    # Example topics
    topics = ["artificial intelligence", "space exploration", "quantum computing"]

    print("\nInteresting Facts Generator (Graph Version)")
    print("-" * 50)

    # Run the graph for each topic
    for topic in topics:
        app.invoke({"topic": topic, "fact": None})


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set your OPENAI_API_KEY in a .env file")
    else:
        main()
