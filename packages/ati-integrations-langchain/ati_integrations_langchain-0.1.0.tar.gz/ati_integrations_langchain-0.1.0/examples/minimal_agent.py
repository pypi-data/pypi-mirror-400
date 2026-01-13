"""Minimal example: creates the ATI callback handler and runs a simple agent.

This example uses a FakeListLLM to avoid needing API keys, but demonstrates
how spans are generated for Agents, Tools, and LLM calls.
"""

from typing import Any

from langchain.agents import AgentType, initialize_agent
from langchain.tools import Tool
from langchain_community.llms import FakeListLLM

from ati_langchain import LangChainInstrumentor

def dummy_search(query: str) -> str:
    """A dummy search tool."""
    return f"Search results for: {query}"

def main() -> None:
    # 1. Instrument
    instrumentor = LangChainInstrumentor()
    handler = instrumentor.instrument(agent_id="example_agent_v1")
    print(f"ATI LangChain handler enabled: {handler}")

    # 2. Setup LangChain components
    # We use FakeListLLM to simulate an agent that decides to use a tool then finishes.
    # Responses:
    # 1. Thought: ... Action: search ... (triggers tool)
    # 2. Final Answer: ... (finishes)
    responses = [
        "Thought: I need to search for the weather.\nAction: search\nAction Input: weather in SF",
        "Final Answer: The weather in SF is sunny."
    ]
    llm = FakeListLLM(responses=responses)

    tools = [
        Tool(
            name="search",
            func=dummy_search,
            description="useful for conducting searches"
        )
    ]

    # 3. Create Agent
    # Note: callback is passed to the agent executor
    agent_executor = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )

    # 4. Run Agent
    # We pass the handler via callbacks (or configure it globally if preferred, 
    # but explicit passing is cleaner for examples)
    print("\n--- Starting Agent Execution ---\n")
    agent_executor.invoke(
        {"input": "What is the weather in SF?"},
        config={"callbacks": [handler]}
    )
    print("\n--- Finished Agent Execution ---")

    # 5. Cleanup
    instrumentor.uninstrument()

if __name__ == "__main__":
    main()
