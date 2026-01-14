from abc import ABC, abstractmethod
from typing import List

from agentops.type import Message


class BaseUserSimulator(ABC):
    """Abstract base class for user simulators."""

    @abstractmethod
    def generate_user_input(
        self, user_story: str, conversation_history: List[Message], **kwargs
    ) -> Message:
        """
        Generate user input based on the user story and conversation history.

        Args:
            user_story: The user's story or goal
            conversation_history: List of previous messages in the conversation
            **kwargs: Additional parameters specific to the simulator implementation

        Returns:
            Message: The generated user input message
        """
        pass
