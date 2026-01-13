
import os
import asyncio
from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from ati_autogen import AutoGenInstrumentor

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

class EchoAgent(BaseChatAgent):
    def __init__(self, name: str):
        super().__init__(name, "An echo agent")

    @property
    def produced_message_types(self):
        return (TextMessage,)

    async def on_messages(self, messages, cancellation_token):
        return await self._generate_reply(messages)

    async def _generate_reply(self, messages):
        # Simulate some work to ensure span duration is visible > 0ms
        await asyncio.sleep(0.5)
        last_msg = messages[-1].content
        print(f"  [EchoAgent] Received: {last_msg}")
        return TextMessage(content=f"Echo: {last_msg}", source=self.name)

    async def on_reset(self, cancellation_token):
        pass

async def main():
    # 1. Configure OpenTelemetry
    resource = Resource.create(attributes={SERVICE_NAME: "ati-autogen-example"})
    
    # Robust Provider Initialization
    try:
        provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(provider)
    except Exception:
        pass
    provider = trace.get_tracer_provider()

    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    if endpoint and endpoint.endswith("/v1/traces"):
        exporter = OTLPSpanExporter(endpoint=endpoint)
    else:
        exporter = OTLPSpanExporter()
        
    if hasattr(provider, "add_span_processor"):
        provider.add_span_processor(BatchSpanProcessor(exporter))
        # Optional: Console output for verification
        # provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    # 2. Instrument
    instrumentor = AutoGenInstrumentor()
    instrumentor.instrument()
    
    try:
        print("Creating Agent...")
        agent = EchoAgent("echo_agent")
        
        print("Sending message to agent...")
        # Simulate a message interaction
        # Note: In real usage, you'd use a Team or stricter message passing
        msg = TextMessage(content="Hello AutoGen!", source="user")
        
        # We need a cancellation token
        token = CancellationToken()
        
        response = await agent.on_messages([msg], token)
        print(f"Agent Response: {response.content}")
        
    finally:
        # 3. Cleanup
        if hasattr(provider, "shutdown"):
            provider.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
