from typing import List, TypeVar

from agentops.llm_user.base_user import BaseUserSimulator
from agentops.prompt.template_render import JinjaTemplateRenderer
from agentops.service_provider.watsonx_provider import Provider
from agentops.type import ContentType, Message

T = TypeVar("T", bound=JinjaTemplateRenderer)


class LLMUser(BaseUserSimulator):
    # default LLM user that uses the llama template
    def __init__(
        self,
        wai_client: Provider,
        template: T,
        user_response_style: List[str] | None = None,
    ):
        self.wai_client = wai_client
        self.prompt_template = template
        self.user_response_style = (
            [] if user_response_style is None else user_response_style
        )

    def generate_user_input(
        self,
        user_story,
        conversation_history: List[Message],
        attack_instructions: str | None = None,
    ) -> Message:
        # the tool response is already summarized, we don't need that to take over the chat history context window
        prompt_input = self.prompt_template.render(
            conversation_history=[
                entry
                for entry in conversation_history
                if entry.type != ContentType.tool_response
            ],
            user_story=user_story,
            user_response_style=self.user_response_style,
            attack_instructions=attack_instructions,
        )
        response = self.wai_client.chat(prompt_input)
        user_input = Message(
            role="user",
            content=response.choices[0].message.content.strip(),
            type=ContentType.text,
        )
        return user_input
