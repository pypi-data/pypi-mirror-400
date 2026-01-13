# ATI Integration for LangChain

This package provides OpenTelemetry instrumentation for LangChain agents using IOcane ATI.

## Installation

```bash
pip install ati-integrations-langchain
```

## Usage

```python
from ati_langchain import LangChainInstrumentor
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType

# 1. Enable Instrumentation
# This returns a callback handler that captures ATI spans.
handler = LangChainInstrumentor().instrument()

# 2. Use in LangChain
llm = ChatOpenAI(temperature=0, callbacks=[handler])
# or pass globally if using a CallbackManager
```

## Configuration

Configure the instrumentation via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `ATI_CAPTURE_PAYLOADS` | Capture input/output payloads (redacted) | `false` |
| `ATI_DEBUG` | Enable debug logging | `false` |

## Features
- Captures LLM calls (`ati.span.type=llm`)
- Captures Tool usage (`ati.span.type=tool`)
- Captures Chain/Agent execution steps
