from typing import Optional

from pydantic import BaseModel, Field

from agentops.type import ContentType, Message


class ParsedMessages(BaseModel):
    """
    A parsed history of messages.
    """

    messages: list[Message] = Field(description="The list of messages")

    @property
    def user_input(self) -> Optional[str]:
        """Find the original user message."""
        for message in self.messages:
            if message.role == "user" and message.type == ContentType.text:
                return str(message.content)
        return None

    @property
    def agent_response(self) -> Optional[str]:
        """Find the most recent assistant message."""
        messages_in_reverse = reversed(self.messages)
        for message in messages_in_reverse:
            if message.role == "assistant" and message.type == ContentType.text:
                return str(message.content)
        return None
