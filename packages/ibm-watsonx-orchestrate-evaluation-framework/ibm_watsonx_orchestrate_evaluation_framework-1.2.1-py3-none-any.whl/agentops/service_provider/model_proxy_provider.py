import json
import logging
import os
import time
import uuid
from threading import Lock
from typing import Any, Dict, List, Optional, Sequence, Tuple

import requests

from agentops.service_provider.provider import Provider
from agentops.type import ChatCompletions, Choice, Message
from agentops.utils.utils import is_ibm_cloud_url

logger = logging.getLogger(__name__)

AUTH_ENDPOINT_AWS = (
    "https://iam.platform.saas.ibm.com/siusermgr/api/1.0/apikeys/token"
)
AUTH_ENDPOINT_IBM_CLOUD = "https://iam.cloud.ibm.com/identity/token"
DEFAULT_PARAM = {
    "min_new_tokens": 1,
    "decoding_method": "greedy",
    "max_new_tokens": 2500,
}


def _infer_cpd_auth_url(instance_url: str) -> str:
    inst = (instance_url or "").rstrip("/")
    if not inst:
        return "/icp4d-api/v1/authorize"
    if "/orchestrate" in inst:
        base = inst.split("/orchestrate", 1)[0].rstrip("/")
        return base + "/icp4d-api/v1/authorize"
    return inst + "/icp4d-api/v1/authorize"


def _normalize_cpd_auth_url(url: str) -> str:
    u = (url or "").rstrip("/")
    if u.endswith("/icp4d-api"):
        return u + "/v1/authorize"
    return url


def _truncate(value: Any, max_len: int = 1000) -> str:
    if value is None:
        return ""
    s = str(value)
    return (
        s
        if len(s) <= max_len
        else s[:max_len] + f"... [truncated {len(s) - max_len} chars]"
    )


def _translate_params_to_chat(params: Dict[str, Any] | None) -> Dict[str, Any]:
    # Translate legacy generation params to chat.completions params.
    p = params or {}
    out: Dict[str, Any] = {}

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
        "max_tokens",
        "seed",
        "response_format",
    }
    for k in passthrough:
        if k in p:
            out[k] = p[k]

    if "max_new_tokens" in p and "max_tokens" not in out:
        out["max_tokens"] = p["max_new_tokens"]

    return out


