
import asyncio
from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from ati_autogen import AutoGenInstrumentor

class EchoAgent(BaseChatAgent):
    def __init__(self, name: str):
        super().__init__(name, "An echo agent")

    @property
    def produced_message_types(self):
        return (TextMessage,)

    async def on_messages(self, messages, cancellation_token):
        # We override on_messages, but the instrumentor wraps BaseChatAgent.on_messages.
        # Wait, if we override it, the wrapper on BaseChatAgent.on_messages might NOT be called
        # if we don't call super() or if the wrapper is on the class.
        # The instrumentor wraps BaseChatAgent.on_messages.
        # If EchoAgent defines on_messages, it replaces the method on the instance/class.
        # The wrapper on BaseChatAgent only affects instances that use BaseChatAgent.on_messages implementation??
        # No, inheritance doesn't automatically wrap overridden methods.
        # This is a problem with monkeypatching base classes.
        
        # However, checking instrumentation:
        # self._instrument_agent() wraps autogen_agentchat.agents.BaseChatAgent.on_messages.
        # If subclass overrides it, it doesn't call base unless super().on_messages() is called.
        # BaseChatAgent.on_messages is abstract?
        return await self._generate_reply(messages)

    async def _generate_reply(self, messages):
         last_msg = messages[-1].content
         return TextMessage(content=f"Echo: {last_msg}", source=self.name)

    async def on_reset(self, cancellation_token):
        pass

# Better approach for example: Use an existing agent or ensure wrapping works.
# Or just call super().on_messages? BaseChatAgent.on_messages in 0.7 IS abstract?
# "def on_messages(...)":
# If it is abstract, wrapping it does nothing for subclasses that implement it.
# We must wrap the SUBCLASS methods or use a hook provided by framework.
# But AutoGen 0.7 does not seem to have a global hook system yet (callbacks are coming but maybe not stable).

# If BaseChatAgent.on_messages is abstract, then my instrumentation is USELESS for subclasses that override it (which is all of them).
# I need to check `BaseChatAgent.on_messages` implementation.
