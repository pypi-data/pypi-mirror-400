import os
import sys

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langchain.tools import tool

from ati_langchain import LangChainInstrumentor

# OpenTelemetry Setup
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

@tool
def dummy_search(query: str) -> str:
    """Useful for conducting searches. Returns a dummy search result."""
    return f"Search results for: {query}"

def main() -> None:
    # Check for API key
    if "OPENAI_API_KEY" not in os.environ:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please export OPENAI_API_KEY='your-api-key' and run again.")
        sys.exit(1)

    # 1. Configure OpenTelemetry (OTLP)
    # This sets up the SDK to send traces to the OTLP endpoint defined in env vars.
    # We manually handle the endpoint to prevent double-appending of /v1/traces
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    if endpoint and endpoint.endswith("/v1/traces"):
        # If the user included the path, use it as is
        exporter = OTLPSpanExporter(endpoint=endpoint)
    else:
        # Otherwise let the exporter handle defaults (which often appends /v1/traces to base)
        exporter = OTLPSpanExporter()

    provider = TracerProvider()
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    # 2. Instrument
    instrumentor = LangChainInstrumentor()
    handler = instrumentor.instrument(agent_id="example_agent_v1")
    print(f"ATI LangChain handler enabled: {handler}")

    # 2. Setup LangChain components
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    tools = [dummy_search]

    # 3. Create Agent (LangGraph)
    # The prebuilt create_react_agent returns a compiled graph that acts as the executor
    agent = create_react_agent(llm, tools)

    # 4. Run Agent
    print("\n--- Starting Agent Execution ---\n")
    try:
        result = agent.invoke(
            {"messages": [HumanMessage(content="What is the weather in SF?")]},
            config={"callbacks": [handler]}
        )
        print("\nAgent Response:")
        print(result["messages"][-1].content)
    except Exception as e:
        print(f"\nError during execution: {e}")
    
    print("\n--- Finished Agent Execution ---")

    # 5. Cleanup
    instrumentor.uninstrument()
    
    # Ensure all spans are exported before exiting
    provider.shutdown()

if __name__ == "__main__":
    main()
