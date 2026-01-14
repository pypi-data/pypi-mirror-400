from enum import Enum, StrEnum
from hashlib import md5
from typing import Any, Dict, List, Literal, Mapping, Optional, Union

from langfuse._client.datasets import DatasetItemClient
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    model_validator,
)


class CallTracker(BaseModel):
    tool_call: List = []
    tool_response: List = []
    generic: List = []
    metadata: Dict[str, Any] = Field(default={})


class EventTypes(StrEnum):
    run_started = "run.started"
    run_step_delta = "run.step.delta"
    message_started = "message.started"
    message_delta = "message.delta"
    message_created = "message.created"
    run_completed = "run.completed"
    done = "done"


class ContentType(StrEnum):
    text = "text"
    tool_call = "tool_call"
    tool_response = "tool_response"
    conversational_search = "conversational_search"


class AttackCategory(StrEnum):
    on_policy = "on_policy"
    off_policy = "off_policy"


class Roles(Enum):
    ASSISTANT = "assistant"
    USER = "user"


class ConversationalSearchCitations(BaseModel):
    url: str
    body: str
    text: str
    title: str
    range_end: int
    range_start: int
    search_result_idx: int


class ConversationalSearchResultMetadata(BaseModel):
    score: float
    document_retrieval_source: str


class ConversationalSearchResults(BaseModel):
    url: str
    body: str
    title: str
    result_metadata: ConversationalSearchResultMetadata


class ConversationalConfidenceThresholdScore(BaseModel):
    response_confidence: float
    response_confidence_threshold: float
    retrieval_confidence: float
    retrieval_confidence_threshold: float

    def table(self):
        return {
            "response_confidence": str(self.response_confidence),
            "response_confidence_threshold": str(
                self.response_confidence_threshold
            ),
            "retrieval_confidence": str(self.retrieval_confidence),
            "retrieval_confidence_threshold": str(
                self.retrieval_confidence_threshold
            ),
        }


class ConversationSearchMetadata(BaseModel):
    """This class is used to store additional informational about the conversational search response that was not part of the API response.

    For example, the tool call that generated the conversational search response is not part of the API response. However,
    during evaluation, we want to refer to the tool that generated the conversational search response.
    """

    tool_call_id: str
    model_config = ConfigDict(frozen=True)


class ConversationalSearch(BaseModel):
    metadata: ConversationSearchMetadata
    response_type: str
    text: str  # same as `content` in Message. This field can be removed if neccesary
    citations: List[ConversationalSearchCitations]
    search_results: List[ConversationalSearchResults]
    citations_title: str
    confidence_scores: ConversationalConfidenceThresholdScore
    response_length_option: str


class Function(BaseModel):
    """OpenAI chat completion function structure for OTel parser tool calls"""

    name: str
    arguments: str  # JSON string of arguments

    model_config = ConfigDict(frozen=True)

    def __str__(self):
        return f"{self.name}:{self.arguments}"


class ToolCall(BaseModel):
    """OpenAI chat completion tool call structure for OTel parser"""

    id: str
    function: Function
    type: Literal["function"] = "function"

    model_config = ConfigDict(frozen=True)

    def __str__(self):
        return f"{self.id}:{self.type}:{self.function}"


class Message(BaseModel):
    """Message class with OpenAI-compatible tool call fields for compatibility
    with OpenTelemetry trace parsing (LangGraph, Pydantic AI, etc.)
    """

    role: str
    content: Union[str, Dict[str, Any]]
    type: ContentType = None
    # event that produced the message
    event: Optional[str] = None
    # used to correlate the Message with the retrieval context (ConversationalSearch)
    conversational_search_metadata: Optional[ConversationSearchMetadata] = None

    model_config = ConfigDict(frozen=True)

    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None

    def hash(self) -> str:
        """Generate hash for message deduplication"""
        parts = [
            self.role,
            str(self.content) if self.content else "",
            (
                ":".join(str(tc) for tc in self.tool_calls)
                if self.tool_calls
                else ""
            ),
            self.tool_call_id or "",
        ]
        return md5(":".join(parts).encode("utf-8")).hexdigest()


class ExtendedMessage(BaseModel):
    message: Message
    reason: dict | list | None = None


class KnowledgeBaseGoalDetail(BaseModel):
    enabled: bool = False
    metrics: list = []


class MatchingStrategy(StrEnum):
    """Argument matching strategy:\n
    Strict: exact match\n
    Optional: optional argument, exact match if the field exists\n
    Fuzzy: semantic/similarity match\n"""

    strict = "strict"
    optional = "optional"
    fuzzy = "fuzzy"


class GoalDetail(BaseModel):
    name: str
    tool_name: Optional[str] = None
    type: ContentType
    args: Optional[Dict] = None
    # matching strategy defaults to `strict` matching if not specified in the test case
    arg_matching: Optional[dict[str, MatchingStrategy]] = Field(
        default_factory=dict
    )
    response: Optional[str] = None
    keywords: Optional[List] = None

    @model_validator(mode="after")
    def validate_arg_matching(self):
        for field in self.arg_matching:
            if field not in self.args:
                raise ValueError(
                    f"{field} not in goal arguments for goal {self.name}"
                )
        return self


class GoalDetailOrchestrate(GoalDetail):
    knowledge_base: KnowledgeBaseGoalDetail = KnowledgeBaseGoalDetail()


class AttackData(BaseModel):
    attack_category: AttackCategory
    attack_type: str
    attack_name: str
    attack_instructions: str


class AttackData(BaseModel):
    agent: str
    agents_list_or_path: Union[List[str], str]
    attack_data: AttackData
    story: str
    starting_sentence: str
    goals: dict | None = None
    goal_details: list[GoalDetail] | None = None


class DatasetModelBase(BaseModel):
    starting_sentence: str | None = None
    story: str
    goals: Mapping[str, Any]
    goal_details: List[GoalDetail]
    max_user_turns: int | None = None
    agent: str | None = None


class DatasetModel(DatasetModelBase):
    @computed_field
    @property
    def input(self) -> Mapping[str, Any]:
        input = {
            "starting_sentence": self.starting_sentence,
            "story": self.story,
            "agent": self.agent,
        }

        return input

    @computed_field
    @property
    def output(self) -> Mapping[str, Any]:
        output = {"goals": self.goals, "goal_details": self.goal_details}

        return output


class OrchestrateDataset(DatasetModelBase):
    goal_details: List[GoalDetailOrchestrate]


class CollectionModel(BaseModel):
    collection_name: str
    datasets: List[DatasetModel]
    collection_description: Optional[str] = ""
    metadata: Optional[Mapping[str, str]] = None


class ToolDefinition(BaseModel):
    tool_description: Optional[str]
    tool_name: str
    tool_params: List[str]


class ProviderInstancesCacheKey(BaseModel):
    provider: str
    hashed_args: str
    hashed_kwargs: str

    def __str__(self) -> str:
        return f"{self.provider}|{self.hashed_args}|{self.hashed_kwargs}"


class RuntimeResponse(BaseModel):
    messages: List[Message]
    thread_id: str | None = None
    context: dict = Field(default={})


class ExperimentResult(BaseModel):
    experiment_name: str
    run_id: str
    experiment_id: str
    metrics: list
    session_ids: List[str]
    aggregate_metrics: List[List[Any]]


class Choice(BaseModel):
    message: Message
    finish_reason: str = None


class ChatCompletions(BaseModel):
    choices: List[Choice]
    id: str = None
    model: str = None


class ErrorLog(BaseModel):
    """Class to keep track of test cases that failed during execution"""

    test_case: str
    test_case_path: str
    reason: str
