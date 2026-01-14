from typing import Mapping

from agentops.collection.arize_collection import ArizeCollection
from agentops.collection.langfuse_collection import LangfuseCollection
from agentops.utils.telemetry_platform import TelemetryPlatform


def Collection(
    name: str, description: str = "", metadata: Mapping[str, str] = {}
):
    telemetry_platform = TelemetryPlatform()
    if telemetry_platform.is_langfuse:
        return LangfuseCollection(name, description, metadata)
    elif telemetry_platform.is_arize:
        return ArizeCollection(name, description, metadata)
    else:
        raise ValueError(
            f"Invalid telemetry platform: {telemetry_platform.platform}"
        )
