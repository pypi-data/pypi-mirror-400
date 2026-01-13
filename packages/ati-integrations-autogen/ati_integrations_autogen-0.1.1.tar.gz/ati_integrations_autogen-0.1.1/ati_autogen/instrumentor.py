from __future__ import annotations

import functools
from dataclasses import dataclass
from typing import Any, Callable

import autogen_agentchat.agents
import autogen_core.tools
from ati_sdk import AtiConfig, AtiTracer
from ati_sdk.semantics import AtiSpanType, ATI_ATTR
from opentelemetry.trace import Status, StatusCode

@dataclass
class AutoGenInstrumentor:
    _enabled: bool = False
    _original_on_messages: Callable | None = None
    _original_tool_run: Callable | None = None
    tracer: AtiTracer | None = None

    def instrument(self, config: AtiConfig | None = None) -> None:
        if self._enabled:
            return
        cfg = AtiConfig.from_env().merged(config)
        self.tracer = AtiTracer(framework="autogen", tracer_name="ati.autogen", config=cfg)

        self._instrument_agent()
        self._instrument_tool()
        self._enabled = True

    def _instrument_agent(self) -> None:
        self._original_init = autogen_agentchat.agents.BaseChatAgent.__init__
        instrumentor = self
        
        # We can't easily use functools.wraps on __init__ for the wrapper signature if we want specific args, 
        # but generic *args works.
        
        def init_wrapper(agent_self: Any, *args: Any, **kwargs: Any) -> None:
            # Call original init
            instrumentor._original_init(agent_self, *args, **kwargs)
            
            # Wrap on_messages
            if hasattr(agent_self, "on_messages"):
                original_on_messages = agent_self.on_messages
                
                async def on_messages_wrapper(messages: Any, cancellation_token: Any) -> Any:
                    if not instrumentor.tracer:
                        return await original_on_messages(messages, cancellation_token)
                    
                    agent_name = getattr(agent_self, "name", "unknown_agent")
                    agent_id = agent_name
                    
                    span = instrumentor.tracer.start_span(
                        "autogen.agent.on_messages",
                        AtiSpanType.AGENT,
                        agent_id=agent_id,
                        agent_name=agent_name,
                        attributes={
                            ATI_ATTR.step_type: "reply",
                        }
                    )
                    try:
                        return await original_on_messages(messages, cancellation_token)
                    except Exception as e:
                        span.record_exception(e)
                        span.set_status(Status(StatusCode.ERROR))
                        raise
                    finally:
                        span.end()

                agent_self.on_messages = on_messages_wrapper

        autogen_agentchat.agents.BaseChatAgent.__init__ = init_wrapper

    def uninstrument(self) -> None:
        if not self._enabled:
            return
        if hasattr(self, "_original_init") and self._original_init:
            autogen_agentchat.agents.BaseChatAgent.__init__ = self._original_init
            self._original_init = None
            
        if self._original_tool_run:
            autogen_core.tools.BaseTool.run = self._original_tool_run
            self._original_tool_run = None
        self._enabled = False

    def _instrument_tool(self) -> None:
        self._original_tool_run = autogen_core.tools.BaseTool.run
        
        @functools.wraps(self._original_tool_run)
        async def wrapper(tool: Any, input_data: Any, cancellation_token: Any) -> Any:
             if not self.tracer:
                 return await self._original_tool_run(tool, input_data, cancellation_token)
             
             tool_name = getattr(tool, "name", "unknown_tool")
             
             span = self.tracer.start_span(
                 "autogen.tool.run",
                 AtiSpanType.TOOL,
                 attributes={
                     ATI_ATTR.tool_name: tool_name
                 }
             )
             
             if self.tracer.config.capture_payloads:
                 self.tracer.add_payload_event(
                     span, kind="tool_args", content=str(input_data),
                     redaction_patterns=(), enabled=True
                 )

             try:
                 return await self._original_tool_run(tool, input_data, cancellation_token)
             except Exception as e:
                 span.record_exception(e)
                 span.set_status(Status(StatusCode.ERROR))
                 raise
             finally:
                 span.end()

        autogen_core.tools.BaseTool.run = wrapper
