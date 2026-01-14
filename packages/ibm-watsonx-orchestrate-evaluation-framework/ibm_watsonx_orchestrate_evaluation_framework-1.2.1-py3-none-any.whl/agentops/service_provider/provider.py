from __future__ import annotations

import logging
import os
from abc import ABC, ABCMeta, abstractmethod
from dataclasses import dataclass
from threading import Lock
from typing import Any, Dict, List, Optional, Sequence, Tuple

from agentops.type import ChatCompletions, ProviderInstancesCacheKey


class SingletonProviderMeta(type):

    _provider_instances: Dict[str, "Provider"] = {}
    _instantiation_lock = Lock()

    def __call__(cls, *args, **kwargs):

        key_str: str = str(cls._get_key(cls.__name__, args, kwargs))

        if key_str not in cls._provider_instances:
            with cls._instantiation_lock:
                if key_str not in cls._provider_instances:
                    cls._provider_instances[key_str] = super().__call__(
                        *args, **kwargs
                    )

        return cls._provider_instances[key_str]

    @staticmethod
    def _get_key(
        provider: str, args: Tuple[Any, ...], kwargs: Dict[str, Any]
    ) -> ProviderInstancesCacheKey:

        args_str = str(args) if args else "noargs"
        kwargs_str = str(sorted(kwargs.items())) if kwargs else "nokwargs"

        return ProviderInstancesCacheKey(
            provider=provider,
            hashed_args=args_str,
            hashed_kwargs=kwargs_str,
        )


class SingletonProviderABCMeta(ABCMeta, SingletonProviderMeta):
    pass


class Provider(ABC, metaclass=SingletonProviderABCMeta):
    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def chat(
        self,
        messages: Sequence[Dict[str, str]],
        params: Optional[Dict[str, Any]] = None,
    ) -> ChatCompletions:
        raise NotImplementedError("Not implemented")

    @abstractmethod
    def encode(self, sentences: List[str]) -> List[list]:
        raise NotImplementedError(
            f"{self.__class__.__name__} does not implement encode()."
        )

    def query(self, sentence: str) -> ChatCompletions:
        messages = []
        if self.system_prompt is not None:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": sentence})
        return self.chat(messages)
