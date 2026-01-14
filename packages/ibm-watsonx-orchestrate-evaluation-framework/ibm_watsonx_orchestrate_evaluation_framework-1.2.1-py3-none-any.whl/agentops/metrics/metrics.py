from collections import defaultdict
from enum import Enum, StrEnum
from typing import Any, Dict, List, Mapping, Optional, Tuple

from langfuse.api.resources.commons.types.score_data_type import ScoreDataType
from pydantic import BaseModel, computed_field
from pydantic.fields import Field

from agentops.metrics.llm_as_judge import AnswerRelevancy, Faithfulness
from agentops.type import ConversationalConfidenceThresholdScore, ErrorLog


class DescriptionQuality(StrEnum):
    GOOD = "GOOD"
    BAD = "BAD"
    MISSING = "MISSING"


class DescriptionQualityMetric(BaseModel):
    tool_name: str = None
    description_score: float | None = None
    threshold: float | None = None

    @computed_field
    @property
    def is_bad_description(self) -> Optional[bool]:
        if self.description_score and self.threshold:
            return self.description_score >= self.threshold

        return None

    @computed_field
    @property
    def description_quality(self) -> str:
        if self.description_score is None:
            return DescriptionQuality.MISSING
        elif self.is_bad_description:
            return DescriptionQuality.BAD
        else:
            return DescriptionQuality.GOOD


class KnowledgeBaseMetrics(BaseModel):
    dataset_name: str = None
    knowledge_base_name: str = (
        None  # in the message response body it is represented as "tool_name"
    )
    tool_call_id: str = None
    faithfulness: Faithfulness = None
    answer_relevancy: AnswerRelevancy = None
    confidence_scores: ConversationalConfidenceThresholdScore = None


class KnowledgeBaseMetricSummary(BaseModel):
    knowledge_base_metrics: List[List[KnowledgeBaseMetrics]]

    @computed_field(alias="detailed")
    @property
    def groupby_dataset(self) -> Mapping[str, Any]:
        groupby = {}
        for metric in self.knowledge_base_metrics:
            for row in metric:
                name = row.dataset_name
                tool_call_id = row.tool_call_id
                knowledge_base_name = row.knowledge_base_name
                faithfulness = row.faithfulness
                confidence_scores = row.confidence_scores
                answer_relevancy = row.answer_relevancy

                if name not in groupby:
                    groupby[name] = {
                        "knowledge_base_name": [knowledge_base_name],
                        "faithfulness": [faithfulness],
                        "confidence_scores": [confidence_scores],
                        "tool_call_id": [tool_call_id],
                        "answer_relevancy": [answer_relevancy],
                        "number_of_calls": 1,
                    }
                else:
                    values = groupby[name]
                    values.get("knowledge_base_name").append(
                        knowledge_base_name
                    )
                    values.get("faithfulness").append(faithfulness)
                    values.get("answer_relevancy").append(answer_relevancy)
                    values.get("confidence_scores").append(confidence_scores)
                    values.get("tool_call_id").append(tool_call_id)
                    values["number_of_calls"] += 1
                    groupby[name] = values

        return groupby

    @computed_field(alias="summary")
    @property
    def average(self) -> Mapping[str, Any]:
        from agentops.utils.utils import average

        summary = {}
        for dataset, metric in self.groupby_dataset.items():
            average_metric = {}
            average_metric["average_faithfulness"] = average(
                [
                    float(faithfulness.faithfulness_score)
                    for faithfulness in metric["faithfulness"]
                ]
            )
            average_metric["average_response_confidence"] = average(
                [
                    float(confidence_score.response_confidence)
                    for confidence_score in metric["confidence_scores"]
                ]
            )
            average_metric["average_retrieval_confidence"] = average(
                [
                    float(confidence_score.retrieval_confidence)
                    for confidence_score in metric["confidence_scores"]
                ]
            )
            average_metric["average_answer_relevancy"] = average(
                [
                    float(answer_relevancy.answer_relevancy_score)
                    for answer_relevancy in metric["answer_relevancy"]
                ]
            )
            average_metric["number_of_calls"] = metric["number_of_calls"]
            average_metric["knowledge_bases_called"] = ", ".join(
                set(metric["knowledge_base_name"])
            )
            summary[dataset] = average_metric

        return summary


