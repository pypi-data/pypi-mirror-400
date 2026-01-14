import json
from pathlib import Path

from jsonargparse import CLI
from rich import print as rich_print

from agentops.orchestrate_coverage import (
    RenderType,
    analyze_coverage,
    render_coverage,
)
from agentops.orchestrate_coverage.config import CoverageConfig
from agentops.wxo_client import get_wxo_client


def main(config: CoverageConfig) -> None:
    wxo_client = None
    if config.auth_config is not None:
        wxo_client = get_wxo_client(
            config.auth_config.url,
            config.auth_config.tenant_name,
            config.auth_config.token,
        )

    reports = analyze_coverage(
        test_paths=config.test_paths,
        output_dir=config.output_dir,
        wxo_client=wxo_client,
        agent_paths=config.agent_paths,
        show_collaborators=config.show_collaborators,
    )

    table_representation = render_coverage(reports, RenderType.table)
    print(table_representation)
    table_representation = render_coverage(reports, RenderType.rich_table)
    rich_print(table_representation)

    coverage_dict = render_coverage(reports, RenderType.dict)
    output_dir = Path(config.output_dir or "")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "coverage.json", "w") as f:
        json.dump(coverage_dict, f, indent=2)
    rich_print(f"Saved output to {output_dir.absolute()}")


if __name__ == "__main__":
    main(CLI(CoverageConfig, as_positional=False))
