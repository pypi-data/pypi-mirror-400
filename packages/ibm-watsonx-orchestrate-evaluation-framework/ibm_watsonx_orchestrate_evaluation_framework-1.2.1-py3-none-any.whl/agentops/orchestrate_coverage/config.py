from dataclasses import dataclass, field

from agentops.arg_configs import AuthConfig


@dataclass
class CoverageConfig:
    test_paths: list[str]
    output_dir: str | None = None
    auth_config: AuthConfig | None = None
    agent_paths: list[str] = field(default_factory=list)
    show_collaborators: bool = False
