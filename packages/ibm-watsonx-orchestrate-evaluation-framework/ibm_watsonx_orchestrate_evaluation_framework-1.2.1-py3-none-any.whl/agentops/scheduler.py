import glob
import json
import os
import re
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from enum import unique
from pathlib import Path
from typing import Any, Callable, Dict, List, Set, Tuple

from rich import print as rich_print
from rich.progress import Progress

from agentops.arg_configs import TestConfig
from agentops.clients import Clients
from agentops.service_provider import LOGGING_ENABLED
from agentops.utils.rich_utils import pretty_print, warn


def discover_tests(
    test_paths: List[str], recursive_search: bool = False
) -> List[str]:
    """
    Discover test cases from the given test paths.

    This function searches for JSON test case files in the provided paths.
    When recursive_search is enabled, it will search through all subdirectories
    recursively. Otherwise, it will only search the top level of each directory.

    Args:
        test_paths: List of paths to search for test cases
        recursive_search: Whether to search recursively in subdirectories

    Returns:
        List of unique test case names
    """
    test_cases = []
    for test_path in test_paths:
        # Check if the path exists
        if not glob.glob(test_path):
            rich_print(
                f"[bold yellow]Warning: Path '{test_path}' does not exist. Skipping.[/bold yellow]"
            )
            continue

        if os.path.isdir(test_path):
            if recursive_search:
                # Use ** pattern for recursive search
                pattern = os.path.join(test_path, "**", "*.json")
                found_files = sorted(glob.glob(pattern, recursive=True))
                rich_print(
                    f"Found {len(found_files)} files in '{test_path}' (recursive search)"
                )
                test_cases.extend(found_files)
            else:
                # Original behavior for non-recursive search
                pattern = os.path.join(test_path, "*.json")
                found_files = sorted(glob.glob(pattern))
                rich_print(
                    f"Found {len(found_files)} files in '{test_path}' (non-recursive)"
                )
                test_cases.extend(found_files)
        else:
            # If it's a file pattern, just use it directly
            found_files = sorted(glob.glob(test_path))
            test_cases.extend(found_files)

    # Filter out non-JSON files and agent.json files
    filtered_cases = [
        tc
        for tc in test_cases
        if tc.endswith(".json") and not tc.endswith("agent.json")
    ]

    # create mapping of test case name to file path
    unique_files_map: dict[str, str] = {}

    for f in filtered_cases:
        name = Path(f).stem
        if name not in unique_files_map:
            unique_files_map[name] = f
        else:
            rich_print(
                f"[bold red]Duplicate test case name detected:[/bold red] "
                f"'{name}' (skipping file '{f}')"
            )

    unique_files = list(unique_files_map.values())
    rich_print(
        f"[bold green]Discovered {len(unique_files)} test cases in total[/bold green]"
    )
    return unique_files


def filter_tests(test_cases: List[str], config_tags: List[str]) -> List[str]:
    """
    Given a set of test cases and a user-passed tag, filter only on test cases that have said tag.

    Args:
        test_cases: List of paths to search for test cases
        tags: List of tags to filter by

    Returns:
        filtered_test_cases
    """
    # If no tags specified just return the original test cases
    if not config_tags:
        return test_cases

    config_tags_set = set(config_tags)
    pretty_print(
        f"Filtering test cases by tags: {', '.join(config_tags)}",
        style="bold blue",
    )
    filtered_test_cases = []
    for test_case_path in test_cases:
        try:
            # Read and parse the test case JSON file
            with open(test_case_path, "r") as f:
                test_data = json.load(f)

            test_case_tags = test_data.get("tags", [])
            # Only add tags that are also in config_tags
            matching_tags = [
                tag for tag in test_case_tags if tag in config_tags_set
            ]
            if matching_tags:
                filtered_test_cases.append(test_case_path)

        except (json.JSONDecodeError, FileNotFoundError):
            # Skip files that can't be read or aren't valid JSON
            pretty_print(
                warn(
                    message=f"Skipping the following test case because of a parsing issue: {test_case_path}"
                )
            )

    return filtered_test_cases


