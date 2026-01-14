from typing import Any, Dict, List, Optional, Sequence

from portkey_ai import Portkey

from agentops.service_provider.provider import Provider
from agentops.type import ChatCompletions, Choice, Message


class PortkeyProvider(Provider):
    """Provider that delegates to the Portkey AI client"""

    def __init__(
        self,
        vendor: str,
        api_key: Optional[str] = None,
        model_id: Optional[str] = None,
        embedding_model: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 60,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__()

        self.vendor = vendor
        self.api_key = api_key
        self.model_id = model_id
        self.embedding_model = embedding_model
        self.base_url = base_url
        self.timeout = timeout * 1000  # convert to ms
        self.system_prompt = system_prompt

        self._client = None
        if self.api_key is not None:
            client_kwargs = {
                "provider": self.vendor,
                "Authorization": self.api_key,
            }
            if self.base_url:
                client_kwargs["base_url"] = base_url
            if self.timeout:
                client_kwargs["request_timeout"] = self.timeout

            client_kwargs.update(kwargs)
            self._client = Portkey(**client_kwargs)

    def _require_client(self) -> None:
        if self._client is None:
            raise ImportError(
                "portkey_ai client is not available. Install 'portkey_ai' and provide a valid api_key."
            )

    def chat(
        self,
        messages: Sequence[Dict[str, str]],
        params: Optional[Dict[str, Any]] = None,
    ) -> ChatCompletions:
        self._require_client()

        kwargs = {}
        if params:
            kwargs.update(params)

        resp = self._client.chat.completions.create(
            messages=messages, model=self.model_id, **kwargs
        )

        return ChatCompletions(
            choices=[
                Choice(
                    message=Message(
                        role=choice.message.role, content=choice.message.content
                    ),
                    finish_reason=choice.finish_reason,
                )
                for choice in resp.choices
            ],
            id=resp.id,
            model=resp.model,
        )

    def encode(self, sentences: List[str]) -> List[list]:
        raise NotImplementedError(
            "encode is not implemented for PortkeyProvider"
        )


if __name__ == "__main__":
    import os

    from agentops.service_provider import get_provider

    # Direct PortkeyProvider usage
    if os.environ.get("OPENAI_API_KEY") is not None:
        provider = PortkeyProvider(
            vendor="openai",
            model_id="gpt-4o-mini",
            api_key=os.environ.get("OPENAI_API_KEY"),
            system_prompt="Respond in Spanish only",
        )
        response = provider.query("Hello, how are you?")
        print(response.choices[0].message.content)
        print(40 * "#")

    # Using get_provider factory method
    prompt = "Write haiku"

    # OpenAI provider
    if os.environ.get("OPENAI_API_KEY") is not None:
        provider = get_provider(
            model_id="gpt-4o-mini",
            vendor="openai",
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        response = provider.query(prompt)
        print(response.choices[0].message.content)
        print(40 * "#")

    # Azure OpenAI
    if os.environ.get("AZURE_OPENAI_API_KEY") is not None:
        provider = get_provider(
            model_id="gpt-4",
            vendor="azure-openai",
            azure_model_name="gpt-4",
            azure_deployment_id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            azure_resource_name=os.getenv("AZURE_OPENAI_RESOURCE_NAME"),
            azure_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            api_key=f"Bearer {os.getenv('AZURE_OPENAI_API_KEY')}",
        )
        response = provider.query(prompt)
        print(response.choices[0].message.content)
