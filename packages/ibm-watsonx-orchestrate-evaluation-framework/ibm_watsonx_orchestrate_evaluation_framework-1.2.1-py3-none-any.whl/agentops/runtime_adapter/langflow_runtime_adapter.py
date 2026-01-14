import os
from typing import Optional

import requests

from agentops.runtime_adapter.runtime_adapter import RuntimeAdapter
from agentops.type import Message, RuntimeResponse


class LangflowRuntimeAdapter(RuntimeAdapter):
    def __init__(self, endpoint_url: str = None, api_key: str = None):
        # Allow overriding endpoint and API key, but default to values from example if not provided
        self.endpoint_url = endpoint_url
        self.api_key = api_key or os.environ.get("LANGFLOW_API_KEY")

    def run(
        self,
        user_message: Message,
        context: dict,
        thread_id=None,
        system_prompt: str = None,
    ) -> RuntimeResponse:
        # Build Langflow request payload as in langflow_example.py
        payload = {
            "output_type": "chat",
            "input_type": "chat",
            "input_value": user_message.content,
        }
        if system_prompt is not None:
            payload["tweaks"] = {"system_prompt": system_prompt}
        payload["session_id"] = thread_id
        headers = {"x-api-key": self.api_key}

        response = requests.request(
            "POST", self.endpoint_url, json=payload, headers=headers
        ).json()
        # langflow_example.py: text_key = resp["outputs"][0]["outputs"][0]['results']["message"]["text_key"]
        text_key = response["outputs"][0]["outputs"][0]["results"]["message"][
            "text_key"
        ]
        agent_content = response["outputs"][0]["outputs"][0]["results"][
            "message"
        ][text_key]
        session_id = response["session_id"]

        return RuntimeResponse(
            messages=[Message(role="assistant", content=agent_content)],
            thread_id=session_id,
        )
