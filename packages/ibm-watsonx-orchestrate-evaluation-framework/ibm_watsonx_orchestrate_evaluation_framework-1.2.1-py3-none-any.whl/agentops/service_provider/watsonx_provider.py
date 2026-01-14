import dataclasses
import json
import logging
import os
import time
import uuid
from threading import Lock
from types import MappingProxyType
from typing import Any, Dict, List, Optional, Sequence

import requests

from agentops.service_provider.provider import Provider
from agentops.type import ChatCompletions, Choice, Message

logger = logging.getLogger(__name__)

# IAM
ACCESS_URL = "https://iam.cloud.ibm.com/identity/token"
ACCESS_HEADER = {
    "content-type": "application/x-www-form-urlencoded",
    "accept": "application/json",
}

YPQA_URL = "https://yp-qa.ml.cloud.ibm.com"
PROD_URL = "https://us-south.ml.cloud.ibm.com"

DEFAULT_PARAM = MappingProxyType(
    {"min_new_tokens": 1, "decoding_method": "greedy", "max_new_tokens": 400}
)


def _truncate(value: Any, max_len: int = 1000) -> str:
    if value is None:
        return ""
    s = str(value)
    return (
        s
        if len(s) <= max_len
        else s[:max_len] + f"... [truncated {len(s) - max_len} chars]"
    )


def _translate_params_to_chat(
    params: Dict[str, Any] = {},
) -> Dict[str, Any]:
    """
    Translate legacy generation params to chat.completions params.
    """
    translated_params: Dict[str, Any] = {}

    if "max_new_tokens" in params:
        translated_params["max_tokens"] = params["max_new_tokens"]

    if params.get("decoding_method") == "greedy":
        translated_params.setdefault("temperature", 0)
        translated_params.setdefault("top_p", 1)

    passthrough = {
        "temperature",
        "top_p",
        "n",
        "stream",
        "stop",
        "presence_penalty",
        "frequency_penalty",
        "logit_bias",
        "user",
        "seed",
        "response_format",
    }
    for k in passthrough:
        if k in params:
            translated_params[k] = params[k]

    return translated_params


