import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from claude_agent_sdk import ClaudeSDKClient
from claude_agent_sdk.types import ClaudeAgentOptions
from opentelemetry.context import attach as attach_otel_context
from opentelemetry.context import get_current as get_otel_context

from agentops.runtime_adapter.runtime_adapter import RuntimeAdapter
from agentops.type import (
    ContentType,
    Function,
    Message,
    RuntimeResponse,
    ToolCall,
)


class ClaudeRuntimeAdapter(RuntimeAdapter):
    def __init__(self, options: ClaudeAgentOptions):
        self.options = options
        self.executor = ThreadPoolExecutor(max_workers=5)
        # TO-DO: unbounded cache for simplicity. we could convert to use the LRUCache
        # just need to make sure we do the client.disconnect and event_loop.close when evit from the cache
        self.cache = {}
        self.connected_cached = set()
        self.event_loop_cache = {}
        self.lock = Lock()

    def _get_sdk_client(self, thread_id):
        if thread_id not in self.cache:
            with self.lock:
                if thread_id not in self.cache:
                    self.cache[thread_id] = ClaudeSDKClient(
                        options=self.options
                    )
        return self.cache[thread_id]

    def _parse_claude_messages(self, claude_messages: list) -> list[Message]:
        """Convert Claude SDK messages to agentops Message format"""
        parsed_messages = []

        for msg in claude_messages:
            msg_type = type(msg).__name__

            # Skip SystemMessage (init messages)
            if msg_type == "SystemMessage":
                continue

            # Parse AssistantMessage
            elif msg_type == "AssistantMessage":
                # Extract text content and tool calls
                text_content = []
                tool_calls = []

                if hasattr(msg, "content") and msg.content:
                    for block in msg.content:
                        block_type = type(block).__name__

                        # Handle text blocks
                        if block_type == "TextBlock" and hasattr(block, "text"):
                            text_content.append(block.text)

                        # Handle tool use blocks (ToolUseBlock)
                        elif block_type == "ToolUseBlock":
                            tool_call = ToolCall(
                                id=(
                                    block.id
                                    if hasattr(block, "id")
                                    else f"call_{len(tool_calls)}"
                                ),
                                function=Function(
                                    name=(
                                        block.name
                                        if hasattr(block, "name")
                                        else "unknown"
                                    ),
                                    arguments=(
                                        json.dumps(block.input)
                                        if hasattr(block, "input")
                                        else "{}"
                                    ),
                                ),
                                type="function",
                            )
                            tool_calls.append(tool_call)

                # Create separate messages for text and tool calls
                # If there's text content, create a text message
                if text_content:
                    content = "\n".join(text_content)
                    message = Message(
                        role="assistant", content=content, type=ContentType.text
                    )
                    parsed_messages.append(message)

                # If there are tool calls, create a tool_call message
                if tool_calls:
                    message = Message(
                        role="assistant",
                        content="",
                        type=ContentType.tool_call,
                        tool_calls=tool_calls,
                    )
                    parsed_messages.append(message)

            # Parse UserMessage (tool results)
            elif msg_type == "UserMessage":
                if hasattr(msg, "content") and msg.content:
                    for block in msg.content:
                        block_type = type(block).__name__

                        # Handle tool result blocks
                        if block_type == "ToolResultBlock":
                            # Extract text from tool result content
                            result_text = ""
                            if hasattr(block, "content") and block.content:
                                for content_item in block.content:
                                    if (
                                        isinstance(content_item, dict)
                                        and content_item.get("type") == "text"
                                    ):
                                        result_text = content_item.get(
                                            "text", ""
                                        )
                                        break

                            message = Message(
                                role="tool",
                                content=result_text,
                                type=ContentType.tool_response,
                                tool_call_id=(
                                    block.tool_use_id
                                    if hasattr(block, "tool_use_id")
                                    else None
                                ),
                            )
                            parsed_messages.append(message)

            # Parse ResultMessage (final result with cost info) - skip this as it's metadata
            elif msg_type == "ResultMessage":
                # ResultMessage contains metadata like cost, we can skip it
                # or extract the final result if needed
                pass

        return parsed_messages

    async def _run(self, user_message: Message, context: dict, thread_id=None):
        client = self._get_sdk_client(thread_id=thread_id)
        if thread_id not in self.connected_cached:
            with self.lock:
                if thread_id not in self.connected_cached:
                    await client.connect()
                    self.connected_cached.add(thread_id)
        await client.query(prompt=user_message.content, session_id=thread_id)
        messages = []
        async for message in client.receive_response():
            messages.append(message)
        # await client.disconnect()
        return messages

    def _run_with_loop(
        self,
        user_message: Message,
        context: dict,
        thread_id=None,
        otel_ctx=None,
    ):
        # Attach OTel context from caller thread to propagate session.id
        if otel_ctx is not None:
            attach_otel_context(otel_ctx)

        # if thread_id not in self.event_loop_cache:
        with self.lock:
            if thread_id not in self.event_loop_cache:
                loop = asyncio.new_event_loop()
                self.event_loop_cache[thread_id] = loop
            loop = self.event_loop_cache[thread_id]

        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            self._run(user_message, context, thread_id)
        )
        return result

    def run(
        self, user_message: Message, context: dict, thread_id=None
    ) -> RuntimeResponse:
        # Capture OTel context before submitting to
        # thread pool
        otel_ctx = get_otel_context()
        future = self.executor.submit(
            self._run_with_loop, user_message, context, thread_id, otel_ctx
        )
        claude_messages = future.result()
        parsed_messages = self._parse_claude_messages(claude_messages)
        return RuntimeResponse(
            messages=parsed_messages, thread_id=thread_id, context=context
        )
