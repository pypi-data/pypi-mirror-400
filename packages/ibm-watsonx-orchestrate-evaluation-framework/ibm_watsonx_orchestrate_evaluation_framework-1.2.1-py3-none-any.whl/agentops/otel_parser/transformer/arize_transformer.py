import json
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import pandas as pd
from opentelemetry.sdk.trace import ReadableSpan

from agentops.otel_parser.common import ObsNode

TYPE_MAPPING = {
    "LLM": "GENERATION",
    "CHAIN": "CHAIN",
    "TOOL": "TOOL",
    "AGENT": "CHAIN",
    "RETRIEVER": "SPAN",
    "EMBEDDING": "SPAN",
}


@dataclass
class ArizeSpan:
    """Wrapper to make Arize DataFrame rows look like Langfuse observations."""

    id: str
    parent_observation_id: Optional[str]
    name: str
    type: str  # LLM, CHAIN, TOOL, etc.
    start_time: Any
    end_time: Any
    input: Optional[Dict]
    output: Optional[Dict]
    metadata: Dict

    @staticmethod
    def parse(input: Any) -> Optional[Dict]:
        if pd.notna(input):
            try:
                return json.loads(input)
            except (json.JSONDecodeError, TypeError):
                return input
        return None

    @classmethod
    def from_row(cls, row: pd.Series) -> "ArizeSpan":
        """Convert a flat Arize DataFrame row to an ArizeSpan object."""
        # Parse JSON fields
        input_val = ArizeSpan.parse(row.get("attributes.input.value"))
        output_val = ArizeSpan.parse(row.get("attributes.output.value"))
        metadata = ArizeSpan.parse(row.get("attributes.metadata")) or {}

        # Map OpenInference span.kind to Langfuse observation type
        span_kind = row.get("attributes.openinference.span.kind", "")
        obs_type = TYPE_MAPPING.get(span_kind, "SPAN")

        return cls(
            id=row["context.span_id"],
            parent_observation_id=(row.get("parent_id")),
            name=row.get("name", ""),
            type=obs_type,
            start_time=row.get("start_time"),
            end_time=row.get("end_time"),
            input=input_val,
            output=output_val,
            metadata=metadata,
        )


def build_observation_forest_from_df(df: pd.DataFrame) -> List[ObsNode]:
    """
    Transform flat Arize DataFrame to nested ObsNode tree structure.
    Returns list of root nodes; each has .children forming a tree.
    """
    nodes: Dict[str, ObsNode] = {}
    children_by_parent: Dict[Optional[str], List[ObsNode]] = defaultdict(list)

    # 1. Create nodes for each row
    for _, row in df.iterrows():
        span = ArizeSpan.from_row(row)
        node = ObsNode(span)
        nodes[span.id] = node
        # adjaceny list to map parent_observation_id to children
        children_by_parent[span.parent_observation_id].append(node)

    # 2. Attach children to parents
    for parent_id, child_nodes in children_by_parent.items():
        if parent_id is None:
            continue

        parent_node = nodes.get(parent_id)
        if parent_node:
            parent_node.children.extend(child_nodes)
            for child_node in child_nodes:
                child_node.parent = parent_node

    # 3. Roots are those with parent_observation_id == None OR
    #  whose parent_id is not in our dataset (e.g., Arize's run_task wrapper)
    roots = children_by_parent[None].copy()

    for parent_id, child_nodes in children_by_parent.items():
        if parent_id is not None and parent_id not in nodes:
            # This parent (e.g., run_task) is not in our dataset
            roots.extend(child_nodes)

    return roots


def group_by_trace(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Group DataFrame rows by trace_id."""
    return {
        trace_id: group
        for trace_id, group in df.groupby("context.trace_id", sort=False)
    }


def _ensure_dict_with_string_keys(value: Any) -> dict:
    """
    Ensure a value is a dictionary with string keys.
    Arize requires metadata columns to be dicts with string keys.
    """
    if value is None:
        return {}

    if isinstance(value, str):
        # Try to parse JSON string
        try:
            parsed = json.loads(value)
            if isinstance(parsed, dict):
                return {str(k): v for k, v in parsed.items()}
            return {}
        except (json.JSONDecodeError, TypeError):
            return {}

    if isinstance(value, dict):
        # Ensure all keys are strings
        return {str(k): v for k, v in value.items()}

    return {}


def spans_to_arize_df(spans: List[ReadableSpan]) -> pd.DataFrame:
    """
    Convert InMemorySpanExporter spans to the flat Arize DataFrame format
    that ArizeSpan.from_row() expects.
    """
    rows = []
    for span in spans:
        attrs = dict(span.attributes) if span.attributes else {}

        # Ensure metadata is a proper dict with string keys (Arize requirement)
        metadata = _ensure_dict_with_string_keys(attrs.get("metadata"))

        row = {
            # Core identifiers (matching Arize export format)
            "context.span_id": format(span.context.span_id, "016x"),
            "context.trace_id": format(span.context.trace_id, "032x"),
            "parent_id": (
                format(span.parent.span_id, "016x") if span.parent else None
            ),
            # Timing
            "name": span.name,
            "start_time": span.start_time,
            "end_time": span.end_time,
            # Status
            "status_code": (
                span.status.status_code.name if span.status else None
            ),
            # Flatten attributes with "attributes." prefix (Arize format)
            "attributes.input.value": attrs.get("input.value"),
            "attributes.output.value": attrs.get("output.value"),
            "attributes.openinference.span.kind": attrs.get(
                "openinference.span.kind"
            ),
            "attributes.metadata": metadata,
            # LLM-specific attributes
            "attributes.llm.input_messages": attrs.get("llm.input_messages"),
            "attributes.llm.output_messages": attrs.get("llm.output_messages"),
            "attributes.llm.model_name": attrs.get("llm.model_name"),
            "attributes.llm.token_count.prompt": attrs.get(
                "llm.token_count.prompt"
            ),
            "attributes.llm.token_count.completion": attrs.get(
                "llm.token_count.completion"
            ),
            # Tool attributes
            "attributes.tool.name": attrs.get("tool.name"),
            "attributes.tool.parameters": attrs.get("tool.parameters"),
        }

        # Also include ALL other attributes with the prefix
        for key, value in attrs.items():
            col_name = f"attributes.{key}"
            if col_name not in row:
                row[col_name] = value

        rows.append(row)

    return pd.DataFrame(rows)