class WatsonXProvider(Provider):
    def __init__(
        self,
        model_id: Optional[str] = None,
        api_key: Optional[str] = None,
        space_id: Optional[str] = None,
        api_endpoint: str = PROD_URL,
        url: str = ACCESS_URL,
        timeout: int = 60,
        params: Optional[Any] = None,
        embedding_model_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        token: Optional[str] = None,
        instance_url: Optional[str] = None,
    ):
        super().__init__()

        self.url = url
        if (embedding_model_id is None) and (model_id is None):
            raise Exception(
                "either model_id or embedding_model_id must be specified"
            )
        self.model_id = model_id
        logger.info("[d b]Using inference model %s", self.model_id)
        api_key = os.environ.get("WATSONX_APIKEY", api_key)
        if not api_key:
            raise Exception("apikey must be specified")
        self.api_key = api_key
        self.access_data = {
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": self.api_key,
        }
        self.api_endpoint = (api_endpoint or PROD_URL).rstrip("/")
        space_id = os.environ.get("WATSONX_SPACE_ID", space_id)
        if not space_id:
            raise Exception("space id must be specified")
        self.space_id = space_id
        self.timeout = timeout
        self.embedding_model_id = embedding_model_id
        self.lock = Lock()

        self.params = params if params is not None else DEFAULT_PARAM
        if isinstance(self.params, MappingProxyType):
            self.params = dict(self.params)
        if dataclasses.is_dataclass(self.params):
            self.params = dataclasses.asdict(self.params)

        self.system_prompt = system_prompt

        self.refresh_time = None
        self.access_token = None
        self._refresh_token()

        self.LEGACY_GEN_URL = (
            f"{self.api_endpoint}/ml/v1/text/generation?version=2023-05-02"
        )
        self.CHAT_COMPLETIONS_URL = f"{self.api_endpoint}/ml/v1/text/chat"
        self.EMBEDDINGS_URL = (
            f"{self.api_endpoint}/ml/v1/text/embeddings?version=2023-10-25"
        )

    def _get_access_token(self):
        response = requests.post(
            self.url,
            headers=ACCESS_HEADER,
            data=self.access_data,
            timeout=self.timeout,
        )
        if response.status_code == 200:
            token_data = json.loads(response.text)
            token = token_data["access_token"]
            expiration = token_data["expiration"]
            expires_in = token_data["expires_in"]
            # 9 minutes before expire
            refresh_time = expiration - int(0.15 * expires_in)
            return token, refresh_time

        raise RuntimeError(
            f"Try to acquire access token and get {response.status_code}. Reason: {response.text} "
        )

    def prepare_header(self):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        return headers

    def _refresh_token(self):
        # if we do not have a token or the current timestamp is 9 minutes away from expire.
        if not self.access_token or time.time() > self.refresh_time:
            with self.lock:
                if not self.access_token or time.time() > self.refresh_time:
                    (
                        self.access_token,
                        self.refresh_time,
                    ) = self._get_access_token()

    def chat(
        self,
        messages: Sequence[Dict[str, str]],
        params: Optional[Dict[str, Any]] = None,
    ) -> ChatCompletions:
        """
        Sends a multi-message chat request to /ml/v1/text/chat
        Returns ChatCompletions object.
        """
        if self.model_id is None:
            raise Exception("model id must be specified for chat")

        self._refresh_token()
        headers = self.prepare_header()

        wx_messages: List[Dict[str, Any]] = []
        for m in messages:
            role = m.get("role")
            content = m.get("content", "")
            if role == "user" and isinstance(content, str):
                wx_messages.append(
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": content}],
                    }
                )
            else:
                wx_messages.append({"role": role, "content": content})

        merged_params = dict(self.params or {})
        if params:
            merged_params.update(params)
        chat_params = _translate_params_to_chat(merged_params)
        chat_params.pop("stream", None)
        if "time_limit" in merged_params:
            chat_params["time_limit"] = merged_params["time_limit"]

        payload: Dict[str, Any] = {
            "model_id": self.model_id,
            "space_id": self.space_id,
            "messages": wx_messages,
            **chat_params,
        }

        url = f"{self.CHAT_COMPLETIONS_URL}?version=2024-10-08"
        request_id = str(uuid.uuid4())
        t0 = time.time()

        last_user = next(
            (
                m.get("content", "")
                for m in reversed(messages)
                if m.get("role") == "user"
            ),
            "",
        )
        logger.debug(
            "[d][b]Sending chat.completions request (non-streaming) | request_id=%s url=%s model=%s space_id=%s params=%s input_preview=%s",
            request_id,
            url,
            self.model_id,
            self.space_id,
            json.dumps(chat_params, sort_keys=True, ensure_ascii=False),
            _truncate(last_user, 200),
        )

        resp = None
        try:
            resp = requests.post(
                url=url, headers=headers, json=payload, timeout=self.timeout
            )
            duration_ms = int((time.time() - t0) * 1000)
            resp.raise_for_status()
            data = resp.json()

            choice = data["choices"][0]
            content = choice["message"]["content"]
            finish_reason = choice.get("finish_reason")
            usage = data.get("usage", {})
            api_request_id = resp.headers.get(
                "x-request-id"
            ) or resp.headers.get("request-id")

            logger.debug(
                "[d][b]chat.completions response received (non-streaming) | request_id=%s status_code=%s duration_ms=%s finish_reason=%s usage=%s output_preview=%s api_request_id=%s",
                request_id,
                resp.status_code,
                duration_ms,
                finish_reason,
                json.dumps(usage, sort_keys=True, ensure_ascii=False),
                _truncate(content, 2000),
                api_request_id,
            )

            return ChatCompletions(
                choices=[
                    Choice(
                        message=Message(role="", content=content),
                        finish_reason=finish_reason,
                    )
                ]
            )

        except Exception as e:
            duration_ms = int((time.time() - t0) * 1000)
            status_code = getattr(resp, "status_code", None)
            resp_text_preview = (
                _truncate(getattr(resp, "text", None), 2000)
                if resp is not None
                else None
            )

            logger.exception(
                "chat.completions request failed (non-streaming) | request_id=%s status_code=%s duration_ms=%s response_text_preview=%s",
                request_id,
                status_code,
                duration_ms,
                resp_text_preview,
            )
            with self.lock:
                if (
                    "authentication_token_expired" in str(e)
                    or status_code == 401
                ):
                    try:
                        self.access_token, self.refresh_time = (
                            self._get_access_token()
                        )
                    except Exception:
                        pass
            raise

    def encode(self, sentences: List[str]) -> List[list]:
        if self.embedding_model_id is None:
            raise Exception(
                "embedding model id must be specified for text encoding"
            )

        self._refresh_token()
        headers = self.prepare_header()

        # Minimal logging for embeddings
        request_id = str(uuid.uuid4())
        t0 = time.time()
        logger.debug(
            "[d][b]Sending embeddings request | request_id=%s url=%s model=%s space_id=%s num_inputs=%s",
            request_id,
            self.EMBEDDINGS_URL,
            self.embedding_model_id,
            self.space_id,
            len(sentences),
        )

        payload = {
            "inputs": sentences,
            "model_id": self.embedding_model_id,
            "space_id": self.space_id,
        }

        resp = requests.post(
            url=self.EMBEDDINGS_URL,
            headers=headers,
            json=payload,
            timeout=self.timeout,
        )
        duration_ms = int((time.time() - t0) * 1000)

        if resp.status_code == 200:
            data = resp.json()
            vectors = [entry["embedding"] for entry in data["results"]]
            logger.debug(
                "[d][b]Embeddings response received | request_id=%s status_code=%s duration_ms=%s num_vectors=%s",
                request_id,
                resp.status_code,
                duration_ms,
                len(vectors),
            )
            return vectors

        logger.error(
            "[d b red]Embeddings request failed | request_id=%s status_code=%s duration_ms=%s response_text_preview=%s",
            request_id,
            resp.status_code,
            duration_ms,
            _truncate(resp.text, 2000),
        )
        resp.raise_for_status()


if __name__ == "__main__":
    provider = WatsonXProvider(
        model_id="meta-llama/llama-3-2-90b-vision-instruct",
        system_prompt="Respond in Spanish only",
    )

    print(provider.query("Hello, how are you?"))
