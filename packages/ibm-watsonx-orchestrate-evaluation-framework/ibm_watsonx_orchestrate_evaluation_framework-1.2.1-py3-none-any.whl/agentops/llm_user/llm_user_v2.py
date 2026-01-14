from typing import List

from agentops.llm_user.base_user import BaseUserSimulator
from agentops.prompt.template_render import UserTemplateRenderer
from agentops.service_provider.watsonx_provider import Provider
from agentops.type import ContentType, Message


class LLMUserV2(BaseUserSimulator):
    # new LLM user that works with chat completion providers like portkey
    def __init__(
        self,
        llm_client: Provider,
        user_prompt_path: str,
    ):
        self.llm_client = llm_client
        self.user_prompt_path = user_prompt_path
        self.prompt_template = UserTemplateRenderer(
            template_path=user_prompt_path
        )

    def _get_system_prompt(
        self, user_story: str, user_response_style: List[str] = None
    ) -> Message:
        # Get the user system prompt
        prompt_messages = self.prompt_template.render(
            user_story=user_story,
            user_response_style=user_response_style,
        )
        return Message(**prompt_messages[0], type=ContentType.text)

    def _get_message_dicts(self, messages: List[Message]) -> List[dict]:
        # Convert messages to dictionary format for the llm client
        return [message.model_dump() for message in messages]

    def _filter_conversation_history(
        self, conversation_history: List[Message]
    ) -> List[Message]:
        # Filter out the agent system prompt
        return [
            message
            for message in conversation_history
            if message.role != "system"
        ]

    def flip_message_roles(self, messages: List[Message]) -> List[Message]:
        # We flip the roles of messages in conversation history to basically prompt the
        # user simulator with the assistant message as the user input message
        # This helps to get the llm to respond as a natural user with the given story.
        new_messages = []
        for message in messages:
            if message.role == "user":
                new_messages.append(
                    Message(
                        role="assistant",
                        content=message.content,
                        type=ContentType.text,
                    )
                )
            else:
                new_messages.append(
                    Message(
                        role="user",
                        content=message.content,
                        type=ContentType.text,
                    )
                )
        return new_messages

    def generate_user_input(
        self,
        user_story: str,
        conversation_history: List[Message],
        user_response_style: List[str] = None,
        starting_user_input: Message = None,
        **kwargs,
    ) -> Message:
        # Get the user system prompt
        system_prompt = self._get_system_prompt(user_story, user_response_style)

        conversation_history = self._filter_conversation_history(
            conversation_history
        )

        ## Adding dummy message if not provided from the simulation side.
        if len(conversation_history) == 0:
            conversation_history.append(
                Message(
                    role="assistant",
                    content="Hi! How can I help you today?",
                    type=ContentType.text,
                )
            )

        conversation_history = self.flip_message_roles(conversation_history)

        # build the conversation history with the system prompt
        messages = [system_prompt] + conversation_history

        if starting_user_input is not None:
            # If starting user input is provided, return it as is for the initial turn
            return starting_user_input
        else:

            # Get response from LLM for simulation
            response = self.llm_client.chat(
                messages=self._get_message_dicts(messages)
            )
            response_message = Message(
                role="user",
                content=response.choices[0].message.content,
                type=ContentType.text,
            )

            return response_message
