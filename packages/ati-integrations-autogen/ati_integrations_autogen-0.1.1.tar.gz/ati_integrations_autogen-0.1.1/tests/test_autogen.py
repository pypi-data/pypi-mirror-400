
import pytest
import asyncio
from unittest.mock import MagicMock

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry import trace

from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
import autogen_core.tools

from ati_autogen import AutoGenInstrumentor
from ati_sdk.semantics import ATI_ATTR, AtiSpanType

@pytest.fixture
def memory_exporter():
    exporter = InMemorySpanExporter()
    return exporter

# Simple Agent for testing
class EchoAgent(BaseChatAgent):
    def __init__(self, name: str):
        super().__init__(name, "echo")

    @property
    def produced_message_types(self):
        return (TextMessage,)

    async def on_messages(self, messages, cancellation_token):
        return TextMessage(content="Echo", source=self.name)
    
    async def on_reset(self, cancellation_token):
        pass

@pytest.mark.asyncio
async def test_autogen_instrumentation(memory_exporter):
    # Setup Tracer
    provider = TracerProvider()
    processor = SimpleSpanProcessor(memory_exporter)
    provider.add_span_processor(processor)

    # Instrument
    instrumentor = AutoGenInstrumentor()
    instrumentor.uninstrument()
    instrumentor.instrument()
    
    # Inject local tracer
    instrumentor.tracer.tracer = provider.get_tracer("ati.autogen")

    try:
        # Create Agent (AFTER instrumentation so __init__ is patched)
        agent = EchoAgent("echo_test")
        
        # Run Agent
        token = CancellationToken()
        msg = TextMessage(content="Hello", source="user")
        
        await agent.on_messages([msg], token)
        
        # Verify Agent Span
        spans = memory_exporter.get_finished_spans()
        agent_spans = [s for s in spans if s.name == "autogen.agent.on_messages"]
        assert len(agent_spans) == 1
        span = agent_spans[0]
        assert span.attributes[ATI_ATTR.span_type] == AtiSpanType.AGENT
        assert span.attributes[ATI_ATTR.agent_id] == "echo_test"

        # Verify Uninstrument
        instrumentor.uninstrument()
        
        # New agent shouldn't have wrapped method
        agent2 = EchoAgent("echo_test_2")
        # Check if attribute is wrapped? Hard to check implementation, 
        # but execution shouldn't produce span.
        
        memory_exporter.clear()
        await agent2.on_messages([msg], token)
        assert len(memory_exporter.get_finished_spans()) == 0

    finally:
        instrumentor.uninstrument()
