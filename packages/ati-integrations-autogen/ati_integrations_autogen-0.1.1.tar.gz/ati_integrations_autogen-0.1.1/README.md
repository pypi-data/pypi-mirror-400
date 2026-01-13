# ATI Integration for AutoGen

This package provides OpenTelemetry instrumentation for [AutoGen](https://github.com/microsoft/autogen) agents using Iocane ATI.

It automatically captures:
- **Agent replies**: The conversation flow between agents.
- **Tool usage**: Execution of registered tools and their arguments.

## Installation

```bash
pip install ati-integrations-autogen opentelemetry-sdk opentelemetry-exporter-otlp
```

## Configuration

Set the standard OpenTelemetry environment variables to point to your Iocane collector:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT="https://api.iocane.ai/v1/traces"
export OTEL_EXPORTER_OTLP_HEADERS="x-iocane-key=YOUR_KEY,x-ati-env=YOUR_ENV_ID"
export OTEL_SERVICE_NAME="my-autogen-agent"
```

## Usage

Here is the robust pattern for instrumenting AutoGen scripts.

**Important**: Because AutoGen or other libraries might initialize OpenTelemetry internally (or if you are running in a notebook), it is best practice to *attempt* to set the provider, but always *retrieve* the active global provider to attach your exporters.

```python
import os
import asyncio
from ati_autogen import AutoGenInstrumentor
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent

# OpenTelemetry Imports
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

async def main():
    # 1. Configure OpenTelemetry (Robust Pattern)
    resource = Resource.create(attributes={SERVICE_NAME: "my-autogen-service"})
    
    try:
        # Try to set the global provider
        provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(provider)
    except Exception:
        # If it fails (e.g., already set), ignore and fetch the active one below
        pass

    # ALWAYS get the global provider to ensure we attach to the active pipeline
    provider = trace.get_tracer_provider()

    # 2. Configure Exporter (Iocane)
    # Ensure usage of the correct endpoint from env or default
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    if endpoint and endpoint.endswith("/v1/traces"):
        exporter = OTLPSpanExporter(endpoint=endpoint)
    else:
        exporter = OTLPSpanExporter()
        
    if hasattr(provider, "add_span_processor"):
        provider.add_span_processor(BatchSpanProcessor(exporter))
    else:
        print("WARNING: TracerProvider does not support add_span_processor.")

    # 3. Instrument AutoGen
    instrumentor = AutoGenInstrumentor()
    instrumentor.instrument()

    try:
        # 4. Your AutoGen Code
        assistant = AssistantAgent("assistant", system_message="You are helpful.")
        user_proxy = UserProxyAgent("user_proxy", code_execution_config=False)
        
        await user_proxy.initiate_chat(assistant, message="Hello!")

    finally:
        # 5. Flush traces
        if hasattr(provider, "shutdown"):
            provider.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

## Environment Variables for Instrumentation

| Variable | Description | Default |
|----------|-------------|---------|
| `ATI_CAPTURE_PAYLOADS` | set to `true` to capture message content and tool arguments as span events | `false` |