class ModelProxyProvider(Provider):
    def __init__(
        self,
        model_id: Optional[str] = None,
        api_key: Optional[str] = None,
        instance_url: Optional[str] = None,
        timeout: int = 300,
        embedding_model_id: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None,
        token: Optional[str] = None,
    ):
        super().__init__()

        instance_url = os.environ.get("WO_INSTANCE", instance_url)
        if not instance_url:
            raise RuntimeError(
                "instance url must be specified to use WO model proxy"
            )

        self.timeout = timeout
        self.model_id = os.environ.get("MODEL_OVERRIDE", model_id)
        logger.info("[d b]Using inference model %s", self.model_id)
        self.embedding_model_id = embedding_model_id

        self.api_key = os.environ.get("WO_API_KEY", api_key)
        self.username = os.environ.get("WO_USERNAME", None)
        self.password = os.environ.get("WO_PASSWORD", None)
        self.auth_type = os.environ.get(
            "WO_AUTH_TYPE", ""
        ).lower()  # explicit override if set, otherwise inferred- match ADK values
        explicit_auth_url = os.environ.get("AUTHORIZATION_URL", None)

        self.is_ibm_cloud = is_ibm_cloud_url(instance_url)
        self.instance_url = instance_url.rstrip("/")

        self.auth_mode, self.auth_url = self._resolve_auth_mode_and_url(
            explicit_auth_url=explicit_auth_url
        )
        self._wo_ssl_verify = (
            os.environ.get("WO_SSL_VERIFY", "true").lower() != "false"
        )
        env_space_id = os.environ.get("WATSONX_SPACE_ID", None)
        if self.auth_mode == "cpd":
            if not env_space_id or not env_space_id.strip():
                raise RuntimeError(
                    "CPD mode requires WATSONX_SPACE_ID environment variable to be set"
                )
            self.space_id = env_space_id.strip()
        else:
            self.space_id = (
                env_space_id.strip()
                if env_space_id and env_space_id.strip()
                else "1"
            )

        if self.auth_mode == "cpd":
            if "/orchestrate" in self.instance_url:
                self.instance_url = self.instance_url.split("/orchestrate", 1)[
                    0
                ].rstrip("/")
            if not self.username:
                raise RuntimeError("CPD auth requires WO_USERNAME to be set")
            if not (self.password or self.api_key):
                raise RuntimeError(
                    "CPD auth requires either WO_PASSWORD or WO_API_KEY to be set (with WO_USERNAME)"
                )
        else:
            if not self.api_key:
                raise RuntimeError(
                    "WO_API_KEY must be specified for SaaS or IBM IAM auth"
                )

        # Endpoints
        self.url = (
            self.instance_url + "/ml/v1/text/generation?version=2024-05-01"
        )  # legacy
        self.chat_url = self.instance_url + "/ml/v1/chat/completions"  # chat
        self.embedding_url = self.instance_url + "/ml/v1/text/embeddings"

        self.lock = Lock()
        self.token, self.refresh_time = self.get_token()
        self.params = params if params else DEFAULT_PARAM
        self.system_prompt = system_prompt

    def _resolve_auth_mode_and_url(
        self, explicit_auth_url: str | None
    ) -> Tuple[str, str]:
        """
        Returns (auth_mode, auth_url)
        - auth_mode: "cpd" | "ibm_iam" | "saas"
        """
        if explicit_auth_url:
            if "/icp4d-api" in explicit_auth_url:
                return "cpd", _normalize_cpd_auth_url(explicit_auth_url)
            if self.auth_type == "ibm_iam":
                return "ibm_iam", explicit_auth_url
            elif self.auth_type == "saas":
                return "saas", explicit_auth_url
            else:
                mode = "ibm_iam" if self.is_ibm_cloud else "saas"
                return mode, explicit_auth_url

        if self.auth_type == "cpd":
            inferred_cpd_url = _infer_cpd_auth_url(self.instance_url)
            return "cpd", inferred_cpd_url
        if self.auth_type == "ibm_iam":
            return "ibm_iam", AUTH_ENDPOINT_IBM_CLOUD
        if self.auth_type == "saas":
            return "saas", AUTH_ENDPOINT_AWS

        if "/orchestrate" in self.instance_url:
            inferred_cpd_url = _infer_cpd_auth_url(self.instance_url)
            return "cpd", inferred_cpd_url

        if self.is_ibm_cloud:
            return "ibm_iam", AUTH_ENDPOINT_IBM_CLOUD
        else:
            return "saas", AUTH_ENDPOINT_AWS

    def get_token(self):
        headers = {}
        post_args = {}
        timeout = 10
        exchange_url = self.auth_url

        if self.auth_mode == "ibm_iam":
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            }
            form_data = {
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": self.api_key,
            }
            post_args = {"data": form_data}
            resp = requests.post(
                exchange_url,
                headers=headers,
                timeout=timeout,
                verify=self._wo_ssl_verify,
                **post_args,
            )
        elif self.auth_mode == "cpd":
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
            body = {"username": self.username}
            if self.password:
                body["password"] = self.password
            else:
                body["api_key"] = self.api_key
            timeout = self.timeout
            resp = requests.post(
                exchange_url,
                headers=headers,
                json=body,
                timeout=timeout,
                verify=self._wo_ssl_verify,
            )
        else:
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
            post_args = {"json": {"apikey": self.api_key}}
            resp = requests.post(
                exchange_url,
                headers=headers,
                timeout=timeout,
                verify=self._wo_ssl_verify,
                **post_args,
            )

        if resp.status_code == 200:
            json_obj = resp.json()
            token = json_obj.get("access_token") or json_obj.get("token")
            if not token:
                raise RuntimeError(
                    f"No token field found in response: {json_obj!r}"
                )

            expires_in = json_obj.get("expires_in")
            try:
                expires_in = int(expires_in) if expires_in is not None else None
            except Exception:
                expires_in = None
            if not expires_in or expires_in <= 0:
                expires_in = int(os.environ.get("TOKEN_DEFAULT_EXPIRES_IN", 1))

            refresh_time = time.time() + int(0.8 * expires_in)
            return token, refresh_time

        resp.raise_for_status()

    def refresh_token_if_expires(self):
        if time.time() > self.refresh_time:
            with self.lock:
                if time.time() > self.refresh_time:
                    self.token, self.refresh_time = self.get_token()

    def get_header(self):
        return {"Authorization": f"Bearer {self.token}"}

    def encode(self, sentences: List[str]) -> List[list]:
        if self.embedding_model_id is None:
            raise Exception(
                "embedding model id must be specified for text generation"
            )

        self.refresh_token_if_expires()
        headers = self.get_header()
        payload = {
            "inputs": sentences,
            "model_id": self.embedding_model_id,
            "space_id": self.space_id,
            "max_token": 1000,
        }
        # "timeout": self.timeout}
        resp = requests.post(
            self.embedding_url,
            json=payload,
            headers=headers,
            verify=self._wo_ssl_verify,
            timeout=self.timeout,
        )

        if resp.status_code == 200:
            json_obj = resp.json()
            return json_obj["generated_text"]

        resp.raise_for_status()

    def chat(
        self,
        messages: Sequence[Dict[str, str]],
        params: Optional[Dict[str, Any]] = None,
    ) -> ChatCompletions:
        # Non-streaming chat using /ml/v1/chat/completions.
        if self.model_id is None:
            raise Exception("model id must be specified for chat")

        self.refresh_token_if_expires()
        headers = self.get_header()

        # Convert messages to watsonx format: user content is typed list
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
        chat_params.pop("stream", None)  # force non-streaming
        if "time_limit" in merged_params:
            chat_params["time_limit"] = merged_params["time_limit"]

        payload: Dict[str, Any] = {
            "model_id": self.model_id,
            "space_id": self.space_id,
            "messages": wx_messages,
            **chat_params,
        }

        url = f"{self.instance_url}/ml/v1/text/chat?version=2024-10-08"

        last_user = next(
            (
                m.get("content", "")
                for m in reversed(messages)
                if m.get("role") == "user"
            ),
            "",
        )
        request_id = str(uuid.uuid4())
        start_time = time.time()

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
                url,
                json=payload,
                headers=headers,
                verify=self._wo_ssl_verify,
                timeout=self.timeout,
            )
            duration_ms = int((time.time() - start_time) * 1000)
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
                        message=Message(role="assistant", content=content),
                        finish_reason=finish_reason,
                    )
                ]
            )

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
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
                    self.token, self.refresh_time = self.get_token()
            raise


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    provider = ModelProxyProvider(
        model_id="meta-llama/llama-3-3-70b-instruct",
        embedding_model_id="ibm/slate-30m-english-rtrvr",
        system_prompt="Respond in Spanish only",
    )
    print(provider.query("Hello, how are you?"))
