import csv
from dataclasses import dataclass, field
from typing import List, Tuple

import pandas as pd

from agentops.compare_runs.model import SummaryMetricsDF


@dataclass
class DiffResults:
    """Class for comparing two evaluation results."""

    result1: SummaryMetricsDF
    result2: SummaryMetricsDF

    def __init__(self, result1: SummaryMetricsDF, result2: SummaryMetricsDF):
        """Initialize DiffResults object."""
        self.result1 = result1  # Reference result
        self.result2 = result2  # Experiment result
        self.diff_table = None  # Diff table
        self.diff_metrics = None  # Diff metrics

    def get_overlapping_test_cases(self) -> List[str]:
        """Get the overlapping test cases between the two results."""
        return list(set(self.result1.df["dataset_name"]) & set(self.result2.df["dataset_name"]))  # type: ignore

    def get_non_overlapping_test_cases(self) -> Tuple[List[str], List[str]]:
        """
        Get test cases that don't overlap between reference and experiment.

        Returns:
            Tuple of (only_in_reference, only_in_experiment)
        """
        reference_names = set(self.result1.df["dataset_name"])
        experiment_names = set(self.result2.df["dataset_name"])

        only_in_reference = list(reference_names - experiment_names)
        only_in_experiment = list(experiment_names - reference_names)

        return only_in_reference, only_in_experiment

    def get_overlap_dfs(self) -> pd.DataFrame:

        overlapping = self.get_overlapping_test_cases()

        if len(overlapping) == 0:
            return pd.DataFrame()

        # Filter both DataFrames to only overlapping test cases
        result1_overlapping = SummaryMetricsDF(
            df=self.result1.df[
                self.result1.df["dataset_name"].isin(overlapping)
            ]
        )
        result2_overlapping = SummaryMetricsDF(
            df=self.result2.df[
                self.result2.df["dataset_name"].isin(overlapping)
            ]
        )

        return result1_overlapping, result2_overlapping

    def compute_overlapping_summary_metrics(
        self, result1_overlapping, result2_overlapping
    ) -> pd.DataFrame:
        """Compute summary metrics for both results, but only on overlapping test cases."""
        # Get overlapping test case names using existing method

        # Compute summary metrics for each
        summary1 = result1_overlapping.get_df_summary(
            string_column="text_match", string_value="Summary Matched"
        )
        summary2 = result2_overlapping.get_df_summary(
            string_column="text_match", string_value="Summary Matched"
        )

        # Turn summary1 and summary2 into dataframe and join
        comparison_df = (
            pd.DataFrame({"reference": summary1, "experiment": summary2})
            .reset_index()
            .rename(columns={"index": "metric"})
        )

        comparison_df["experiment - reference"] = (
            comparison_df["experiment"] - comparison_df["reference"]
        )
        comparison_df = comparison_df.round(2)

        return comparison_df

    def get_summary_statistics_table(self) -> pd.DataFrame:
        """
        Generate a formatted summary statistics table comparing reference and experiment results.

        Returns:
            DataFrame with columns: Metric, Reference, Experiment, Experiment - Reference
        """
        # Get overlapping dataframes
        result1_overlapping, result2_overlapping = self.get_overlap_dfs()

        # Compute metrics on overlapping data
        overlap_metrics = self.compute_overlapping_summary_metrics(
            result1_overlapping, result2_overlapping
        )

        # Build summary rows dynamically
        summary_rows = []

        # Row 1: Total Tests
        summary_rows.append(
            {
                "Metric": "Total Tests",
                "Reference": len(self.result1.df),
                "Experiment": len(self.result2.df),
            }
        )

        # Row 2: Overlapping Tests
        summary_rows.append(
            {
                "Metric": "Overlapping Tests",
                "Reference": len(result1_overlapping.df),
                "Experiment": len(result2_overlapping.df),
            }
        )

        # Row 3 & 4: Extract from overlap_metrics
        for metric_name, display_name in [
            ("text_match_count", "Summary Matches"),
            ("is_success_true_count", "Is Success"),
        ]:
            metric_row = overlap_metrics[
                overlap_metrics["metric"] == metric_name
            ]
            if not metric_row.empty:
                summary_rows.append(
                    {
                        "Metric": display_name,
                        "Reference": int(metric_row.iloc[0]["reference"]),
                        "Experiment": int(metric_row.iloc[0]["experiment"]),
                    }
                )

        # Create DataFrame and add difference column
        summary_stats = pd.DataFrame(summary_rows)
        summary_stats["Experiment - Reference"] = (
            summary_stats["Experiment"] - summary_stats["Reference"]
        )

        return summary_stats

    def get_overlapping_summary_metrics_table(self) -> pd.DataFrame:
        """
        Get the full overlapping summary metrics table.
        This is a convenience method that handles getting overlapping dataframes internally.

        Returns:
            DataFrame with columns: metric, reference, experiment, experiment - reference
        """
        # Get overlapping dataframes
        result1_overlapping, result2_overlapping = self.get_overlap_dfs()
        # Compute and return metrics
        return self.compute_overlapping_summary_metrics(
            result1_overlapping, result2_overlapping
        )

    def get_column_differences(self, column_name: str) -> pd.DataFrame:
        """
        Get rows where the specified column values differ between reference and experiment.

        Args:
            column_name: Name of the column to compare (e.g., 'text_match', 'is_success')

        Returns:
            DataFrame with dataset_name and the differing column values from both results
        """
        # Get overlapping dataframes
        result1_overlapping, result2_overlapping = self.get_overlap_dfs()

        # Check if we have overlapping data
        if (
            isinstance(result1_overlapping, pd.DataFrame)
            and result1_overlapping.empty
        ):
            return pd.DataFrame()

        # Merge on dataset_name to align the rows
        merged = result1_overlapping.df.merge(
            result2_overlapping.df,
            on="dataset_name",
            suffixes=("_reference", "_experiment"),
        )

        # Build column names with suffixes
        col_ref = f"{column_name}_reference"
        col_exp = f"{column_name}_experiment"

        # Filter to rows where the column differs
        if col_ref in merged.columns and col_exp in merged.columns:
            differences = merged[merged[col_ref] != merged[col_exp]][
                ["dataset_name", col_ref, col_exp]
            ]
            return differences

        return pd.DataFrame()