class KeywordSemanticSearchMetric(BaseModel):
    keyword_match: bool
    semantic_match: bool
    message: str
    goal_detail: str


class TextMatchType(Enum):
    text_match = "Summary Matched"
    text_mismatch = "Summary MisMatched"
    na = "NA"


class ToolCallAndRoutingMetrics(BaseModel):
    dataset_name: str = ""
    total_steps: int = 0
    llm_step: int = 0
    total_tool_calls: int = 0
    expected_tool_calls: int = 0
    correct_tool_calls: int = 0
    relevant_tool_calls: int = (
        0  # calls with the same function but different args
    )
    total_routing_calls: int = 0
    relevant_routing_calls: int = 0
    tool_calls_with_incorrect_parameter: int = 0
    text_match: TextMatchType = TextMatchType.na
    is_success: bool = False
    avg_resp_time: float = -1

    @computed_field
    @property
    def tool_call_recall(self) -> float:
        return round(
            (
                self.correct_tool_calls / self.expected_tool_calls
                if self.expected_tool_calls > 0
                else 0.0
            ),
            2,
        )

    @computed_field
    @property
    def tool_call_precision(self) -> float:
        return round(
            (
                (self.correct_tool_calls) / self.total_tool_calls
                if self.total_tool_calls > 0
                else 0.0
            ),
            2,
        )

    @computed_field
    @property
    def agent_routing_accuracy(self) -> float:
        return round(
            (
                self.relevant_routing_calls / self.total_routing_calls
                if self.total_routing_calls > 0
                else 0.0
            ),
            2,
        )


class Annotation(BaseModel):
    recommendation: str
    details: str
    quote: str
    parameter_name: Optional[str]


class FailedStaticTestCases(BaseModel):
    metric_name: str
    description: str
    explanation: str


class FailedSemanticTestCases(BaseModel):
    metric_name: str
    evidence: str
    explanation: str
    output: int
    confidence: float
    annotations: Optional[List[Annotation]] = None


class EnhancedAnalyzeMetrics(BaseModel):
    test_case_name: str
    tool_names: List[str]
    parameter_annotations: List[List[FailedSemanticTestCases]] = [[]]
    tool_annotations: List[List[FailedSemanticTestCases]] = [[]]
    static_metrics: List[List[FailedStaticTestCases]] = [[]]


class ReferenceLessEvalMetrics(BaseModel):
    dataset_name: str
    number_of_tool_calls: int
    number_of_successful_tool_calls: int
    number_of_static_failed_tool_calls: int
    number_of_semantic_failed_tool_calls: int
    failed_static_tool_calls: Optional[
        List[Tuple[int, List[FailedStaticTestCases]]]
    ]
    failed_semantic_tool_calls: Optional[
        List[Tuple[int, List[FailedSemanticTestCases]]]
    ]


class Metric(BaseModel):
    """Generic metric result."""

    eval_name: str = Field(description="name of eval that produce metric")
    value: int | float | bool | str = Field(description="metric value")
    metadata: Optional[dict] = Field(
        default=None,
        description="metadata that was generated along side the metric. example: llmaaj reason, retrieval score",
    )


class EvaluatorData(Metric):
    comment: Optional[str] = ""

    @computed_field
    @property
    def data_type(self) -> ScoreDataType:
        if isinstance(self.value, bool):
            return ScoreDataType.BOOLEAN
        elif isinstance(self.value, int) or isinstance(self.value, float):
            return ScoreDataType.NUMERIC
        else:
            return ScoreDataType.CATEGORICAL


class CustomEvalMetrics(BaseModel):
    dataset_name: str
    custom_metrics: list[Metric]


