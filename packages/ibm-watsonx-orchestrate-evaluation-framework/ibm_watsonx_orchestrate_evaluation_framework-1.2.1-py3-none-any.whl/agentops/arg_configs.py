import os
from dataclasses import dataclass, field
from enum import StrEnum
from typing import List, Optional, Union

from agentops import __file__

DEFAULT_PROVIDER_VENDOR: str = "ibm"

root_dir = os.path.dirname(__file__)
LLAMA_USER_PROMPT_PATH = os.path.join(
    root_dir, "prompt", "llama_user_prompt.jinja2"
)
KEYWORDS_GENERATION_PROMPT_PATH = os.path.join(
    root_dir, "prompt", "keywords_generation_prompt.jinja2"
)


@dataclass
class AuthConfig:
    url: Optional[str] = None
    tenant_name: str = "local"
    token: str | None = None


@dataclass
class LLMUserConfig:
    model_id: str = field(default="meta-llama/llama-3-405b-instruct")
    prompt_config: str = field(default=LLAMA_USER_PROMPT_PATH)
    user_response_style: List[str] = field(default_factory=list)


@dataclass
class ProviderConfig:
    model_id: str = field(default="meta-llama/llama-3-405b-instruct")
    provider: str = field(
        default_factory=lambda: (
            "gateway"
            if os.getenv("USE_GATEWAY_MODEL_PROVIDER", "").lower() == "true"
            else "watsonx"
        )
    )
    embedding_model_id: str = field(
        default="sentence-transformers/all-minilm-l6-v2"
    )
    vendor: str = field(default=DEFAULT_PROVIDER_VENDOR)
    referenceless_eval: bool = field(default=False)


@dataclass
class CustomMetricsConfig:
    paths: Optional[list[str]] = field(default=None)
    llmaaj_config: ProviderConfig = field(default_factory=ProviderConfig)


@dataclass
class ExtractorsConfig:
    paths: Optional[list[str]] = field(default=None)


@dataclass
class ControllerConfig:
    enable_verbose_logging: bool = True
    enable_manual_user_input: bool = False


@dataclass
class TestConfig:
    test_paths: List[str]
    output_dir: str
    auth_config: AuthConfig
    wxo_lite_version: str
    provider_config: ProviderConfig = field(default_factory=ProviderConfig)
    llm_user_config: LLMUserConfig = field(default_factory=LLMUserConfig)
    custom_metrics_config: CustomMetricsConfig = field(
        default_factory=CustomMetricsConfig
    )
    extractors_config: ExtractorsConfig = field(
        default_factory=ExtractorsConfig
    )
    skip_available_results: bool = False
    data_annotation_run: bool = False
    num_workers: int = 2
    n_runs: int = 1
    enable_verbose_logging: bool = True
    enable_manual_user_input: bool = False
    similarity_threshold: float = 0.8
    enable_fuzzy_matching: bool = False
    is_strict: bool = True
    enable_recursive_search: bool = False
    tags: list[str] = field(default_factory=list)
    error_keywords: List[str] = field(default_factory=list)
    skip_legacy_evaluation: bool = (
        False  # Skip legacy evaluation and only run user/agent simulations
    )
    collection_name: str = "default-collection"
    operator_configs: dict = None
    metrics: list[str] = field(
        default_factory=lambda: [
            "JourneySuccessMetric",
            "ToolCalling",
            "OrchestrateAgentRoutingAccuracy",
        ]
    )


@dataclass
class AttackConfig:
    attack_paths: List[str]
    output_dir: str
    auth_config: AuthConfig
    provider_config: ProviderConfig = field(default_factory=ProviderConfig)
    llm_user_config: LLMUserConfig = field(default_factory=LLMUserConfig)
    enable_verbose_logging: bool = True
    enable_manual_user_input: bool = False
    num_workers: int = 2
    skip_available_results: bool = True


@dataclass
class AttackGeneratorConfig:
    attacks_list: Union[List[str], str]
    datasets_path: Union[List[str], str]
    agents_list_or_path: Union[List[str], str]
    target_agent_name: str
    auth_config: AuthConfig
    output_dir: str = None
    max_variants: int = None


class AnalyzeMode(StrEnum):
    default = "default"
    enhanced = "enhanced"


@dataclass
class AnalyzeConfig:
    data_path: str
    tool_definition_path: Optional[str] = None
    mode: str = AnalyzeMode.default
    num_workers: int = 10
    run: int = -1
    test_names: Optional[Union[str, List[str]]] = None
    test_pattern: Optional[str] = None
    agent_names: Optional[Union[str, List[str]]] = None


@dataclass
class KeywordsGenerationConfig:
    model_id: str = field(default="meta-llama/llama-3-405b-instruct")
    prompt_config: str = field(default=KEYWORDS_GENERATION_PROMPT_PATH)


@dataclass
class TestCaseGenerationConfig:
    log_path: str
    seed_data_path: str
    output_dir: str
    keywords_generation_config: KeywordsGenerationConfig = field(
        default_factory=KeywordsGenerationConfig
    )
    enable_verbose_logging: bool = True


@dataclass
class ChatRecordingConfig:
    output_dir: str
    keywords_generation_config: KeywordsGenerationConfig = field(
        default_factory=KeywordsGenerationConfig
    )
    service_url: str = "http://localhost:4321"
    tenant_name: str = "local"
    token: str = None
    max_retries: int = 5


@dataclass
class QuickEvalConfig(TestConfig):
    tools_path: str = None


@dataclass
class BatchAnnotateConfig:
    allowed_tools: List[str]
    tools_path: str
    stories_path: str
    output_dir: str
    num_variants: int = 2


@dataclass
class CompareRunsConfig:
    reference_file_location: str
    experiment_file_location: str
    csv_output_dir: Optional[str] = None
