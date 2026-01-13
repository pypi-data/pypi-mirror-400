# ATI Integration for AutoGen

This package provides OpenTelemetry instrumentation for AutoGen agents using IOcane ATI.

## Installation

```bash
pip install ati-integrations-autogen
```

## Usage

```python
from ati_autogen import AutoGenInstrumentor
import autogen

# 1. Enable Instrumentation
# This wraps BaseChatAgent.on_messages and BaseTool.run
instrumentor = AutoGenInstrumentor()
instrumentor.instrument()

# 2. Run AutoGen agents
config_list = [{"model": "gpt-4", "api_key": "..."}]
assistant = autogen.AssistantAgent("assistant", llm_config={"config_list": config_list})
user_proxy = autogen.UserProxyAgent("user_proxy")

user_proxy.initiate_chat(assistant, message="Hello!")

# 3. (Optional) Uninstrument
instrumentor.uninstrument()
```

## Configuration

Configure the instrumentation via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `ATI_CAPTURE_PAYLOADS` | Capture message content and tool arguments | `false` |

## Features
- Captures Agent replies (`ati.span.type=agent`)
- Captures Tool usage (`ati.span.type=tool`)
