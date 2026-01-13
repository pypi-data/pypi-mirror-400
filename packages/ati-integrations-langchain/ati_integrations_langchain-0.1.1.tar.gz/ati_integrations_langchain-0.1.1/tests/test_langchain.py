
import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry import trace

from langchain.agents import AgentType, initialize_agent
from langchain.tools import Tool
from langchain_community.llms import FakeListLLM

from ati_langchain import LangChainInstrumentor
from ati_sdk.semantics import ATI_ATTR, AtiSpanType

@pytest.fixture
def memory_exporter():
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    processor = SimpleSpanProcessor(exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    return exporter

def test_langchain_agent_instrumentation(memory_exporter):
    # Setup
    instrumentor = LangChainInstrumentor()
    # Ensure clean state
    instrumentor.uninstrument()
    
    handler = instrumentor.instrument(agent_id="test_agent")

    # Mocks
    responses = [
        "Thought: I need to use a tool.\nAction: test_tool\nAction Input: hello",
        "Final Answer: Done."
    ]
    llm = FakeListLLM(responses=responses)
    
    def dummy_func(x):
        return "tool_output"
        
    tools = [
        Tool(name="test_tool", func=dummy_func, description="test tool")
    ]

    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    )

    # Execution
    agent.invoke({"input": "task"}, config={"callbacks": [handler]})

    # Verification
    spans = memory_exporter.get_finished_spans()
    
    # We expect at least:
    # 1. Chain span (agent execution)
    # 2. LLM span (first call)
    # 3. Tool span (test_tool)
    # 4. LLM span (second call - final answer)
    
    assert len(spans) >= 4
    
    # Check Chain Span
    chain_spans = [s for s in spans if s.attributes.get(ATI_ATTR.span_type) == AtiSpanType.STEP]
    assert chain_spans, "No chain/step spans found"
    assert chain_spans[0].attributes[ATI_ATTR.agent_id] == "test_agent"
    
    # Check LLM Span
    llm_spans = [s for s in spans if s.attributes.get(ATI_ATTR.span_type) == AtiSpanType.LLM]
    assert llm_spans, "No LLM spans found"
    assert llm_spans[0].attributes[ATI_ATTR.agent_id] == "test_agent"
    
    # Check Tool Span
    tool_spans = [s for s in spans if s.attributes.get(ATI_ATTR.span_type) == AtiSpanType.TOOL]
    assert tool_spans, "No tool spans found"
    t_span = tool_spans[0]
    assert t_span.name == "langchain.tool.call"
    assert t_span.attributes[ATI_ATTR.tool_name] == "test_tool"
    
    # Cleanup
    instrumentor.uninstrument()
