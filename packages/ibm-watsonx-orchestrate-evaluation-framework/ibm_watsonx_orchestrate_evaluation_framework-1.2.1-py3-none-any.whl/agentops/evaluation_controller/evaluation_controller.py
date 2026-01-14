import os
from collections import deque
from typing import List, Tuple

import rich

from agentops.arg_configs import ControllerConfig, TestConfig
from agentops.llm_user.base_user import BaseUserSimulator
from agentops.runtime_adapter.runtime_adapter import RuntimeAdapter
from agentops.type import (
    CallTracker,
    ContentType,
    ConversationalSearch,
    Message,
    Roles,
)
from agentops.utils.utils import Tokenizer, safe_divide

tokenizer = Tokenizer()


def calculate_word_overlap_similarity_score(
    first_message_text: str, second_message_text: str
) -> float:
    """Calculate the word overlap similarity score between the .content field of two Message objects.
    Args:
        first_message_text (str): The .content field of the first message.
        second_message_text (str): The .content field of the second message.
    """

    words_in_first_message = tokenizer(first_message_text)
    words_in_second_message = tokenizer(second_message_text)

    # Calculate the number of common words
    common_words = set(words_in_first_message) & set(words_in_second_message)
    unique_words = set(words_in_first_message + words_in_second_message)

    unique_words_count = len(unique_words)
    common_words_count = len(common_words)

    return safe_divide(common_words_count, unique_words_count)


def _generate_user_input(
    user_turn: int,
    story: str,
    conversation_history: list[Message],
    llm_user: BaseUserSimulator,
    enable_manual_user_input: bool = False,
    starting_user_input: str | None = None,
    attack_instructions: str | None = None,
) -> Message:
    """Generates the user input for the current turn."""

    if user_turn == 0 and starting_user_input is not None:
        return Message(
            role="user",
            content=starting_user_input,
            type=ContentType.text,
        )

    if enable_manual_user_input:
        content = input("[medium_orchid1]Enter your input[/medium_orchid1] ✍️: ")
        return Message(role="user", content=content, type=ContentType.text)

    # llm generated user input
    return llm_user.generate_user_input(
        story,
        conversation_history,
        attack_instructions=attack_instructions,
    )


