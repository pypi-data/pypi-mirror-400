import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Mapping, Optional, Union

from agentops.extractors import Extractor
from agentops.metrics.metrics import Metric
from agentops.prompt.template_render import LLMaaJTemplateRenderer
from agentops.service_provider.provider import Provider
from agentops.type import Message, OrchestrateDataset
from agentops.utils.extracted_context import update_context
from agentops.utils.messages_parser import ParsedMessages

root_dir: str = os.path.dirname(os.path.dirname(__file__))
LLMAAJ_PROMPT_PATH = os.path.join(root_dir, "prompt", "llmaaj_prompt.jinja2")


class Evaluation(ABC):
    """Abstract base class for all evaluations."""

    def __init__(
        self,
        llm_client: Optional[Provider] = None,
        config: Optional[Dict] = None,
    ) -> None:
        self._llm_client = llm_client
        self.config = config
        self._dependencies = []

    @property
    def dependencies(self):
        return self._dependencies

    @dependencies.setter
    def dependencies(self, d):
        self._dependencies = d

    @property
    def llm_client(self) -> Any:
        """Access client, require it if used."""
        if self._llm_client is None:
            raise RuntimeError(
                f"{self.__class__.__name__} requires a client, but none was provided"
            )
        return self._llm_client

    def evaluate(
        self,
        messages: list[Message],
        extracted_context: Mapping[str, Any],
        ground_truth: Optional[OrchestrateDataset] = None,
        metadata: Mapping[str, Any] = None,
    ) -> Union[Optional[Metric], List[Optional[Metric]]]:
        """
        Public evaluation method that applies context updates.

        This method is called by the framework and handles the decorator logic.
        Subclasses should implement do_evaluate() instead.

        Args:
            messages: agent and user conversational messages (includes tool calls)
            extracted_context: dictionary containing data derived from the messages
            ground_truth: ground truth data
            metadata: additional metadata

        Returns:
            Metric or list of metrics
        """
        results = self.do_evaluate(
            messages=messages,
            extracted_context=extracted_context,
            ground_truth=ground_truth,
            metadata=metadata,
        )
        return update_context(self, results, extracted_context)

    @abstractmethod
    def do_evaluate(
        self,
        messages: list[Message],
        extracted_context: Mapping[str, Any],
        ground_truth: Optional[OrchestrateDataset] = None,
        metadata: Mapping[str, Any] = None,
    ) -> Union[Optional[Metric], List[Optional[Metric]]]:
        """
        Evaluation implementation to be overridden by subclasses.

        This method contains the actual evaluation logic.
        The update_context function is called automatically by the evaluate() method.

        Args:
            messages: agent and user conversational messages (includes tool calls)
            extracted_context: dictionary containing data derived from the messages
            ground_truth: ground truth data
            metadata: additional metadata

        Returns:
            Metric or list of metrics
        """
        raise NotImplementedError


class LLMaaJEvaluation(Evaluation, ABC):
    """Evaluation metric for LLMaaJ."""

    @property
    @abstractmethod
    def llmaaj_instructions(self) -> str:
        """LLMaaJ instructions for the evaluator."""
        raise NotImplementedError

    @abstractmethod
    def format_llm_output(self, string: str) -> int | float | bool | str:
        """Format the output of the LLMaaJ query."""
        raise NotImplementedError

    @property
    def selected_context_keys(self) -> set[str]:
        """Override to implement context keys to pass to the prompt."""
        return set()

    def select_context(
        self, extracted_context: Dict[str, Any]
    ) -> dict[str, Any]:
        """Additional context to be added to the prompt."""
        selected_context = {
            key: value
            for key, value in extracted_context.items()
            if key in self.selected_context_keys
        }

        return selected_context

    def do_evaluate(
        self,
        messages: list[Message],
        extracted_context: Mapping[str, Any],
        ground_truth: Optional[OrchestrateDataset] = None,
        metadata: Mapping[str, Any] = None,
    ) -> Optional[Metric]:
        """
        Default LLMaaJ evaluation implementation.

        Subclasses can override this method for custom evaluation logic.
        """
        renderer = LLMaaJTemplateRenderer(LLMAAJ_PROMPT_PATH)
        parsed = ParsedMessages(messages=messages)
        if parsed.user_input is None or parsed.agent_response is None:
            return None
        context = str(self.select_context(extracted_context))
        prompt = renderer.render(
            user_input=parsed.user_input,
            agent_answer=parsed.agent_response,
            llmaaj_instructions=self.llmaaj_instructions,
            context=context,
        )
        response = self.llm_client.chat(prompt)
        value = self.format_llm_output(response.choices[0].message.content)
        return Metric(eval_name=self.name, value=value)
