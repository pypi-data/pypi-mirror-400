import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

from agentops.orchestrate_coverage.models import EnrichmentMetrics, TestStat
from agentops.orchestrate_coverage.report_models import (
    AgentCoverageReport,
    AgentCoverageRow,
    CollaboratorCoverageRow,
)
from agentops.resource_map import AgentData, ResourceMap
from agentops.scheduler import discover_tests
from agentops.type import ContentType, DatasetModelBase
from agentops.utils.file_system import FileType, list_all_files
from agentops.wxo_client import WXOClient

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def analyze_coverage(
    test_paths: list[str],
    output_dir: str | None = None,
    wxo_client: WXOClient | None = None,
    resource_map: ResourceMap | None = None,
    agent_paths: list[str] | None = None,
    show_collaborators: bool = False,
) -> list[AgentCoverageReport]:
    """
    Analyze test coverage for agents, including enrichment metrics if resource map is available.

    Args:
        test_paths: Paths to test case files or directories
        output_dir: Directory containing execution results (for observed tools)
        wxo_client: WXO client for building resource map if not provided
        resource_map: Pre-built resource map (optional, will be built if not provided)

    Returns:
        List of coverage metrics per agent
    """
    test_case_files = discover_tests(test_paths)
    resource_map = _ensure_resource_map(resource_map, wxo_client)

    offline_agent_data = _build_offline_data(agent_paths)
    agent_data = (
        resource_map.agent_data if resource_map else {} | offline_agent_data
    )

    # Analyze test definitions
    test_stats = _analyze_test_definitions(test_case_files)

    # Augment with observed tools from execution results
    observed_tools_by_agent = _collect_observed_tools(
        [] if output_dir is None else [output_dir],
        list(test_stats.keys()),
    )

    # Calculate coverage metrics
    reports = _calculate_coverage_metrics(
        test_stats, observed_tools_by_agent, agent_data, show_collaborators
    )

    reports.sort(key=lambda r: r.agent.agent)
    return reports


def _build_offline_data(agent_paths: list[str] | None) -> dict[str, AgentData]:
    """Build offline AgentData from agent definition files. Supports only YAML and JSON.

    Args:
        agent_paths: A list of paths to agent definition files

    Returns:
        A mapping of agent name to AgentData object
    """

    if not agent_paths:
        return {}
    agent_files = list_all_files(
        agent_paths, file_types=[FileType.JSON, FileType.YAML]
    )

    result = {}
    # Agent definition files can be YAML/JSON/PY files.
    for agent_file in agent_files:
        if agent_file.endswith(".json"):
            with open(agent_file, "r") as fp:
                content = json.load(fp)

        elif agent_file.endswith(".yaml"):
            with open(agent_file, "r") as fp:
                content = yaml.safe_load(fp)
        else:
            logger.warning(f"Extension not supported for {agent_file}")
            continue

        tools = content.get("tools", [])
        agent_name = content.get("name", "")
        result[agent_name] = AgentData(
            agent_name=agent_name,
            id="",
            tools=tools,
            collaborators=content.get("collaborators", []),
            is_manager=(len(tools) == 0),
        )
    return result


def _ensure_resource_map(
    resource_map: ResourceMap | None,
    wxo_client: WXOClient | None,
) -> ResourceMap | None:
    """Check if resource map exists. If not, attempt to retrieve it.

    Args:
        resource_map: any existing resource map object
        wxo_client: client to connect to wxo server

    Returns:
        A resource map object if it exists
    """
    if resource_map is not None:
        return resource_map

    if wxo_client is None:
        return None

    try:
        return ResourceMap(wxo_client)

    except Exception as e:
        logger.warning(
            f"Failed to build resource map for enrichment metrics: {e}. "
            "Enrichment metrics (declared_tools, untested_tools, tool_coverage) will not be available."
        )
        return None


