from collections.abc import Iterable
from enum import StrEnum

from rich.console import Console
from rich.table import Table
from tabulate import tabulate

from agentops.orchestrate_coverage.report_models import AgentCoverageReport

COVERAGE_CORE_METRICS = (
    "agent",
    "test_count",
    "tool_calls_avg",
    "kw_resp_match_count",
    "story_chars_avg",
    "story_words_avg",
)

COVERAGE_ENRICHED_METRICS = (
    "untested_tools",
    "declared_tools",
    "tool_coverage",
)

COVERAGE_ALL_METRICS = COVERAGE_CORE_METRICS + COVERAGE_ENRICHED_METRICS


class RenderType(StrEnum):
    dict = "dict"
    table = "table"
    rich_table = "rich_table"


def render_coverage(
    reports: Iterable[AgentCoverageReport],
    render_type: RenderType,
) -> str | dict:
    match render_type:
        case RenderType.dict:
            return to_dict(reports)
        case RenderType.table:
            return to_table(reports)
        case RenderType.rich_table:
            return to_rich_table(reports)
        case _:
            raise ValueError(f"Invalid render type: {render_type}")


def to_dict(reports: Iterable[AgentCoverageReport]) -> dict:
    """Render agent coverage report as a dictonary

    Args:
        reports: a list of agent coverage reports

    Returns:
        a dictionary mapping representing each agent's coverage report
    """
    result = {}
    for report in reports:
        result[report.agent.agent] = report.to_dict()
    return result


def to_table(reports: Iterable[AgentCoverageReport]) -> str:
    """Render agent coverage report as a tabulate table

    Args:
        reports: a list of agent coverage reports

    Returns:
        a table formatted string representing each agent's coverage report
    """
    has_enrichment = _has_enrichment(reports)

    table_headers = (
        COVERAGE_ALL_METRICS if has_enrichment else COVERAGE_CORE_METRICS
    )

    rows = [row for report in reports for row in report.to_rows()]
    return tabulate(rows, headers=table_headers)


def to_rich_table(reports: Iterable[AgentCoverageReport]) -> Table:
    """
    Render agent coverage report using Rich Table.

    Args:
        reports: a list of agent coverage reports

    Returns:
        a rich table instance representing each agent's coverage report
    """
    has_enrichment = _has_enrichment(reports)
    table_headers = (
        COVERAGE_ALL_METRICS if has_enrichment else COVERAGE_CORE_METRICS
    )

    # Create a rich table
    table = Table(show_header=True)
    for header in table_headers:
        table.add_column(header)

    # Add rows
    for report in reports:
        for row in report.to_rows():
            table.add_row(*[str(elem) for elem in row])

    return table


def _has_enrichment(reports: Iterable[AgentCoverageReport]) -> bool:
    return any([r.is_enriched for r in reports])
