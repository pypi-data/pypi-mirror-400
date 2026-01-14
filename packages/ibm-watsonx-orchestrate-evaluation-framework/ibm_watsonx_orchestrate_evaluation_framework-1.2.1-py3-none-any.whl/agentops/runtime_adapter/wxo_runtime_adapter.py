import json
import os
import time
from typing import Any, Dict, Generator, List, Mapping

import requests
import rich
import yaml

from agentops.runtime_adapter.runtime_adapter import RuntimeAdapter
from agentops.service_provider.watsonx_provider import WatsonXProvider
from agentops.type import (
    ContentType,
    ConversationalConfidenceThresholdScore,
    ConversationalSearch,
    ConversationalSearchCitations,
    ConversationalSearchResultMetadata,
    ConversationalSearchResults,
    ConversationSearchMetadata,
    Message,
    RuntimeResponse,
)
from agentops.utils.utils import is_saas_url
from agentops.wxo_client import WXOClient


def is_transfer_response(step_detail: Dict):
    # this is not very reliable
    if step_detail["type"] == "tool_response" and step_detail["name"].endswith(
        "_agent"
    ):
        return True
    return False


class WXORuntimeAdapter(RuntimeAdapter):
    def __init__(self, wxo_client):
        self.wxo_client = wxo_client
        self.enable_saas_mode = is_saas_url(wxo_client.service_url)

    def _runs_endpoint(self, user_input: Message, agent_name, thread_id=None):
        agent_id = self.get_agent_id(agent_name)
        payload = {"message": user_input.model_dump(), "agent_id": agent_id}
        if thread_id:
            payload["thread_id"] = thread_id

        if self.enable_saas_mode:
            # TO-DO: this is not validated after the v1 prefix change
            # need additional validation
            path = "/v1/orchestrate/runs"
        else:
            path = "v1/orchestrate/runs"

        response: requests.Response = self.wxo_client.post(payload, path)

        if int(response.status_code) == 200:
            result = response.json()
            return result["thread_id"]
        else:
            response.raise_for_status()

    def _stream_events(
        self, user_input: Message, agent_name: str, thread_id=None
    ) -> Generator[Dict, None, None]:
        agent_id = self.get_agent_id(agent_name)
        payload = {"message": user_input.model_dump(), "agent_id": agent_id}
        if thread_id:
            payload["thread_id"] = thread_id

        if self.enable_saas_mode:
            # TO-DO: this is not validated after the v1 prefix change
            # need additional validation
            path = "/v1/orchestrate/runs?stream=true"
        else:
            path = "v1/orchestrate/runs?stream=true"

        response: requests.Response = self.wxo_client.post(
            payload, path, stream=True
        )
        import json

        for chunk in self._parse_events(response):
            chunk = json.loads(chunk.strip())
            yield chunk

    def parse_conversational_search_response(
        self,
        conversational_search: Mapping[str, Any],
        metadata: ConversationSearchMetadata,
    ) -> ConversationalSearch:
        def parse_citations():
            citations = conversational_search["citations"]
            parsed_citations = []
            for citation in citations:
                c = ConversationalSearchCitations(
                    url=citation.get("url", ""),
                    body=citation.get("body", ""),
                    text=citation.get("text", ""),
                    title=citation.get("title", ""),
                    range_start=citation.get("range_start"),
                    range_end=citation.get("range_end"),
                    search_result_idx=citation.get("search_result_idx"),
                )
                parsed_citations.append(c)

            return parsed_citations

        def parsed_search_results():
            search_results = conversational_search["search_results"]
            parsed_search_results = []
            for result in search_results:
                result_metadata = result.get("result_metadata", {})
                result_metadata = ConversationalSearchResultMetadata(
                    score=result_metadata.get("score"),
                    document_retrieval_source=result_metadata.get(
                        "document_retrieval_source"
                    ),
                )
                c = ConversationalSearchResults(
                    url=result.get("url", ""),
                    body=result.get("body", ""),
                    title=result.get("title", ""),
                    result_metadata=result_metadata,
                )
                parsed_search_results.append(c)

            return parsed_search_results

        citations = parse_citations()
        retrieval_context = parsed_search_results()
        citations_title = conversational_search.get("citations_title", "")
        response_length_option = conversational_search.get(
            "response_length_option", ""
        )
        text = conversational_search.get("text", "")

        confidence_scores = ConversationalConfidenceThresholdScore(
            **conversational_search.get("confidence_scores")
        )
        response_type = conversational_search.get("response_type")
        # should always be conversational_search
        assert response_type == ContentType.conversational_search

        conversational_search = ConversationalSearch(
            metadata=metadata,
            response_type=response_type,
            text=text,
            citations=citations,
            search_results=retrieval_context,
            citations_title=citations_title,
            confidence_scores=confidence_scores,
            response_length_option=response_length_option,
        )

        return conversational_search

    def run(
        self,
        user_input: Message,
        context: dict,
        thread_id=None,
    ) -> RuntimeResponse:

        agent_name = context["agent_name"]
        call_tracker = context["call_tracker"]
        recover = False
        messages = list()
        conversational_search_data = []

        start_time = time.time()
        for chunk in self._stream_events(user_input, agent_name, thread_id):
            event = chunk.get("event", "")
            if _thread_id := chunk.get("data", {}).get("thread_id"):
                thread_id = _thread_id
                if delta := chunk.get("data", {}).get("delta"):
                    role = delta["role"]
                    if step_details := delta.get("step_details"):
                        if any(
                            is_transfer_response(step_detail)
                            for step_detail in step_details
                        ):
                            continue
                        for idx, step_detail in enumerate(step_details):
                            if step_detail["type"] == "tool_calls":
                                # in step details, we could have [tool_response, tool_call]
                                # in this case, we skip since we already capture the tool call
                                if idx == 1:
                                    continue

                                content_type = ContentType.tool_call
                                for tool in step_detail["tool_calls"]:
                                    # Only add "transfer_to_" calls here. Other tool calls are already
                                    # captured in the next block, including them here will cause duplication
                                    # if not tool["name"].startswith("transfer_to_"):
                                    #     continue
                                    tool_json = {"type": "tool_call"}
                                    tool_json.update(tool)
                                    content = json.dumps(tool_json)
                                    messages.append(
                                        Message(
                                            role=role,
                                            content=content,
                                            type=content_type,
                                            event=event,
                                        )
                                    )
                                    end_time = time.time()
                                    call_tracker.tool_call.append(
                                        end_time - start_time
                                    )
                                    start_time = end_time
                            elif step_detail["type"] == "tool_call":
                                # in step details, we could have [tool_response, tool_call]
                                # in this case, we skip since we already capture the tool call
                                if idx == 1:
                                    continue
                                content_type = ContentType.tool_call
                                content = json.dumps(step_detail)
                                messages.append(
                                    Message(
                                        role=role,
                                        content=content,
                                        type=content_type,
                                        event=event,
                                    )
                                )
                                end_time = time.time()
                                call_tracker.tool_call.append(
                                    end_time - start_time
                                )
                                start_time = end_time
                            elif step_detail["type"] == "tool_response":
                                content = json.dumps(step_detail)
                                content_type = ContentType.tool_response
                                messages.append(
                                    Message(
                                        role=role,
                                        content=content,
                                        type=content_type,
                                        event=event,
                                    )
                                )
                                end_time = time.time()
                                call_tracker.tool_response.append(
                                    end_time - start_time
                                )
                                start_time = end_time
                    elif content_field := delta.get("content"):
                        for val in content_field:
                            response_type = val["response_type"]
                            # TODO: is this ever hit? the event name is "message.created", and it seems the event should be "message.delta"
                            if (
                                response_type == ContentType.text
                                and chunk["event"] == "message_created"
                            ):
                                messages.append(
                                    Message(
                                        role=role,
                                        content=val["text"],
                                        type=ContentType.text,
                                    ),
                                    chunk=event,
                                )
                                end_time = time.time()
                                call_tracker.generic.append(
                                    end_time - start_time
                                )
                                start_time = end_time

                elif chunk["event"] == "message.created":
                    message = chunk.get("data", {}).get("message")

                    role = message.get("role")
                    # this is a behavior introduced in orchestrate adk 2.2.0
                    if not role:
                        continue
                    for content in message["content"]:
                        if (
                            content["response_type"]
                            == ContentType.conversational_search
                        ):
                            end_time = time.time()
                            call_tracker.generic.append(end_time - start_time)
                            start_time = end_time

                            """ This is under the assumption the flow is (tool call -> tool response -> response back to user).
                            In other words, the tool response is not fed back in to the agent.
                            We get the previous message and extract the `tool_call_id`.
                            
                            NOTE: The previous message is a tool call because how we parse the event stream.
                            NOTE: The conversational search response event does not have a 'tool call id' which can be used to associate with the 'conversational search response'.
                            """

                            last_message = json.loads(messages[-1].content)
                            tool_call_id = last_message.get(
                                "tool_call_id", None
                            )
                            assert tool_call_id is not None
                            conversational_search_metadata = (
                                ConversationSearchMetadata(
                                    tool_call_id=tool_call_id
                                )
                            )
                            conversational_search = (
                                self.parse_conversational_search_response(
                                    conversational_search=content,
                                    metadata=conversational_search_metadata,
                                )
                            )
                            conversational_search_data.append(
                                conversational_search
                            )
                            messages.append(
                                Message(
                                    role=role,
                                    content=content["text"],
                                    type=ContentType.conversational_search,
                                    conversational_search_metadata=conversational_search_metadata,
                                    event=event,
                                )
                            )
                        if content["response_type"] == ContentType.text:
                            messages.append(
                                Message(
                                    role=role,
                                    content=content["text"],
                                    type=ContentType.text,
                                    event=chunk["event"],
                                )
                            )
                            end_time = time.time()
                            call_tracker.generic.append(end_time - start_time)
                            start_time = end_time
            else:
                # Exit the loop if we lose the thread_id
                recover = True
                break

        if recover and (thread_id is not None):
            rich.print(
                "🔬 [bold][magenta]INFO:[/magenta][/bold]",
                f"Attempting to recover messages from thread_id {thread_id}",
            )
            # If we lose the thread_id, we need to wait for a bit to allow the message to come through
            # before attempting to recover the messages.
            time.sleep(10)
            messages = self.recover_messages(thread_id)
            rich.print(
                "🔬 [bold][magenta]INFO:[/magenta][/bold]",
                f"Recovered {len(messages)} messages from thread_id {thread_id}",
            )

        return RuntimeResponse(
            messages=messages,
            thread_id=thread_id,
            context={"conversational_search_data": conversational_search_data},
        )

    def _parse_events(
        self, stream: Generator[bytes, None, None]
    ) -> Generator[bytes, None, None]:
        data = b""
        for chunk in stream:
            for line in chunk.splitlines(True):
                data += line
                if data.endswith((b"\r\r", b"\n\n", b"\r\n\r\n", b"\n")):
                    yield data
                    data = b""
        if data:
            yield data

    def recover_messages(self, thread_id: str) -> List[Message]:
        messages = self.get_messages(thread_id)
        return self._get_messages_after_last_user(messages)

    def get_messages(self, thread_id) -> List[Message]:
        if self.enable_saas_mode:
            path = f"v1/orchestrate/threads/{thread_id}/messages"
        else:
            path = f"v1/threads/{thread_id}/messages"
        response = self.wxo_client.get(path)
        if response.status_code == 200:
            result = response.json()

        else:
            response.raise_for_status()

        messages = []
        for entry in result:
            tool_call_id = None
            if step_history := entry.get("step_history"):
                for step_message in step_history:
                    role = step_message["role"]
                    if step_details := step_message.get("step_details"):
                        for step_detail in step_details:
                            if step_detail["type"] == "tool_calls":
                                content_type = ContentType.tool_call
                                for tool in step_detail["tool_calls"]:
                                    tool_json = {"type": "tool_call"}
                                    tool_json.update(tool)
                                    content = json.dumps(tool_json)
                                    # TO-DO: review do we even need the get messages for retry loop anymore?
                                    if msg_content := entry.get("content"):
                                        if (
                                            msg_content[0].get("response_type")
                                            == "conversational_search"
                                        ):
                                            continue
                                    messages.append(
                                        Message(
                                            role=role,
                                            content=content,
                                            type=content_type,
                                        )
                                    )
                            elif step_detail["type"] == "tool_call":
                                tool_call_id = step_detail["tool_call_id"]
                                content_type = ContentType.tool_call
                                content = json.dumps(step_detail)
                                messages.append(
                                    Message(
                                        role=role,
                                        content=content,
                                        type=content_type,
                                    )
                                )
                            else:
                                content = json.dumps(step_detail)
                                content_type = ContentType.tool_response
                                messages.append(
                                    Message(
                                        role=role,
                                        content=content,
                                        type=content_type,
                                    )
                                )
            if content_field := entry.get("content"):
                role = entry["role"]
                for val in content_field:
                    if val["response_type"] == ContentType.text:
                        messages.append(
                            Message(
                                role=role,
                                content=val["text"],
                                type=ContentType.text,
                            )
                        )
                    if (
                        val["response_type"]
                        == ContentType.conversational_search
                    ):
                        conversational_search_metadata = (
                            ConversationSearchMetadata(
                                tool_call_id=tool_call_id
                            )
                        )
                        messages.append(
                            Message(
                                role=role,
                                content=val["text"],
                                type=ContentType.text,
                                conversational_search_metadata=conversational_search_metadata,
                            )
                        )

        return messages

    @staticmethod
    def _get_messages_after_last_user(messages: List[Message]) -> List[Message]:
        for i in range(len(messages) - 1, -1, -1):
            if messages[i].role == "user":
                return messages[i + 1 :]
        return messages

    def get_agent_id(self, agent_name: str):
        if self.enable_saas_mode:
            path = "v1/orchestrate/agents"
        else:
            path = "v1/orchestrate/agents"

        response = self.wxo_client.get(path)

        if response.status_code == 200:
            result = response.json()
            for agent in result:
                if agent.get("name", "") == agent_name:
                    return agent.get("id")

            raise Exception(f"Agent with name {agent_name} not found.")

        else:
            response.raise_for_status()

    def get_agent_name_from_thread_id(self, thread_id: str) -> str:
        if self.enable_saas_mode:
            thread_path = f"v1/orchestrate/threads/{thread_id}"
            agents_path = "v1/orchestrate/agents"
        else:
            thread_path = f"v1/threads/{thread_id}"
            agents_path = "v1/orchestrate/agents"

        thread_response = self.wxo_client.get(thread_path)
        thread_response.raise_for_status()
        thread_data = thread_response.json()
        agent_id = thread_data.get("agent_id", "")

        agents_response = self.wxo_client.get(agents_path)
        agents_response.raise_for_status()
        agents_list = agents_response.json()
        for agent in agents_list:
            if agent.get("id", "") == agent_id:
                return agent.get("name")

        return None


if __name__ == "__main__":
    wai_client = WatsonXProvider(model_id="meta-llama/llama-3-3-70b-instruct")
    auth_config_path = (
        f"{os.path.expanduser('~')}/.cache/orchestrate/credentials.yaml"
    )
    with open(auth_config_path, "r") as f:
        auth_config = yaml.safe_load(f)

    tenant_name = "local"
    token = auth_config["auth"][tenant_name]["wxo_mcsp_token"]

    wxo_client = WXOClient(service_url="http://localhost:4321", api_key=token)
    inference_backend = WXORuntimeAdapter(wxo_client=wxo_client)
    resp = wxo_client.get("v1/orchestrate/agents")
    resp = resp.json()

    for agent in resp:
        print(agent["name"], agent["display_name"])
