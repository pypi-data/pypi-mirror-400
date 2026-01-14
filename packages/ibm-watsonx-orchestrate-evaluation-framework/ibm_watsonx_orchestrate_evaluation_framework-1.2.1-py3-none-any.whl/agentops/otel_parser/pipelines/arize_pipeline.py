from typing import List

import pandas as pd

from agentops.otel_parser import langgraph_parser
from agentops.otel_parser.common import dfs_
from agentops.otel_parser.transformer.arize_transformer import (
    build_observation_forest_from_df,
    group_by_trace,
)
from agentops.type import Message
from agentops.utils.rich_utils import RichLogger

logger = RichLogger(__name__)


class ArizePipeline:
    @staticmethod
    def langgraph_pipeline(
        spans_df: pd.DataFrame, session_ids: List[str]
    ) -> List[Message]:
        """
        Pipeline to parse Langgraph observations from Arize spans DataFrame.

        Args:
            spans_df: DataFrame containing Arize spans data.

        Returns:
            List of parsed messages.
        """

        # Sort the spans_df by session_ids so we reconstruct the conversation in the correct order
        spans_df = spans_df.sort_values(
            "attributes.session.id",
            key=lambda x: x.map({v: i for i, v in enumerate(session_ids)}),
        )

        all_messages = []
        trace_groups = group_by_trace(spans_df)

        for trace_id, trace_df in trace_groups.items():
            seen = set()
            messages = []
            # Sort by start_time
            logger.info(f"Sorting trace {trace_id} by start_time")
            trace_df = trace_df.sort_values("start_time")

            # Build nested tree structure
            observation_tree = build_observation_forest_from_df(trace_df)

            # Use existing parser (same as Langfuse path)
            parsed_messages = langgraph_parser.parse_observations(
                observation_tree
            )
            for msg in parsed_messages:
                if msg.hash() in seen:
                    continue
                seen.add(msg.hash())
                messages.append(msg)

            all_messages.append(messages)

        return all_messages