class EvaluationController:
    MAX_CONVERSATION_STEPS = int(os.getenv("MAX_CONVERSATION_STEPS", 20))
    MESSAGE_SIMILARITY_THRESHOLD = float(
        os.getenv("MESSAGE_SIMILARITY_THRESHOLD", 0.98)
    )  # if any two consecutive messages are >98% similar, the inference loop will be terminated
    MAX_REPEATING_MESSAGES = int(
        os.getenv("MAX_REPEATING_MESSAGES", 3)
    )  # this is the maximum number of repeating messages by the user or assistant before terminating the inference loop

    def __init__(
        self,
        runtime: RuntimeAdapter,
        llm_user: BaseUserSimulator,
        config: TestConfig | ControllerConfig,
    ):
        self.runtime = runtime
        self.llm_user = llm_user
        self.config = config
        self.repeating_output_detection = self.MAX_REPEATING_MESSAGES >= 2

        if self.repeating_output_detection:
            # Use deque for efficient O(1) operations
            self.recent_user_messages = deque(
                maxlen=self.MAX_REPEATING_MESSAGES
            )
            self.recent_assistant_messages = deque(
                maxlen=self.MAX_REPEATING_MESSAGES
            )

    def run(
        self,
        task_n,
        story,
        agent_name: str,
        starting_user_input: str | None = None,
        attack_instructions: str | None = None,
        max_user_turns: int | None = None,
        session_id: str | None = None,
    ) -> Tuple[
        List[Message], List[CallTracker], List[ConversationalSearch], str
    ]:
        thread_id = session_id
        conversation_history: List[Message] = []
        conversational_search_history_data = []
        call_tracker = CallTracker()

        max_turns = (
            self.MAX_CONVERSATION_STEPS
            if max_user_turns is None
            else max_user_turns
        )

        for user_turn in range(max_turns):
            user_input = _generate_user_input(
                user_turn=user_turn,
                story=story,
                conversation_history=conversation_history,
                llm_user=self.llm_user,
                enable_manual_user_input=self.config.enable_manual_user_input,
                starting_user_input=starting_user_input,
                attack_instructions=attack_instructions,
            )

            if self.config.enable_verbose_logging:
                rich.print(
                    f"[dark_khaki][Task-{task_n}][/dark_khaki] 👤[bold blue] User:[/bold blue]",
                    user_input.content,
                )

            if self._is_end(user_input):
                break

            if self.repeating_output_detection:
                self.recent_user_messages.append(user_input.content)

            conversation_history.append(user_input)

            # (
            #     messages,
            #     thread_id,
            #     conversational_search_data,
            # )
            resp = self.runtime.run(
                user_input,
                context={
                    "agent_name": agent_name,
                    "call_tracker": call_tracker,
                },
                thread_id=thread_id,
            )
            messages = resp.messages
            thread_id = resp.thread_id
            call_tracker.metadata = {"thread_id": thread_id}
            conversational_search_data = resp.context.get(
                "conversational_search_data", []
            )
            if not messages:
                raise RuntimeError(
                    f"[Task-{task_n}] No messages is produced. Exiting task."
                )

            for message in messages:
                if self.repeating_output_detection:
                    if (
                        message.role == Roles.ASSISTANT
                        and message.type == ContentType.text
                    ):
                        self.recent_assistant_messages.append(message.content)

                if (
                    self.config.enable_verbose_logging
                    and message.content.strip()
                ):
                    rich.print(
                        f"[orange3][Task-{task_n}][/orange3] 🤖[bold cyan] Agent:[/bold cyan]",
                        message.content,
                    )

                # hook for subclasses
                if self._post_message_hook(
                    task_n=task_n,
                    step=user_turn,
                    message=message,
                    conversation_history=conversation_history,
                ):
                    return (
                        conversation_history,
                        call_tracker,
                        conversational_search_history_data,
                        thread_id,
                    )

            conversation_history.extend(messages)
            conversational_search_history_data.extend(
                conversational_search_data
            )

        return (
            conversation_history,
            call_tracker,
            conversational_search_history_data,
            thread_id,
        )

    def _post_message_hook(self, **kwargs) -> bool:
        """
        Hook for subclasses to extend behavior.
        Return True to break the loop early.
        """
        return False

    def _is_looping(self, messages: deque) -> bool:
        """Checks whether the user or assistant is stuck in a loop.
        Args:
            messages (deque): Defines the message cache to be assessed for similarity.
        Returns:
            bool: True if stuck in a loop, False otherwise.
        """
        sim_count = 0

        if len(messages) >= self.MAX_REPEATING_MESSAGES:
            oldest_cached_message = messages[0]
            for i, old_message in enumerate(messages):
                if i == 0:
                    continue
                if oldest_cached_message == old_message:
                    sim_count += 1
                elif (
                    calculate_word_overlap_similarity_score(
                        oldest_cached_message, old_message
                    )
                    > self.MESSAGE_SIMILARITY_THRESHOLD
                ):
                    sim_count += 1

        return sim_count >= self.MAX_REPEATING_MESSAGES - 1

    def _is_end(self, current_user_input: Message) -> bool:
        """
        Check if the user input indicates the end of the conversation.

        - This function checks if the user input contains 'END'.
        - An END is also triggered when the message cache(s) is filled with messages that are too similar.
        - Elaborate checking ONLY if EvaluationController.END_IF_MISBEHAVING=True
        Args:
            current_user_input (Message): The user message.
        Returns:
            bool: True if the user input indicates an END, False otherwise.
        """
        current_user_message_content = current_user_input.content.strip()

        # Check if the user message contains 'END'
        if "END" in current_user_message_content:
            return True

        if self.repeating_output_detection:
            # Check for repeating user or assistant messages
            if self._is_looping(self.recent_user_messages) or self._is_looping(
                self.recent_assistant_messages
            ):
                return True

        # Final fallback for termination is in the main inference loop, which defines MAX_CONVERSATION_STEPS
        return False


class AttackEvaluationController(EvaluationController):
    def __init__(
        self, *args, attack_data=None, attack_evaluator=None, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.attack_data = attack_data
        self.attack_evaluator = attack_evaluator

    def _post_message_hook(
        self, task_n, step, message, conversation_history
    ) -> bool:
        """Override hook to add live attack evaluation."""
        if self.attack_evaluator and self.attack_data:
            success = self.attack_evaluator.evaluate(
                self.attack_data, conversation_history + [message]
            )
            if success:
                rich.print(
                    f"[bold green]Attack for [Task-{task_n}] succeeded early at step {step}! Stopping simulation.[/bold green]"
                )
                # persist the live result so the aggregator can pick it up later
                try:
                    self.attack_evaluator.save_evaluation_result(
                        self.attack_data, True
                    )
                except Exception:
                    pass
                conversation_history.append(message)
                return True
        return False