def _analyze_test_definitions(files: list[str]) -> dict[str, TestStat]:
    """Parse and collect stats from test case files.

    Args:
        files: List of paths to test case files.

    Returns:
        A dictionary mapping each agent to its aggregated statistics.
    """
    per_agent: dict[str, TestStat] = defaultdict(TestStat)

    for file in files:
        if not file.endswith(".json") or file.endswith("agent.json"):
            continue

        tc = _load_test_case(file)
        if tc is None:
            continue

        agent_bucket = per_agent[tc.agent]
        agent_bucket.tests += 1

        tool_calls = 0
        has_kw_resp = False

        for gd in tc.goal_details:
            if gd.type == ContentType.tool_call:
                tool_calls += 1
                if gd.tool_name:
                    agent_bucket.tools_seen.add(gd.tool_name)
            elif gd.type == ContentType.text:
                if (
                    gd.response is not None and str(gd.response).strip() != ""
                ) and (isinstance(gd.keywords, list) and len(gd.keywords) > 0):
                    has_kw_resp = True

        agent_bucket.tool_calls += tool_calls
        agent_bucket.kw_resp_match_count += 1 if has_kw_resp else 0
        story = tc.story or ""
        agent_bucket.story_chars += len(story)
        agent_bucket.story_words += len(story.split())

    return per_agent


def _calculate_coverage_metrics(
    test_stats: dict[str, TestStat],
    observed_tools_by_agent: dict[str, set[str]],
    agent_data: dict[str, AgentData],
    show_collaborators: bool,
) -> list[AgentCoverageReport]:
    """Calculate and generate coverage metrics for each agent.

    Args:
        test_stats: A dictionary mapping each agent to its aggregated statistics.
        observed_tools_by_agent: A mapping of tools used in tests output by agent.
        agent_data: Resource data containing agent information, including tools and collaborator agents

    Returns:
        A list of objects representing coverage information for each agent.
    """
    reports: list[AgentCoverageReport] = []

    for agent, stats in test_stats.items():
        # Calculate basic averages
        tests = max(stats.tests, 1)
        tool_calls_avg = stats.tool_calls / tests
        avg_chars = stats.story_chars / tests
        avg_words = stats.story_words / tests

        # Calculate enrichment metrics if resource map available
        enrichment_result = _calculate_enrichment_metrics(
            agent, stats, observed_tools_by_agent, agent_data
        )

        coverage_row_data = {
            "agent": agent,
            "test_count": stats.tests,
            "tool_calls_avg": tool_calls_avg,
            "kw_resp_match_count": stats.kw_resp_match_count,
            "story_chars_avg": avg_chars,
            "story_words_avg": avg_words,
        }
        collab_rows = []
        if enrichment_result:
            coverage_row_data.update(
                {
                    "untested_tools_count": len(
                        enrichment_result.untested_tools
                    ),
                    "declared_tools": len(enrichment_result.agent_tools),
                    "tool_coverage": enrichment_result.tool_coverage,
                    "untested_tools": sorted(enrichment_result.untested_tools),
                }
            )
            agent_row = AgentCoverageRow(**coverage_row_data)
            if show_collaborators:
                for (
                    collab_agent,
                    metrics,
                ) in enrichment_result.collaborator_metrics.items():
                    collab_rows.append(
                        CollaboratorCoverageRow(
                            **{
                                "agent": collab_agent,
                                "untested_tools_count": len(
                                    metrics.untested_tools
                                ),
                                "declared_tools": len(metrics.agent_tools),
                                "tool_coverage": metrics.tool_coverage,
                                "untested_tools": sorted(
                                    metrics.untested_tools
                                ),
                            }
                        )
                    )
        else:
            agent_row = AgentCoverageRow(**coverage_row_data)
        reports.append(
            AgentCoverageReport(
                agent=agent_row,
                collaborators=collab_rows,
                is_enriched=(enrichment_result is not None),
            )
        )

    return reports


