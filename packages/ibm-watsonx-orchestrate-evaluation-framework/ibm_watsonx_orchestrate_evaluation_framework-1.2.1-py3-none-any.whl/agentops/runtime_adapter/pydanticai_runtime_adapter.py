from pydantic_ai import Agent

from agentops.runtime_adapter.runtime_adapter import RuntimeAdapter
from agentops.type import Message, RuntimeResponse


class PydanticAIRuntimeAdapter(RuntimeAdapter):
    def __init__(self, agent: Agent):
        self.agent = agent

    def run(
        self,
        user_message: Message,
        context: dict,
        thread_id=None,
    ) -> RuntimeResponse:
        chat_history = context.get("chat_history")
        output = self.agent.run_sync(
            user_message.content, message_history=chat_history
        )
        context["chat_history"] = output.all_messages()
        return RuntimeResponse(
            context=context,
            messages=[Message(role="assistant", content=output.output)],
        )
