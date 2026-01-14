import json
import logging
import os
import time
import uuid
from typing import Any, Dict, Iterator, List, Optional, Sequence

import requests

from agentops.service_provider.provider import Provider
from agentops.type import ChatCompletions, Choice, Message

logger = logging.getLogger(__name__)

OLLAMA_URL = os.environ.get("OLLAMA_HOST", "http://localhost:11434")


def _truncate(value: Any, max_len: int = 1000) -> str:
    if value is None:
        return ""
    s = str(value)
    return (
        s
        if len(s) <= max_len
        else s[:max_len] + f"... [truncated {len(s) - max_len} chars]"
    )


def _translate_params_to_ollama_options(
    params: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Map generic params to Ollama 'options' field.
    Ollama options docs: https://github.com/ollama/ollama/blob/main/docs/modelfile.md#parameters
    """
    p = params or {}
    out: Dict[str, Any] = {}

    for key in ("temperature", "top_p", "top_k", "stop", "seed"):
        if key in p:
            out[key] = p[key]

    if "max_new_tokens" in p:
        out["num_predict"] = p["max_new_tokens"]
    elif "max_tokens" in p:
        out["num_predict"] = p["max_tokens"]

    if "repeat_penalty" in p:
        out["repeat_penalty"] = p["repeat_penalty"]
    if "repeat_last_n" in p:
        out["repeat_last_n"] = p["repeat_last_n"]

    return out


class OllamaProvider(Provider):
    def __init__(
        self,
        model_id: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 300,
        system_prompt: Optional[str] = None,
        token: Optional[str] = None,
        instance_url: Optional[str] = None,
    ):
        super().__init__()
        self.generate_url = (
            OLLAMA_URL.rstrip("/") + "/api/generate"
        )  # legacy text generation
        self.chat_url = OLLAMA_URL.rstrip("/") + "/api/chat"  # chat endpoint
        self.model_id = os.environ.get("MODEL_OVERRIDE", model_id)
        logger.info("[d b]Using inference model %s", self.model_id)
        self.params = params or {}
        self.timeout = timeout
        self.system_prompt = system_prompt

    def chat(
        self,
        messages: Sequence[Dict[str, str]],
        params: Optional[Dict[str, Any]] = None,
    ) -> ChatCompletions:
        """
        Non-streaming chat via /api/chat.
        """
        if not self.model_id:
            raise ValueError("model_id must be specified for Ollama chat")

        merged_params = dict(self.params or {})
        if params:
            merged_params.update(params)
        options = _translate_params_to_ollama_options(merged_params)

        payload: Dict[str, Any] = {
            "model": self.model_id,
            "messages": list(messages),
            "stream": False,
        }
        if options:
            payload["options"] = options

        last_user = next(
            (
                m.get("content", "")
                for m in reversed(messages)
                if m.get("role") == "user"
            ),
            "",
        )
        request_id = str(uuid.uuid4())
        t0 = time.time()

        logger.debug(
            "[d][b]Sending Ollama chat request (non-streaming, multi-message) | request_id=%s url=%s model=%s params=%s input_preview=%s",
            request_id,
            self.chat_url,
            self.model_id,
            json.dumps(options, sort_keys=True, ensure_ascii=False),
            _truncate(last_user, 200),
        )

        resp = None
        try:
            resp = requests.post(
                self.chat_url, json=payload, timeout=self.timeout
            )
            duration_ms = int((time.time() - t0) * 1000)
            resp.raise_for_status()
            data = resp.json()

            message = data.get("message") or {}
            content = message.get("content", "") or ""
            finish_reason = data.get("done_reason")
            usage = {
                "prompt_eval_count": data.get("prompt_eval_count"),
                "eval_count": data.get("eval_count"),
                "prompt_eval_duration_ns": data.get("prompt_eval_duration"),
                "eval_duration_ns": data.get("eval_duration"),
                "total_duration_ns": data.get("total_duration"),
                "load_duration_ns": data.get("load_duration"),
            }

            logger.debug(
                "[d][b]Ollama chat response received (non-streaming, multi-message) | request_id=%s status_code=%s duration_ms=%s finish_reason=%s usage=%s output_preview=%s",
                request_id,
                resp.status_code,
                duration_ms,
                finish_reason,
                json.dumps(usage, sort_keys=True, ensure_ascii=False),
                _truncate(content, 2000),
            )

            return ChatCompletions(
                choices=[
                    Choice(
                        message=Message(role="", content=content),
                        finish_reason=finish_reason,
                    )
                ]
            )

        except Exception:
            duration_ms = int((time.time() - t0) * 1000)
            status_code = getattr(resp, "status_code", None)
            resp_text_preview = (
                _truncate(getattr(resp, "text", None), 2000)
                if resp is not None
                else None
            )

            logger.exception(
                "Ollama chat request (non-streaming, multi-message) encountered an error | request_id=%s status_code=%s duration_ms=%s response_text_preview=%s",
                request_id,
                status_code,
                duration_ms,
                resp_text_preview,
            )
            raise

    def encode(self, sentences: List[str]) -> List[list]:
        raise NotImplementedError(
            "encode is not implemented for OllamaProvider"
        )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    provider = OllamaProvider(
        model_id="llama3.1:8b", system_prompt="Respond in Spanish only"
    )

    print(provider.query("Hello, how are you?"))

    # chat API
    messages = [
        {"role": "system", "content": "You are concise."},
        {"role": "user", "content": "List three fruits."},
    ]
    result = provider.chat(messages)
    print(result)
