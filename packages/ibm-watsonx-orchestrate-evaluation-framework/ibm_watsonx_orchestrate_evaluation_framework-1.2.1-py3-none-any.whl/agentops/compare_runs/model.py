from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import pandas as pd

from agentops.utils.utils import safe_divide


@dataclass
class SummaryMetricsDF:
    """Class representing a collection of test case evaluation results."""

    df: pd.DataFrame  # Store as DataFrame instead of dict

    @classmethod
    def from_csv(cls, file_path: str) -> "SummaryMetricsDF":
        """Create a SummaryMetricsDF from a CSV file."""
        # Read CSV with pandas
        df = pd.read_csv(file_path)

        # Convert boolean columns
        if "is_success" in df.columns:
            df["is_success"] = (
                df["is_success"].astype(str).str.lower() == "true"
            )

        return cls(df)

    def get_df_summary(
        self,
        string_column: Optional[str] = None,
        string_value: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get summary statistics for the DataFrame.

        Computes:
        - Average of numeric columns
        - Average of boolean columns (proportion of True values)
        - Count of specific string value in a column (if specified)

        Args:
            string_column: Optional column name to count string values in
            string_value: Optional string value to count

        Returns:
            Dictionary with 'numeric_averages', 'boolean_averages', and optionally 'string_count'
        """
        if self.df.empty:
            return {}

        summary = {}

        # Separate numeric and boolean columns
        numeric_cols = self.df.select_dtypes(include=["number"]).columns
        bool_cols = self.df.select_dtypes(include=["bool"]).columns

        # Compute averages for numeric and boolean columns only
        cols_to_average = list(numeric_cols) + list(bool_cols)
        if cols_to_average:
            means = self.df[cols_to_average].mean()
            # Convert Series to dict and add to summary
            summary.update(means.to_dict())  # type: ignore

        # Count string values if specified
        if string_column and string_value and string_column in self.df.columns:
            summary[f"{string_column}_count"] = int(
                (self.df[string_column] == string_value).sum()
            )

        # Count boolean values (True and False counts for each boolean column)
        for col in bool_cols:
            summary[f"{col}_true_count"] = int((self.df[col] == True).sum())

        return summary


# Made with Bob
