from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def main():
    # Initialize the LLM
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0.7,
    )

    # Create a prompt template
    prompt = PromptTemplate.from_template(
        "Tell me a short interesting fact about {topic}. Keep it under 100 words."
    )

    # Create a simple chain
    chain = prompt | llm | StrOutputParser()

    # Example topics
    topics = ["artificial intelligence", "space exploration", "quantum computing"]

    print("\nInteresting Facts Generator")
    print("-" * 50)

    for topic in topics:
        print(f"\nTopic: {topic}")
        response = chain.invoke({"topic": topic})
        print(f"Fact: {response}\n")
        print("-" * 50)


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set your OPENAI_API_KEY in a .env file")
    else:
        main()
