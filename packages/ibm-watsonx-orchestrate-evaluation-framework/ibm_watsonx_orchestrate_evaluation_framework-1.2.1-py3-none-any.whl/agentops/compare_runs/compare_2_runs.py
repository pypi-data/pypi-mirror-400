import sys
from pathlib import Path

import pandas as pd
from jsonargparse import CLI

from agentops.arg_configs import CompareRunsConfig
from agentops.compare_runs.diff import DiffResults
from agentops.compare_runs.model import SummaryMetricsDF
from agentops.utils.utils import create_table


def main(config: CompareRunsConfig):
    """Main function to compare two run result files."""
    # Extract values from config
    reference_file = config.reference_file_location
    experiment_file = config.experiment_file_location

    try:
        # Create evaluation results directly from files
        result1 = SummaryMetricsDF.from_csv(reference_file)
        result2 = SummaryMetricsDF.from_csv(experiment_file)

        # Create diff results
        diff_results = DiffResults(result1, result2)

        # Get and print summary statistics table
        summary_stats_table = diff_results.get_summary_statistics_table()
        tmp_table = create_table(
            summary_stats_table, title="Summary Statistics"
        )
        if tmp_table:
            tmp_table.print()

        # Get and print non-overlapping test cases
        only_in_ref, only_in_exp = diff_results.get_non_overlapping_test_cases()
        print(f"\nTest cases only in reference: {len(only_in_ref)}")
        if only_in_ref:
            print(only_in_ref)
        print(f"\nTest cases only in experiment: {len(only_in_exp)}")
        if only_in_exp:
            print(only_in_exp)

        # Get and print column statistics table
        column_stats_table = (
            diff_results.get_overlapping_summary_metrics_table()
        )
        tmp_table = create_table(column_stats_table, title="Average Values")
        if tmp_table:
            tmp_table.print()

        # Print all column differences
        for column_name, display_name in [
            ("text_match", "Text Match"),
            ("is_success", "Is Success"),
        ]:
            diffs_table = diff_results.get_column_differences(column_name)
            if not diffs_table.empty:
                tmp_table = create_table(
                    diffs_table, title=f"{display_name} Differences"
                )
                if tmp_table:
                    tmp_table.print()
            else:
                print(f"\n{display_name} Differences")
                print(
                    f"No differences found - all overlapping test cases have matching {column_name} values"
                )

        ## write each table to a csv in a specified folder
        if config.csv_output_dir:
            csv_output_dir = Path(config.csv_output_dir)
            csv_output_dir.mkdir(parents=True, exist_ok=True)

            summary_stats_table.to_csv(
                csv_output_dir / "summary_statistics.csv", index=False
            )
            column_stats_table.to_csv(
                csv_output_dir / "average_values.csv", index=False
            )
            if not diffs_table.empty:
                diffs_table.to_csv(
                    csv_output_dir / "diff_results.csv", index=False
                )

            print(f"\nCSV files written to {csv_output_dir}/")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    args = CLI(CompareRunsConfig, as_positional=False)
    sys.exit(main(args))

# Made with Bob
