# ATI Integration for LangChain

This package provides OpenTelemetry instrumentation for LangChain agents using IOcane ATI. It captures traces for LLM calls, Tools, and Agent execution steps, allowing you to visualize your agent's behavior in the Iocane dashboard.

## Installation

You can install the package and its required dependencies from PyPI (or your local source):

```bash
# Install the integration and OpenTelemetry components
pip install ati-integrations-langchain opentelemetry-sdk opentelemetry-exporter-otlp langgraph langchain-openai
```

### Local Development
If you are developing this package locally:
```bash
pip install -e .
```

## Configuration

The integration relies on standard OpenTelemetry environment variables to export traces to Iocane.

### 1. Endpoint and Authentication
Set the following environment variables. You can find your **Environment ID** and **API Key** in the Iocane Dashboard under *Settings > Environment*.

```bash
# The Iocane OTLP Endpoint
export OTEL_EXPORTER_OTLP_ENDPOINT="https://api.iocane.ai"

# Authentication Headers
# Replace YOUR_KEY and YOUR_ENV_ID with your actual values.
# Note: Format is comma-separated key=value pairs.
export OTEL_EXPORTER_OTLP_HEADERS="x-iocane-key=YOUR_KEY,x-ati-env=YOUR_ENV_ID"
```

### 2. Service Name
Identify your agent service:
```bash
export OTEL_SERVICE_NAME="my-langchain-agent"
```

### 3. OpenAI Key
If using OpenAI models:
```bash
export OPENAI_API_KEY="sk-..."
```

## Usage

To use this integration, you must:
1.  Configure the OpenTelemetry SDK globally to export traces.
2.  Instrument your LangChain application using `LangChainInstrumentor`.

Here is a complete example:

```python
import os
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from ati_langchain import LangChainInstrumentor

# --- 1. Configure OpenTelemetry (OTLP) ---
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

# Initialize Tracer Provider
provider = TracerProvider()

# Configure OTLP Exporter
# Note: Ensure the endpoint URL is correct (TracerProvider adds /v1/traces if not present, but explicit is safer)
endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
if endpoint and endpoint.endswith("/v1/traces"):
    exporter = OTLPSpanExporter(endpoint=endpoint)
else:
    # Let the exporter handle default pathing
    exporter = OTLPSpanExporter()

# Add the exporter to the provider
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)

# --- 2. Instrument LangChain ---
# This automatically captures traces for all subsequent LangChain & LangGraph execution.
LangChainInstrumentor().instrument(agent_id="my-agent-v1")

# --- 3. Define your Agent ---
@tool
def magic_tool(query: str) -> str:
    """A sample tool."""
    return f"Magic result for: {query}"

llm = ChatOpenAI(model="gpt-3.5-turbo")
tools = [magic_tool]
agent = create_react_agent(llm, tools)

# --- 4. Run the Agent ---
print("Running agent...")
try:
    response = agent.invoke({"messages": [("user", "What is the magic answer?")]})
    print("Response:", response["messages"][-1].content)
finally:
    # --- 5. Cleanup ---
    # Ensure all traces are sent before exiting
    provider.shutdown()
```

## Troubleshooting

### No Traces in Dashboard
-   **Check `OTEL_EXPORTER_OTLP_HEADERS`**: Ensure `x-ati-env` matches the Environment ID selected in your dashboard. Mismatches are common.
-   **Flush Traces**: Ensure you call `provider.shutdown()` at the end of your script. `BatchSpanProcessor` sends traces asynchronously; if the script exits too fast, traces are lost.

### 404 Error (Endpoint)
-   If you see 404 errors, your `OTEL_EXPORTER_OTLP_ENDPOINT` might be incorrect.
    -   Use `https://api.iocane.ai` (SDK appends `/v1/traces` automatically).
    -   OR use `https://api.iocane.ai/v1/traces` and handle it manually in your code (as shown in the example).

### Collector Decode Error
-   If the Collector logs show `utf-8 codec can't decode byte`, ensure your Collector matches the version that supports Protobuf ingestion (`application/x-protobuf`), or force the exporter to use JSON (though Protobuf is preferred).
