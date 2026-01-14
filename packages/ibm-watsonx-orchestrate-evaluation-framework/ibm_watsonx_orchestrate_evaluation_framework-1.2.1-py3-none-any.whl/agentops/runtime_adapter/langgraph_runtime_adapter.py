from langgraph.graph.state import CompiledStateGraph

from agentops.runtime_adapter.runtime_adapter import RuntimeAdapter
from agentops.type import Message, RuntimeResponse


class LanggraphRuntimeAdapter(RuntimeAdapter):
    def __init__(self, agent: CompiledStateGraph):
        self.agent = agent

    def run(
        self,
        user_message: Message,
        context: dict,
        thread_id=None,
    ) -> RuntimeResponse:

        message_json = user_message.model_dump()
        messages = {"messages": [message_json]}
        response = self.agent.invoke(
            messages, config={"configurable": {"thread_id": thread_id}}
        )
        message = Message(
            role="assistant", content=response["messages"][-1].content
        )
        return RuntimeResponse(messages=[message], thread_id=thread_id)
