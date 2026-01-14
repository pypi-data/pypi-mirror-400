import hashlib
import json
import logging
import uuid
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from openinference.instrumentation import using_session

from agentops.automatic_eval_generation.tool_seq_generator import (
    generate_eval_data_from_stories,
)
from agentops.automatic_eval_generation.workflow_converter import (
    WorkflowConverter,
)
from agentops.llm_user.llm_user_v2 import LLMUserV2 as LLMUser
from agentops.otel_parser import otel_parser as parser
from agentops.runtime_adapter.runtime_adapter import RuntimeAdapter
from agentops.runtime_adapter.wxo_runtime_adapter import WXORuntimeAdapter
from agentops.service_provider.provider import Provider
from agentops.type import CallTracker, ContentType, Message
from agentops.utils.langfuse_tool_success_filter import (
    LangfuseToolSuccessFilter,
)

logger = logging.getLogger(__name__)


class AutomaticEvalDataGenerator:
    """
    Automatic evaluation data generator for agent testing.

    This class orchestrates the complete workflow:
    1. Generate tool sequences from user stories
    2. Run user-agent simulations
    3. Filter successful sessions
    4. Convert to workflow format

    Works with any RuntimeAdapter implementation (LangGraph, Claude, etc.)
    """

    def __init__(
        self,
        runtime_adapted_agent: RuntimeAdapter,
        user_client: Provider,
        tool_sequence_client: Provider,
        openapi_spec: dict,
        user_prompt_path: Path = Path(__file__).parent
        / "../prompt"
        / "universal_user_template.jinja2",
    ):
        """
        Initialize the evaluation data generator.

        Args:
            runtime_adapted_agent: Agent to evaluate (any RuntimeAdapter)
            user_client: LLM client for user simulator (Provider instance)
            tool_sequence_client: LLM client for generating tool sequences (Provider instance)
            openapi_spec: OpenAPI specification dict
            user_prompt_path: Path to user simulator prompt template
        """
        self.runtime_adapted_agent = runtime_adapted_agent
        self.openapi_spec = openapi_spec
        self.user_prompt_path = user_prompt_path
        self.tool_sequence_client = tool_sequence_client

        # Parse OpenAPI spec to get tool information
        from .tool_seq_generator import (
            format_tools_for_prompt,
            parse_openapi_spec,
        )

        self.tools = parse_openapi_spec(openapi_spec)
        self.tool_spec = format_tools_for_prompt(self.tools)

        # Initialize user simulator
        self.user_agent = LLMUser(
            llm_client=user_client,
            user_prompt_path=user_prompt_path,
        )

        # Initialize trace filter
        self.trace_filter = LangfuseToolSuccessFilter()

    def extract_actual_tool_calls_from_trace(
        self, session_id: str
    ) -> List[Dict[str, Any]]:
        """
        Extract actual tool calls with resolved arguments and responses from Langfuse trace.

        This extracts the REAL tool calls that the agent made during execution,
        with all placeholders naturally resolved through agent execution, plus their responses.

        Args:
            session_id: Langfuse session ID

        Returns:
            List of tool calls with tool_name, resolved arguments, response, and call_id
        """

        try:
            # Parse the session to get structured messages
            messages = parser.poll_messages(session_id)

            logger.info(
                f"Parsing trace for session {session_id}, found {len(messages)} messages"
            )

            tool_calls = []
            tool_responses = {}  # Map tool_call_id -> response content

            # First pass: Extract tool responses and map them by tool_call_id
            for i, msg in enumerate(messages):
                if (
                    msg.type == ContentType.tool_response
                    and hasattr(msg, "tool_call_id")
                    and msg.tool_call_id
                ):
                    tool_responses[msg.tool_call_id] = msg.content
                    logger.debug(
                        f"  Found tool response for {msg.tool_call_id}: {str(msg.content)[:100] if msg.content else 'empty'}"
                    )

            # Second pass: Extract tool calls from assistant messages and match with responses
            for i, msg in enumerate(messages):
                logger.debug(
                    f"Message {i}: role={msg.role}, type={msg.type}, tool_calls={msg.tool_calls}"
                )

                # Check assistant messages with tool_calls
                if msg.role == "assistant" and msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        # Parse the arguments JSON string
                        try:
                            arguments = json.loads(tool_call.function.arguments)
                        except json.JSONDecodeError:
                            logger.warning(
                                f"Failed to parse arguments for tool {tool_call.function.name}"
                            )
                            arguments = {}

                        # Get the response for this tool call
                        response = tool_responses.get(tool_call.id, None)

                        tool_calls.append(
                            {
                                "tool_name": tool_call.function.name,
                                "arguments": arguments,
                                "response": response,
                                "call_id": tool_call.id,
                            }
                        )
                        logger.debug(
                            f"  Extracted tool call: {tool_call.function.name} with args {arguments} and response available: {response is not None}"
                        )

            if tool_calls:
                logger.debug(
                    f"✓ Extracted {len(tool_calls)} actual tool calls from trace {session_id}"
                )
            else:
                logger.warning(f"⚠ No tool calls found in trace {session_id}")
                logger.warning(
                    f"  Message roles found: {[msg.role for msg in messages]}"
                )
                logger.warning(
                    f"  Messages with tool_calls: {sum(1 for msg in messages if msg.tool_calls)}"
                )

            return tool_calls

        except Exception as e:
            logger.error(
                f"❌ Failed to extract tool calls from trace {session_id}: {e}"
            )
            return []

    def _make_hashable(self, tool_call: Dict[str, Any]) -> str:
        return hashlib.sha256(
            json.dumps(tool_call, sort_keys=True).encode()
        ).hexdigest()

    def deduplicate_tool_calls(
        self, tool_calls: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        unique_tool_call_indices = []
        seen_hashes = set()
        for i, tool_call in enumerate(tool_calls):
            ## keep only tool name and args
            tool_call = {
                "tool_name": tool_call["tool_name"],
                "arguments": tool_call["arguments"],
            }
            hashable = self._make_hashable(tool_call)
            if hashable not in seen_hashes:
                seen_hashes.add(hashable)
                unique_tool_call_indices.append(i)

        return [tool_calls[i] for i in unique_tool_call_indices]

    def filter_tools_based_on_spec(
        self, tool_calls: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Filter tools based on the OpenAPI specification.
        """
        spec_tool_names = [tool["name"] for tool in self.tools]
        return [
            tool for tool in tool_calls if tool["tool_name"] in spec_tool_names
        ]

    def generate_eval_data(
        self,
        user_stories_df: pd.DataFrame,
        max_turns: int,
        agent_name: str = None,
    ) -> Dict[str, Any]:
        """
        Generate evaluation data from user stories.

        The workflow:
        1. Generate tool sequences with $placeholders from user stories
        2. Run agent simulations (agent naturally resolves dependencies)
        3. Extract ACTUAL tool calls from Langfuse traces (slot filling complete!)
        4. Convert to workflow format with resolved values

        Args:
            user_stories_df: DataFrame with columns: task_id, user_story
            max_turns: Maximum conversation turns per evaluation
            agent_name: Name of the agent being evaluated

        Returns:
            Dictionary mapping session_id to converted workflow format:
            {
                session_id: {
                    "agent": agent_name,
                    "story": user_story,
                    "starting_sentence": starting_sentence,
                    "goals": {...},
                    "goal_details": [...]  # With RESOLVED arguments from traces
                }
            }
        """
        # Step 1: Generate evaluation data (tool sequences and starting sentences) from user stories
        logger.info("Generating evaluation data from user stories...")
        eval_data = generate_eval_data_from_stories(
            user_stories_df, self.openapi_spec, self.tool_sequence_client
        )

        # Step 2: Prepare evaluation data
        logger.info(f"Preparing {len(eval_data)} evaluations...")
        tool_sequences = []
        task_id_session_id_map = {}

        for task_id, data in eval_data.items():
            tool_sequences.append(data["tool_sequence"])
            session_id = str(uuid.uuid4())
            task_id_session_id_map[session_id] = task_id

        # Step 3: Run evaluations
        logger.info(f"Running evaluations with max {max_turns} turns each...")
        session_ids_map = self.run_eval(
            tool_sequences,
            list(task_id_session_id_map.keys()),
            max_turns,
            agent_name,
        )

        # Step 4: Filter successful sessions
        logger.info("Filtering successful sessions via Langfuse traces...")
        logger.info(f"session_ids: {list(session_ids_map.keys())}")
        filtered_session_ids = self.trace_filter.filter_sessions(
            list(session_ids_map.keys())
        )
        logger.info(
            f"Successfully completed: {len(filtered_session_ids)}"
            f"/{len(list(session_ids_map.keys()))} sessions"
        )

        # Step 5: Convert to workflow format using LLM
        logger.info("Converting to workflow format using LLM...")
        converted_data_dict = {}

        for session_id in filtered_session_ids:
            task_id = task_id_session_id_map[session_ids_map[session_id]]

            # Extract ACTUAL tool calls from the trace (slot filling happens naturally)
            actual_tool_calls = self.extract_actual_tool_calls_from_trace(
                session_id
            )

            ## deduplicate actual tool calls based on tool name and args
            actual_tool_calls = self.deduplicate_tool_calls(actual_tool_calls)

            ## filter tools based on the OpenAPI specification
            actual_tool_calls = self.filter_tools_based_on_spec(
                actual_tool_calls
            )

            # If extraction fails or no tool calls found, fall back to generated sequence
            if not actual_tool_calls:
                logger.warning(
                    f"No actual tool calls extracted for {session_id}, "
                    f"using generated sequence with placeholders"
                )
                actual_tool_calls = eval_data[task_id]["tool_sequence"]
            else:
                logger.info(
                    f"Using {len(actual_tool_calls)} actual tool calls "
                    f"(resolved) for session {session_id}"
                )

            # Convert to workflow format with syntactic approach
            converter = WorkflowConverter()
            converted_data_dict[session_id] = (
                converter.convert_tool_calls_to_workflow(
                    tool_calls=actual_tool_calls,
                    agent=agent_name,
                    story=eval_data[task_id]["user_story"],
                    starting_sentence=eval_data[task_id]["starting_sentence"],
                )
            )

        logger.info(f"Generated {len(converted_data_dict)} evaluation cases")
        return converted_data_dict

    def run_eval_for_instance(
        self,
        user_story: str,
        max_turns: int,
        session_id: str = None,
        agent_name: str = None,
    ):
        """
        Run a single evaluation instance (user-agent conversation).

        Args:
            user_story: The user story/goal for the conversation
            max_turns: Maximum number of conversation turns
            session_id: Optional session ID for tracking
        """
        conversation_history = []

        for _ in range(max_turns):
            # Start conversation with agent greeting
            if len(conversation_history) == 0:
                conversation_history.append(
                    Message(
                        role="assistant",
                        content="Hi! How can I help you today?",
                        type=ContentType.text,
                    )
                )

            # Generate user input
            user_response = self.user_agent.generate_user_input(
                user_story=user_story,
                conversation_history=conversation_history,
                user_response_style=[],
            )
            conversation_history.append(user_response)

            logger.debug(f"User: {user_response.content}")

            # Check for stop signal
            if "###STOP###" in user_response.content:
                break

            # Get agent response
            with using_session(session_id) as session:
                agent_response = self.runtime_adapted_agent.run(
                    user_response,
                    {"agent_name": agent_name, "call_tracker": CallTracker()},
                    (
                        None
                        if isinstance(
                            self.runtime_adapted_agent, WXORuntimeAdapter
                        )
                        and len(conversation_history) <= 2
                        else session_id
                    ),
                )
            session_id = agent_response.thread_id
            agent_response_content = agent_response.messages[0].content

            logger.debug(f"Agent: {agent_response_content}")

            conversation_history.append(
                Message(
                    role="assistant",
                    content=agent_response_content,
                    type=ContentType.text,
                )
            )
        return session_id

    def run_eval(
        self,
        tool_sequences: list[str],
        session_ids: list[str],
        max_turns: int,
        agent_name: str = None,
    ):
        """
        Run evaluations for multiple tool sequences.

        Args:
            tool_sequences: List of tool sequences to evaluate
            session_ids: List of session IDs for tracking
            max_turns: Maximum turns per conversation

        Returns:
            List of session IDs that were evaluated
        """
        session_ids_map = {}
        for i, tool_sequence in enumerate(tool_sequences):
            user_story = (
                "You need to instruct the agent to invoke the "
                "given tools with the specified arguments."
                "If the tool call has placeholder, resolve them based on the assistant's response. And if there are multiple possible values, make sure to invoke all of them one by one."
            )
            user_story = user_story + str(tool_sequence)

            session_id = self.run_eval_for_instance(
                user_story, max_turns, session_ids[i], agent_name
            )
            session_ids_map[session_id] = session_ids[i]

        return session_ids_map
