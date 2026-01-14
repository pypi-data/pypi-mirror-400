import os
from functools import lru_cache

from agentops.arg_configs import AuthConfig
from agentops.service_provider import USE_GATEWAY_MODEL_PROVIDER
from agentops.wxo_client import get_wxo_client

WXO_AUTH_CONFIG_DEFAULTS = AuthConfig(
    url=os.getenv("WXO_URL", "http://localhost:4321"),
    tenant_name=os.getenv("WXO_TENANT", "wxo-dev"),
    token=os.getenv("WXO_TOKEN", None),
)


@lru_cache(maxsize=1)
def _get_cached_wxo_client():
    # TODO: remove this once the client is implemented as a Singleton.
    return get_wxo_client(
        WXO_AUTH_CONFIG_DEFAULTS.url,
        WXO_AUTH_CONFIG_DEFAULTS.tenant_name,
        WXO_AUTH_CONFIG_DEFAULTS.token,
    )


def get_provider_kwargs(**base_kwargs: dict) -> dict:

    if not USE_GATEWAY_MODEL_PROVIDER:
        return base_kwargs

    if "instance_url" in base_kwargs and "token" in base_kwargs:
        return base_kwargs

    wxo_client = _get_cached_wxo_client()

    return {
        **base_kwargs,
        "instance_url": wxo_client.service_url,
        "token": wxo_client.api_key,
    }
