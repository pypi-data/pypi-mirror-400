from __future__ import annotations

import json
import logging
import os
import time
import uuid
from threading import Lock
from typing import Any, Dict, List, Optional, Sequence, Tuple

import requests
import yaml

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
}


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
        # "max_tokens", #reasoning frequently uses up max_tokens so not passing for now
        "seed",
        "response_format",
    }
    for k in passthrough:
        if k in p:
            out[k] = p[k]

    # reasoning frequently uses up max_tokens so not passing for now
    # if "max_new_tokens" in p and "max_completion_tokens" not in out:
    #    out["max_completion_tokens"] = p["max_new_tokens"]

    return out


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


def _get_active_tenant_name() -> Optional[str]:
    """
    Read the active tenant name from the orchestrate config file.
    Returns None if the config file doesn't exist or doesn't have an active environment.
    """
    env_config_path = (
        f"{os.path.expanduser('~')}/.config/orchestrate/config.yaml"
    )
    try:
        with open(env_config_path, "r", encoding="utf-8") as f:
            env_config = yaml.safe_load(f) or {}
            context = env_config.get("context", {})
            return context.get("active_environment")
    except (FileNotFoundError, yaml.YAMLError):
        return None


class GatewayProvider(Provider):

    def __init__(
        self,
        model_id: Optional[str] = None,
        api_key: Optional[str] = None,
        instance_url: Optional[str] = None,
        timeout: int = 300,
        embedding_model_id: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None,
        chat_path: Optional[str] = None,
        embeddings_path: Optional[str] = None,
        gateway_provider: Optional[str] = None,
        gateway_api_key_label: Optional[str] = None,
        x_gateway_config: Optional[Dict[str, Any]] = None,
        # New: static bearer token (overridden by WO_TOKEN if present)
        token: Optional[str] = None,
    ):
        super().__init__()
        instance_url = os.environ.get("WO_INSTANCE", instance_url)
        if not instance_url:
            tenant_name = _get_active_tenant_name()
            logger.info("[d b]Gateway provider using tenant: %s", tenant_name)
            from agentops.service_instance import tenant_setup

            token, instance_url, _ = tenant_setup(
                service_url=None, tenant_name=tenant_name
            )

        if not instance_url:
            raise RuntimeError(
                "instance url must be specified for gateway provider"
            )
        self.timeout = timeout
        self.model_id = os.environ.get("MODEL_OVERRIDE", model_id)
        logger.info("[d b]Using inference model %s", self.model_id)
        self.embedding_model_id = embedding_model_id

        self.api_key = os.environ.get("WO_API_KEY", api_key)
        self.username = os.environ.get("WO_USERNAME", None)
        self.password = os.environ.get("WO_PASSWORD", None)
        self.auth_type = os.environ.get("WO_AUTH_TYPE", "").lower()
        explicit_auth_url = os.environ.get("AUTHORIZATION_URL", None)

        self.is_ibm_cloud = is_ibm_cloud_url(instance_url)
        self.instance_url = instance_url.rstrip("/")

        self._wo_ssl_verify = (
            os.environ.get("WO_SSL_VERIFY", "true").lower() != "false"
        )

        # Decide: static token vs exchange/refresh
        token_from_env = os.environ.get("WO_TOKEN", None)
        static_token = token_from_env if token_from_env is not None else token
        self._use_static_token = bool(static_token)

        if not self._use_static_token:
            self.auth_mode, self.auth_url = self._resolve_auth_mode_and_url(
                explicit_auth_url=explicit_auth_url
            )
        else:
            self.auth_mode, self.auth_url = ("static", "")

        env_space_id = os.environ.get("WATSONX_SPACE_ID", None)
        if self._use_static_token:
            self.space_id = (
                env_space_id.strip()
                if env_space_id and env_space_id.strip()
                else "1"
            )
        else:
            if self.auth_mode == "cpd":
                if not env_space_id or not env_space_id.strip():
                    raise RuntimeError(
                        "CPD mode requires WATSONX_SPACE_ID environment variable to be set"
                    )
                self.space_id = env_space_id.strip()
                if "/orchestrate" in self.instance_url:
                    self.instance_url = self.instance_url.split(
                        "/orchestrate", 1
                    )[0].rstrip("/")
                if not self.username:
                    raise RuntimeError(
                        "CPD auth requires WO_USERNAME to be set"
                    )
                if not (self.password or self.api_key):
                    raise RuntimeError(
                        "CPD auth requires either WO_PASSWORD or WO_API_KEY to be set (with WO_USERNAME)"
                    )
            else:
                self.space_id = (
                    env_space_id.strip()
                    if env_space_id and env_space_id.strip()
                    else "1"
                )
                if not self.api_key:
                    raise RuntimeError(
                        "WO_API_KEY must be specified for SaaS or IBM IAM auth"
                    )

        default_chat_path = os.environ.get(
            "GATEWAY_CHAT_PATH",
            "/v1/orchestrate/gateway/model/chat/completions",
        )
        default_embeddings_path = os.environ.get(
            "GATEWAY_EMBEDDINGS_PATH",
            "/v1/orchestrate/gateway/model/embeddings",
        )
        self.chat_url = self.instance_url + (chat_path or default_chat_path)
        self.embeddings_url = self.instance_url + (
            embeddings_path or default_embeddings_path
        )

        self.gateway_provider = gateway_provider or os.environ.get(
            "GATEWAY_PROVIDER", "watsonx"
        )
        self.gateway_api_key_label = gateway_api_key_label or os.environ.get(
            "GATEWAY_API_KEY_LABEL", "gateway"
        )
        self.x_gateway_config_override = (
            x_gateway_config  # if set, we use it verbatim
        )

        self.payload_model_prefix = os.environ.get(
            "GATEWAY_MODEL_PREFIX", "watsonx/"
        )

        self.lock = Lock()

        # Token initialization
        if self._use_static_token:
            # Use the provided or env token as-is; no refresh
            self.token = static_token  # type: ignore[assignment]
            self.refresh_time = float("inf")
        else:
            # Original behavior: exchange to acquire token + refresh schedule
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
            inferred_cpd_auth_url = _infer_cpd_auth_url(self.instance_url)
            return "cpd", inferred_cpd_auth_url
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
        # No-op if using static token
        if self._use_static_token:
            return
        if time.time() > self.refresh_time:
            with self.lock:
                if time.time() > self.refresh_time:
                    self.token, self.refresh_time = self.get_token()

    def _auth_header(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}

    def _build_x_gateway_config(self, override_params: Dict[str, Any]) -> str:
        """
        Build x-gateway-config header JSON string.
        """
        if self.x_gateway_config_override:
            return json.dumps(self.x_gateway_config_override)

        config = {
            "strategy": {"mode": "single"},
            "targets": [
                {
                    "provider": self.gateway_provider,
                    "api_key": self.gateway_api_key_label,
                    "override_params": override_params or {},
                }
            ],
        }
        return json.dumps(config, separators=(",", ":"))

    def _headers(
        self, request_id: str, override_params: Dict[str, Any]
    ) -> Dict[str, str]:
        h = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "x-request-id": request_id,
            "x-gateway-config": self._build_x_gateway_config(override_params),
        }
        h.update(self._auth_header())
        return h

    def _payload_model_str(self, model_id: str) -> str:
        prefix = self.payload_model_prefix or ""
        # Check if prefix already provided
        return (
            model_id
            if (
                prefix
                and (
                    model_id.startswith(prefix)
                    or model_id.startswith("virtual-model")
                )
            )
            else f"{prefix}{model_id}"
        )

    def chat(
        self,
        messages: Sequence[Dict[str, str]],
        params: Optional[Dict[str, Any]] = None,
    ) -> ChatCompletions:
        """
        Returns ChatCompletions object.
        """
        if self.model_id is None:
            raise Exception("model id must be specified for chat")

        self.refresh_token_if_expires()

        merged_params = dict(self.params or {})
        if params:
            merged_params.update(params)
        chat_params = _translate_params_to_chat(merged_params)
        chat_params.pop("stream", None)

        override_params = dict(merged_params)
        override_params["model"] = self.model_id

        payload: Dict[str, Any] = {
            "model": self._payload_model_str(self.model_id),
            "messages": list(messages),
            **chat_params,
        }

        request_id = str(uuid.uuid4())
        headers = self._headers(request_id, override_params)

        last_user = next(
            (
                m.get("content", "")
                for m in reversed(messages)
                if m.get("role") == "user"
            ),
            "",
        )
        t0 = time.time()
        logger.debug(
            "[d][b]Sending gateway chat.completions request (non-streaming) | request_id=%s url=%s model=%s params=%s input_preview=%s",
            request_id,
            self.chat_url,
            self.model_id,
            json.dumps(chat_params, sort_keys=True, ensure_ascii=False),
            _truncate(last_user, 200),
        )

        resp = None
        try:
            resp = requests.post(
                self.chat_url,
                json=payload,
                headers=headers,
                verify=self._wo_ssl_verify,
                timeout=self.timeout,
            )
            duration_ms = int((time.time() - t0) * 1000)
            resp.raise_for_status()
            data = resp.json()

            choice = (data.get("choices") or [{}])[0]
            content = ""
            if isinstance(choice, dict):
                content = (
                    (choice.get("message", {}) or {}).get("content")
                    or choice.get("text")
                    or ""
                )
            finish_reason = (
                choice.get("finish_reason")
                if isinstance(choice, dict)
                else None
            )
            usage = data.get("usage", {})
            api_request_id = resp.headers.get(
                "x-request-id"
            ) or resp.headers.get("request-id")

            logger.debug(
                "[d][b]Gateway chat.completions response received (non-streaming) | request_id=%s status_code=%s duration_ms=%s finish_reason=%s usage=%s output_preview=%s api_request_id=%s",
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

        except Exception:
            duration_ms = int((time.time() - t0) * 1000)
            status_code = getattr(resp, "status_code", None)
            resp_text_preview = None
            try:
                if resp is not None:
                    resp_text_preview = _truncate(
                        getattr(resp, "text", None), 2000
                    )
            except Exception:
                pass

            logger.exception(
                "Gateway chat.completions request failed (non-streaming) | request_id=%s status_code=%s duration_ms=%s response_text_preview=%s",
                request_id,
                status_code,
                duration_ms,
                resp_text_preview,
            )
            # Only attempt re-auth if not in static-token mode
            if (status_code == 401) and (not self._use_static_token):
                with self.lock:
                    try:
                        self.token, self.refresh_time = self.get_token()
                    except Exception:
                        pass
            raise

    def encode(self, sentences: List[str]) -> List[list]:
        """
        Embeddings via gateway. Returns a list of vectors (list[float]) per input.
        """
        if self.embedding_model_id is None:
            raise Exception(
                "embedding model id must be specified for text encoding"
            )

        self.refresh_token_if_expires()

        override_params = {"model": self.embedding_model_id}
        request_id = str(uuid.uuid4())
        headers = self._headers(request_id, override_params)

        payload = {
            "input": sentences,
            "model": self._payload_model_str(self.embedding_model_id),
        }

        t0 = time.time()
        logger.debug(
            "[d][b]Sending gateway embeddings request | request_id=%s url=%s model=%s num_inputs=%s",
            request_id,
            self.embeddings_url,
            self.embedding_model_id,
            len(sentences),
        )

        resp = requests.post(
            self.embeddings_url,
            json=payload,
            headers=headers,
            verify=self._wo_ssl_verify,
            timeout=self.timeout,
        )
        duration_ms = int((time.time() - t0) * 1000)

        if resp.status_code != 200:
            logger.error(
                "[d b red]Gateway embeddings request failed | request_id=%s status_code=%s duration_ms=%s response_text_preview=%s",
                request_id,
                resp.status_code,
                duration_ms,
                _truncate(resp.text, 2000),
            )
            resp.raise_for_status()

        data = resp.json()

        if "data" in data and isinstance(data["data"], list) and data["data"]:
            vectors = [entry.get("embedding") for entry in data["data"]]
            logger.debug(
                "[d][b]Gateway embeddings response received | request_id=%s status_code=%s duration_ms=%s num_vectors=%s",
                request_id,
                resp.status_code,
                duration_ms,
                len(vectors),
            )
            return vectors

        # Fallback
        raise RuntimeError(
            f"Unexpected embeddings response: {json.dumps(data)[:500]}"
        )


if __name__ == "__main__":
    provider = GatewayProvider(
        model_id="meta-llama/llama-3-3-70b-instruct",
        system_prompt="Respond in Spanish only",
    )
    print(provider.query("Hello, how are you?"))