def _calculate_enrichment_metrics(
    agent_name: str,
    stats: TestStat,
    observed_tools_by_agent: dict[str, set[str]],
    agent_data: dict[str, AgentData],
) -> EnrichmentMetrics | None:
    """Calculates extra coverage metrics if resource map is available

    Args:
        agent_name: agent name
        stats: A dictionary mapping each agent to its aggregated statistics.
        observed_tools_by_agent: A mapping of tools used in tests output by agent.
        agent_data: Resource data containing agent information, including tools and collaborator agents

    Returns:
        An object containing enrichment metrics if available, else None.
    """
    if agent_data is None:
        logger.warning(
            "Resource map is None. Enrichment metrics unavailable. "
            "Check if wxo_client was provided and API calls succeeded."
        )
        return None

    if agent_name not in agent_data:
        logger.warning(f"Agent '{agent_name}' not found in resource map. ")
        return None

    # tools seen in test cases/output messages
    observed_tools = observed_tools_by_agent.get(agent_name) or set(
        stats.tools_seen
    )
    agent = agent_data[agent_name]

    result = EnrichmentMetrics()

    if agent.is_manager:
        # get all tools under its collaborator agents
        agent_tools = set(agent.tools)
        for collaborator in agent.collaborators:
            # Calculate coverage metrics for its collaborator agents
            if collaborator not in agent_data:
                continue
            collab_agent = agent_data[collaborator]
            collab_tools = set(collab_agent.tools)
            collab_metrics = EnrichmentMetrics(
                untested_tools=collab_tools - observed_tools,
                agent_tools=collab_tools,
                tool_coverage=len(collab_tools & observed_tools)
                / len(collab_tools),
            )
            agent_tools.update(collab_tools)
            result.collaborator_metrics[collab_agent.agent_name] = (
                collab_metrics
            )
    else:
        agent_tools = set(agent.tools)
    result.agent_tools = agent_tools

    # Calculate coverage metrics
    if len(agent_tools) > 0:
        result.untested_tools = agent_tools - observed_tools
        result.tool_coverage = len(agent_tools & observed_tools) / len(
            agent_tools
        )
    else:
        logger.warning(
            f"No tools found for agent '{agent.agent_name}' in resource map. "
        )
        return None

    return result


def _load_test_case(path: str) -> DatasetModelBase | None:
    """Loads a test case at the given path

    Args:
        path: path to the test case

    Returns:
        an DatasetModel object containing the test case if it was successfully loaded
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return DatasetModelBase.model_validate(json.load(f))

    except Exception as e:
        print(f"Error: unable to load test case {path} {e}")
        return None


def _collect_observed_tools(
    output_paths: list[str],
    known_agents: list[str],
) -> dict[str, set[str]]:
    observed: dict[str, set[str]] = defaultdict(set)

    if not output_paths:
        return observed

    results: list[tuple[str | None, set[str]]] = []

    for base in output_paths:
        base_path = Path(base)

        if not base_path.exists():
            continue

        for p in base_path.rglob("*.json"):
            result = _process_json_file(p)
            if result is not None:
                results.append(result)

    for agent_name, seen_tools in results:
        if agent_name is None:
            for a in known_agents:
                observed[a].update(seen_tools)
        else:
            observed[agent_name].update(seen_tools)

    return observed


def _extract_tool_name(tool: dict[str, Any]) -> str | None:
    fn = tool.get("function")
    if isinstance(fn, dict):
        name = fn.get("name")
        if isinstance(name, str) and name:
            return name
    name = tool.get("name")
    return name if isinstance(name, str) and name else None


def _extract_tools_from_message(msg: dict[str, Any]) -> set[str]:
    tools: set[str] = set()

    for tcalls_key in {"tool_calls", "toolCalls", "tools"}:
        tcalls = msg.get(tcalls_key)
        if isinstance(tcalls, list):
            for t in tcalls:
                if isinstance(t, dict):
                    name = _extract_tool_name(t)
                    if name:
                        tools.add(name)

    name = msg.get("name") or msg.get("tool_name")
    if isinstance(name, str) and name:
        tools.add(name)

    return tools


def _process_json_file(file_path: Path) -> tuple[str | None, set[str]] | None:
    """Extracts tools used in an evaluation output file

    Args:
        file_path: path to output file

    Returns:
        A tuple containing the agent name and the tools seen
    """
    # TODO szhang 11/05 this is intended to load evaluation output to collect a list of tools and agents. The processing function needs to be updated to parse messages correctly, currently it's unable to parse tools from evaluation output.
    try:
        with file_path.open("r", encoding="utf-8") as f:
            loaded_json = json.load(f)
    except Exception:
        return None

    candidates: list[dict[str, Any]] = []

    match loaded_json:
        case {"messages": list() as messages}:
            candidates = messages
        case {"history": list() as history}:
            candidates = history
        case list() as items:
            candidates = items
        case _:
            return None

    match loaded_json:
        case {"agent": str() as agent_name}:
            agent_name = agent_name
        case {"agent_name": str() as agent_name}:
            agent_name = agent_name
        case _:
            agent_name = None

    seen_tools: set[str] = set()

    for msg in candidates:
        if not isinstance(msg, dict):
            continue

        seen_tools.update(_extract_tools_from_message(msg))

    if not seen_tools:
        return None

    return (agent_name, seen_tools)
