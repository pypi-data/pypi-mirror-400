from typing import Optional

from pydantic import BaseModel, Field


class TestStat(BaseModel):
    """Object to keep track of test case stats per agent"""

    tests: int = 0
    tool_calls: int = 0
    kw_resp_match_count: int = 0
    story_chars: int = 0
    story_words: int = 0
    tools_seen: set = Field(default_factory=set)


class EnrichmentMetrics(BaseModel):
    """Enriched metrics in a coverage report"""

    untested_tools: set[str] = Field(default_factory=set)
    agent_tools: set[str] = Field(default_factory=set)
    tool_coverage: Optional[float] = None
    collaborator_metrics: dict[str, "EnrichmentMetrics"] = Field(
        default_factory=dict
    )
