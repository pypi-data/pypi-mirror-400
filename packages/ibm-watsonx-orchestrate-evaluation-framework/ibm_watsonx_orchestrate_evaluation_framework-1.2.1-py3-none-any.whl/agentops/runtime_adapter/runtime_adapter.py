from abc import abstractmethod

from agentops.type import CallTracker, Message, RuntimeResponse


class RuntimeAdapter:

    @abstractmethod
    def run(
        self,
        user_message: Message,
        context: dict,
        thread_id=None,
    ) -> RuntimeResponse:
        pass