class ExtractorData(BaseModel):
    field_name: str = Field(
        description="name of the computed field (ie. `correct_tool_calls`)"
    )
    value: Any = Field(description="value of the computed field")


def create_avg_row(metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create an average row from a list of metric dictionaries.

    Args:
        metrics: List of metric dictionaries

    Returns:
        Dictionary with averaged metrics
    """
    from agentops.utils.utils import safe_divide

    avg_row = {
        "Dataset": "Summary (Average)",
        "Runs": 0,
        "Total Steps": 0,
        "LLM Steps": 0,
        "Total Tool Calls": 0,
        "Tool Call Precision": 0,
        "Tool Call Recall": 0,
        "Agent Routing Accuracy": 0,
        "Text Match": 0,
        "Journey Success": 0,
        "Avg Resp Time (sec)": 0,
    }

    if metrics:
        for row in metrics:
            avg_row["Runs"] += row.get("Runs", 0)
            avg_row["Total Steps"] += row["Total Steps"]
            avg_row["LLM Steps"] += row["LLM Steps"]
            avg_row["Total Tool Calls"] += row["Total Tool Calls"]
            avg_row["Tool Call Precision"] += row["Tool Call Precision"]
            avg_row["Tool Call Recall"] += row["Tool Call Recall"]
            avg_row["Agent Routing Accuracy"] += row["Agent Routing Accuracy"]
            avg_row["Text Match"] += row["Text Match"]
            avg_row["Journey Success"] += row["Journey Success"]
            avg_row["Avg Resp Time (sec)"] += row["Avg Resp Time (sec)"]

        n = len(metrics)
        # Average over datasets
        avg_row["Runs"] = round(safe_divide(avg_row["Runs"], n), 2)
        avg_row["Total Steps"] = round(
            safe_divide(avg_row["Total Steps"], n), 2
        )
        avg_row["LLM Steps"] = round(safe_divide(avg_row["LLM Steps"], n), 2)
        avg_row["Total Tool Calls"] = round(
            safe_divide(avg_row["Total Tool Calls"], n), 2
        )
        avg_row["Tool Call Precision"] = round(
            safe_divide(avg_row["Tool Call Precision"], n), 2
        )
        avg_row["Tool Call Recall"] = round(
            safe_divide(avg_row["Tool Call Recall"], n), 2
        )
        avg_row["Agent Routing Accuracy"] = round(
            safe_divide(avg_row["Agent Routing Accuracy"], n), 2
        )
        avg_row["Text Match"] = round(safe_divide(avg_row["Text Match"], n), 2)
        avg_row["Journey Success"] = round(
            safe_divide(avg_row["Journey Success"], n), 2
        )
        avg_row["Avg Resp Time (sec)"] = round(
            safe_divide(avg_row["Avg Resp Time (sec)"], n), 2
        )

    return avg_row


def format_metrics_for_display(
    tool_call_metrics: list[ToolCallAndRoutingMetrics],
) -> list[dict[str, Any]]:
    from agentops.utils.utils import mean, safe_divide, to_pct

    # Group metrics by dataset name
    grouped = defaultdict(list)
    for m in tool_call_metrics:
        grouped[m.dataset_name].append(
            {
                "Dataset": m.dataset_name,
                "Total Steps": m.total_steps,
                "LLM Steps": m.llm_step,
                "Total Tool Calls": m.total_tool_calls,
                "Tool Call Precision": m.tool_call_precision,
                "Tool Call Recall": m.tool_call_recall,
                "Agent Routing Accuracy": m.agent_routing_accuracy,
                "Text Match": m.text_match,
                "Journey Success": m.is_success,
                "Avg Resp Time (sec)": m.avg_resp_time,
            }
        )

    # Create per-test rows with averages over runs
    per_test_rows = []
    for ds, rows in grouped.items():
        out = {"Dataset": ds}

        # Average numeric columns over runs
        numeric_keys = [
            "Total Steps",
            "LLM Steps",
            "Total Tool Calls",
            "Tool Call Precision",
            "Tool Call Recall",
            "Agent Routing Accuracy",
            "Avg Resp Time (sec)",
        ]

        for k in numeric_keys:
            out[k] = mean(
                [r[k] for r in rows if isinstance(r.get(k), (int, float))]
            )

        # Add total runs per dataset
        out["Runs"] = round(float(len(rows)), 2)

        # Journey Success -> numeric fraction in [0,1]
        js_vals = [1 if bool(r.get("Journey Success")) else 0 for r in rows]
        out["Journey Success"] = round(
            safe_divide(sum(js_vals), len(js_vals)), 2
        )

        # Text Match -> numeric fraction in [0,1]
        tm_hits = 0
        tm_den = len(rows)
        for r in rows:
            val = r.get("Text Match")
            if str(val).strip() == TextMatchType.text_match.value:
                tm_hits += 1
        out["Text Match"] = round(safe_divide(tm_hits, tm_den), 2)

        per_test_rows.append(out)

    # Create overall average row
    overall_row = create_avg_row(per_test_rows)

    # Format percentages
    tool_call_metrics_for_display = per_test_rows + [overall_row]
    for row in tool_call_metrics_for_display:
        row["Text Match"] = to_pct(row.get("Text Match"), decimals=0)
        row["Journey Success"] = to_pct(row.get("Journey Success"), decimals=0)

    column_order = [
        "Dataset",
        "Runs",
        "Total Steps",
        "LLM Steps",
        "Total Tool Calls",
        "Tool Call Precision",
        "Tool Call Recall",
        "Agent Routing Accuracy",
        "Text Match",
        "Journey Success",
        "Avg Resp Time (sec)",
    ]

    tool_call_metrics_for_display = [
        {col: row.get(col, "") for col in column_order}
        for row in tool_call_metrics_for_display
    ]

    return tool_call_metrics_for_display


def extract_metrics(
    results: List[
        Tuple[
            ToolCallAndRoutingMetrics,
            KnowledgeBaseMetricSummary,
            CustomEvalMetrics,
        ]
    ],
) -> tuple[
    list[ToolCallAndRoutingMetrics],
    KnowledgeBaseMetricSummary,
    List[CustomEvalMetrics],
]:
    """
    Aggregate metrics from test results.

    Args:
        results: List of tuples (metrics, knowledge_base_metrics, custom_metrics)

    Returns:
        Tuple of (knowledge_base_summary, tool_rows, custom_metrics)
    """

    tool_call_metrics = [metric[0] for metric in results]
    knowledge_base_metrics = [metric[1] for metric in results]
    custom_metrics: List[CustomEvalMetrics] = [metric[2] for metric in results]

    kb_summary = KnowledgeBaseMetricSummary(
        knowledge_base_metrics=knowledge_base_metrics
    )

    if len(tool_call_metrics) > 0:
        # Remove the average row if it exists
        tool_call_metrics = [
            row
            for row in tool_call_metrics
            if row.dataset_name != "Summary (Average)"
        ]

    return tool_call_metrics, kb_summary, custom_metrics


def extract_error_cases(
    results: List[
        Tuple[
            ToolCallAndRoutingMetrics,
            KnowledgeBaseMetricSummary,
            CustomEvalMetrics,
            Optional[ErrorLog],
        ]
    ],
) -> Tuple[
    List[
        Tuple[
            ToolCallAndRoutingMetrics,
            KnowledgeBaseMetricSummary,
            CustomEvalMetrics,
        ]
    ],
    List[ErrorLog],
]:
    """Filters valid results and extracts test cases that failed

    Args:
        results: a list of evaluation results

    Returns:
        a tuple containing a list of valid evaluation results and a list of error logs containing failed test cases
    """
    filtered_results = []
    errors = []
    for r in results:
        error_log = r[-1]
        if error_log != None:
            errors.append(error_log)
        else:
            filtered_results.append(r[0:3])

    return filtered_results, errors