def _removesuffix(s: str, suf: str) -> str:
    """Remove suffix from string (for Python < 3.9 compatibility)"""
    return s[: -len(suf)] if s.endswith(suf) else s


def get_available_runs(output_dir: str) -> Dict[str, Set[int]]:
    """
    Get available runs from the output directory.

    Args:
        output_dir: Output directory path

    Returns:
        Dictionary mapping test case stems to sets of run numbers
    """
    available_runs = defaultdict(set)
    for f in glob.glob(os.path.join(output_dir, "messages", "*.messages.json")):
        # strip the fixed tail
        name = _removesuffix(os.path.basename(f), ".messages.json")
        # match either "<stem>" (single run) OR "<stem>.runN" (multi-run)
        m = re.match(r"^(?P<stem>.+?)(?:\.run(?P<run>\d+))?$", name)
        if not m:
            continue
        stem = m.group("stem")
        run_num = int(m.group("run") or 1)  # no suffix ⇒ run 1
        available_runs[stem].add(run_num)

    return available_runs


def enumerate_jobs(
    test_cases: List[str],
    n_runs: int,
    skip_available_results: bool,
    output_dir: str,
) -> List[Tuple[int, str, int]]:
    """
    Enumerate jobs to be run.

    Args:
        test_cases: List of test case file paths
        n_runs: Number of runs per test case
        skip_available_results: Whether to skip available results
        output_dir: Output directory path

    Returns:
        List of tuples (task_n, test_case, run_idx)
    """
    jobs = []
    task_n = 0

    available_runs = (
        get_available_runs(output_dir) if skip_available_results else {}
    )

    for test_case in test_cases:
        stem = Path(test_case).stem

        for run_idx in range(n_runs):
            run_number = run_idx + 1

            # Skip precisely this (test, run) if results exist
            if skip_available_results and (
                run_number in available_runs.get(stem, set())
            ):
                print(
                    f"Skipping {stem} run {run_number} as results already exist."
                )
                continue

            jobs.append((task_n, test_case, run_idx))
            task_n += 1

    return jobs


def run_jobs(
    jobs: List[Tuple[int, str, int]],
    config: TestConfig,
    clients: Clients,
    process_func: Callable,
    num_workers: int,
) -> List[Any]:
    """
    Run jobs using ThreadPoolExecutor.

    Args:
        jobs: List of jobs to run
        config: Test configuration
        clients: Tuple of clients (wxo_client, llmaaj_provider, resource_map, inference_backend, llm_user)
        process_func: Function to process each job
        num_workers: Number of worker threads

    Returns:
        List of results from all jobs
    """

    if config.num_workers > 1 and config.enable_manual_user_input:
        rich_print(
            "[bold yellow]Warning ⚠️: Manual user input is disabled for parallel execution.[/bold yellow]"
        )
        config.enable_manual_user_input = (
            False  # disable manual user input for parallel execution
        )

    executor = ThreadPoolExecutor(max_workers=num_workers)
    futures = []

    for task_n, test_case, run_idx in jobs:
        future = executor.submit(
            process_func,
            task_n,
            test_case,
            config,
            clients.inference_backend,
            clients.resource_map,
            clients.llm_user,
            clients.llmaaj_provider,
            run_idx,
        )
        futures.append(((test_case, run_idx), future))

    results = []

    if futures:
        if LOGGING_ENABLED:
            # No progress bar when logging - just process tasks
            for (test_case, run_idx), future in futures:
                try:
                    results.extend(future.result())
                except Exception as e:
                    import traceback

                    rich_print(f"test case {test_case} fails with {e}")

                    traceback.print_exc()
        else:
            with Progress() as progress:
                task1 = progress.add_task(
                    f"[purple]Evaluating {len(futures)} tasks...",
                    total=len(futures),
                )
                for (test_case, run_idx), future in futures:
                    try:
                        results.extend(future.result())
                    except Exception as e:
                        import traceback

                        rich_print(f"test case {test_case} fails with {e}")

                        traceback.print_exc()
                    finally:
                        progress.update(task1, advance=1)

    return results
