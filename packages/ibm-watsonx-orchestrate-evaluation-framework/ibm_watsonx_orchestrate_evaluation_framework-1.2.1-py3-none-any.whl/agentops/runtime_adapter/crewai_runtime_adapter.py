from crewai import Agent

from agentops.runtime_adapter.runtime_adapter import RuntimeAdapter
from agentops.type import Message, RuntimeResponse


class CrewAIRuntimeAdapter(RuntimeAdapter):
    def __init__(self, agent: Agent):
        self.agent = agent

    def run(
        self,
        user_message: Message,
        context: dict,
        thread_id=None,
    ) -> RuntimeResponse:

        user_query = user_message.content
        result = self.agent.kickoff(inputs={"user_query": user_query})

        assistant_text = str(result)
        message = Message(role="assistant", content=assistant_text)
        return RuntimeResponse(messages=[message], thread_id=thread_id)
