import os
from enum import StrEnum

from pydantic import BaseModel, computed_field


class Platform(StrEnum):
    LANGFUSE = "langfuse"
    ARIZE = "arize"


class TelemetryPlatform(BaseModel):
    @computed_field
    @property
    def platform(self) -> str:
        platform = os.getenv("TELEMETRY_PLATFORM")
        if platform is None:
            raise ValueError("TELEMETRY_PLATFORM is not set")
        if platform not in Platform._value2member_map_:
            raise ValueError(
                f"Invalid platform: {platform}. The supported platforms are: {list(Platform)}"
            )

        return platform

    @computed_field
    @property
    def is_langfuse(self) -> bool:
        return self.platform == Platform.LANGFUSE

    @computed_field
    @property
    def is_arize(self) -> bool:
        return self.platform == Platform.ARIZE
