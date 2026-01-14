import logging
import os

from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler

from agentops.arg_configs import DEFAULT_PROVIDER_VENDOR, ProviderConfig
from agentops.service_provider.gateway_provider import GatewayProvider
from agentops.service_provider.model_proxy_provider import ModelProxyProvider
from agentops.service_provider.ollama_provider import OllamaProvider
from agentops.service_provider.portkey_provider import PortkeyProvider
from agentops.service_provider.referenceless_provider_wrapper import (
    GatewayProviderLLMKitWrapper,
    ModelProxyProviderLLMKitWrapper,
    WatsonXLLMKitWrapper,
)
from agentops.service_provider.watsonx_provider import WatsonXProvider

try:
    from agentops.service_provider.portkey_provider import PortkeyProvider
except:
    pass


load_dotenv()

USE_GATEWAY_MODEL_PROVIDER: bool = (
    os.environ.get("USE_GATEWAY_MODEL_PROVIDER", "FALSE").upper() == "TRUE"
)

_logging_console = Console(stderr=True)

logger = logging.getLogger(__name__)


def get_log_level_from_env():

    level_env = os.getenv("WXO_EVALUATION_LOGLEVEL")
    return level_env


LOGGING_ENABLED = get_log_level_from_env() is not None


def configure_logging_for_package_from_env(
    package_name: str = "agentops",
    ensure_output: bool = True,
) -> None:
    """
    Configure logging using the env var WXO_EVALUATION_LOGLEVEL - no logging if that's not set
    """
    try:
        level_env = get_log_level_from_env()
        if not level_env:
            return

        level = None
        upper = level_env.strip().upper()
        if hasattr(logging, upper):
            level = getattr(logging, upper, None)

        pkg_logger = logging.getLogger(package_name)
        pkg_logger.setLevel(level)

        if ensure_output:
            if not pkg_logger.handlers:
                handler = RichHandler(
                    console=_logging_console,
                    rich_tracebacks=True,
                    show_time=False,
                    show_level=False,
                    show_path=False,
                    markup=True,
                    enable_link_path=True,
                    omit_repeated_times=True,
                    tracebacks_theme="github-dark",
                )
                handler.setFormatter(
                    logging.Formatter("%(levelname)s %(message)s")
                )
                handler.setLevel(logging.NOTSET)
                pkg_logger.addHandler(handler)
            pkg_logger.propagate = False

        # Quiet common noisy debug libs
        for name in (
            "urllib3",
            "urllib3.connectionpool",
            "requests.packages.urllib3",
        ):
            logging.getLogger(name).setLevel(logging.WARNING)
    except:
        logger.warning("Input log level %s not valid", level_env)


configure_logging_for_package_from_env()


def _instantiate_provider(config: ProviderConfig, **kwargs):

    if config.provider == "watsonx":
        logger.info("Instantiate watsonx provider")
        if config.referenceless_eval:
            provider = WatsonXLLMKitWrapper
        else:
            provider = WatsonXProvider
        return provider(
            model_id=config.model_id,
            embedding_model_id=config.embedding_model_id,
            **kwargs,
        )
    elif config.provider == "ollama":
        logger.info("Instantiate Ollama")
        return OllamaProvider(model_id=config.model_id, **kwargs)

    elif config.provider == "gateway":
        logger.info("Instantiate gateway inference provider")
        if config.referenceless_eval:
            provider = GatewayProviderLLMKitWrapper
        else:
            provider = GatewayProvider
        return provider(
            model_id=config.model_id,
            embedding_model_id=config.embedding_model_id,
            **kwargs,
        )

    elif config.provider == "model_proxy":
        logger.info("Instantiate model proxy provider")
        if config.referenceless_eval:
            provider = ModelProxyProviderLLMKitWrapper
        else:
            provider = ModelProxyProvider

        return provider(
            model_id=config.model_id,
            embedding_model_id=config.embedding_model_id,
            **kwargs,
        )
    elif config.provider == "portkey":
        logger.info("Instantiate portkey provider")
        return PortkeyProvider(
            model_id=config.model_id,
            vendor=config.vendor,
            **kwargs,
        )

    else:
        raise RuntimeError(
            f"target provider is not supported {config.provider}"
        )


def get_provider(
    config: ProviderConfig = None,
    model_id: str = None,
    embedding_model_id: str = None,
    vendor: str = DEFAULT_PROVIDER_VENDOR,
    referenceless_eval: bool = False,
    **kwargs,
):

    if config:
        return _instantiate_provider(config, **kwargs)

    if not model_id:
        raise ValueError("model_id must be provided if config is not supplied")

    if USE_GATEWAY_MODEL_PROVIDER:
        logger.info("[d b]Using gateway inference provider override")
        config = ProviderConfig(
            provider="gateway",
            model_id=model_id,
            referenceless_eval=referenceless_eval,
        )
        return _instantiate_provider(config, **kwargs)

    if vendor != DEFAULT_PROVIDER_VENDOR:
        logger.info(
            "[d b]Using portkey inference provider with vendor %s", vendor
        )
        config = ProviderConfig(
            provider="portkey", model_id=model_id, vendor=vendor
        )
        return _instantiate_provider(config, **kwargs)

    if "WATSONX_APIKEY" in os.environ and "WATSONX_SPACE_ID" in os.environ:
        logger.info("[d b]Using watsonx inference provider")
        config = ProviderConfig(
            provider="watsonx",
            model_id=model_id,
            embedding_model_id=embedding_model_id,
            referenceless_eval=referenceless_eval,
        )
        return _instantiate_provider(config, **kwargs)

    if "WO_INSTANCE" in os.environ:
        logger.info("[d b]Using model_proxy inference provider")
        config = ProviderConfig(
            provider="model_proxy",
            model_id=model_id,
            referenceless_eval=referenceless_eval,
        )
        return _instantiate_provider(config, **kwargs)

    logger.info("[d b]Using gateway inference provider default")
    config = ProviderConfig(
        provider="gateway",
        model_id=model_id,
        referenceless_eval=referenceless_eval,
    )
    return _instantiate_provider(config, **kwargs)
