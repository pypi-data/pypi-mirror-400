from abc import ABC, abstractmethod
from typing import Any, Dict, List, Mapping, Optional

from agentops.type import Message, OrchestrateDataset
from agentops.utils.extracted_context import update_context


class Extractor(ABC):
    def __init__(self, config: Optional[Dict] = None):
        self.config = config
        self._dependencies = []

    @property
    def dependencies(self):
        if not self._dependencies:
            return []

        return self._dependencies

    @dependencies.setter
    def dependencies(self, d):
        self._dependencies = d

    def extract(
        self,
        messages: List[Message],
        ground_truth: Optional[OrchestrateDataset] = None,
        extracted_context: Mapping[str, Any] = {},
        **kwargs,
    ) -> Any:
        """
        Public extraction method that applies context updates.

        This method is called by the framework and handles the decorator logic.
        Subclasses should implement do_extract() instead.

        Args:
            messages: agent and user conversational messages (includes tool calls)
            ground_truth: ground truth data
            extracted_context: dictionary containing data derived from the messages
            **kwargs: additional keyword arguments

        Returns:
            Extracted data
        """
        results = self.do_extract(
            messages=messages,
            ground_truth=ground_truth,
            extracted_context=extracted_context,
            **kwargs,
        )
        return update_context(self, results, extracted_context)

    @abstractmethod
    def do_extract(
        self,
        messages: List[Message],
        ground_truth: Optional[OrchestrateDataset] = None,
        extracted_context: Mapping[str, Any] = {},
        **kwargs,
    ) -> Any:
        """
        Extraction implementation to be overridden by subclasses.

        This method contains the actual extraction logic.
        The update_context function is called automatically by the extract() method.

        Args:
            messages: agent and user conversational messages (includes tool calls)
            ground_truth: ground truth data
            extracted_context: dictionary containing data derived from the messages
            **kwargs: additional keyword arguments

        Returns:
            Extracted data
        """
        raise NotImplementedError
