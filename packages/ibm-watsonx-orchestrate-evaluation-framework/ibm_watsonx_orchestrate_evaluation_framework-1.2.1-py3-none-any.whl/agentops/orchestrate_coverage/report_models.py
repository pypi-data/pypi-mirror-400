from typing import Optional

from pydantic import BaseModel


class CollaboratorCoverageRow(BaseModel):
    """Coverage report row with enrichment metrics for a collaborator agent"""

    agent: str
    untested_tools_count: int
    declared_tools: int
    tool_coverage: float
    untested_tools: list[str]

    def to_row(self):
        base = [f"└──{self.agent}"] + [""] * 5

        base += [
            self.untested_tools_count,
            self.declared_tools,
            f"{self.tool_coverage * 100:.2f}%",
        ]
        return base


class AgentCoverageRow(BaseModel):
    """Coverage report row for an agent"""

    agent: str
    test_count: int
    tool_calls_avg: float
    kw_resp_match_count: int
    story_chars_avg: float
    story_words_avg: float
    untested_tools_count: Optional[int] = None
    declared_tools: Optional[int] = None
    tool_coverage: Optional[float] = None
    untested_tools: Optional[list[str]] = None

    def to_row(self) -> list[str]:
        """Convert to a list with relevant fields

        Returns:
            _description_
        """
        base = [
            self.agent,
            self.test_count,
            f"{self.tool_calls_avg:.2f}",
            self.kw_resp_match_count,
            f"{self.story_chars_avg:.1f}",
            f"{self.story_words_avg:.1f}",
        ]

        if (
            self.untested_tools_count is not None
            and self.declared_tools is not None
            and self.tool_coverage is not None
        ):
            base += [
                self.untested_tools_count,
                self.declared_tools,
                f"{self.tool_coverage * 100:.2f}%",
            ]
        return base


class AgentCoverageReport(BaseModel):
    agent: AgentCoverageRow
    collaborators: list[CollaboratorCoverageRow]
    is_enriched: bool

    def to_rows(self) -> list[list[str]]:
        """Convert the report into a list of rows (agent + collaborators).

        Returns:
            A list of rows
        """
        return [self.agent.to_row()] + [r.to_row() for r in self.collaborators]

    def to_dict(self) -> dict:
        """Convert the report to a dictionary, excluding `is_enriched` field and empty fields."""
        return self.model_dump(exclude={"is_enriched"}, exclude_none=True)
