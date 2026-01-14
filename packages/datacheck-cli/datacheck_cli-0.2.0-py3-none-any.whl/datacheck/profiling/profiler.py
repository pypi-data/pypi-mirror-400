"""Data profiling and quality analysis."""

from typing import Any

import pandas as pd


class DataProfiler:
    """Generate comprehensive data quality profiles.

    Analyzes DataFrames to provide:
    - Column types and data types
    - Statistical summaries (numeric columns)
    - Missing value analysis
    - Cardinality and uniqueness
    - Data quality insights

    Example:
        >>> profiler = DataProfiler()
        >>> profile = profiler.profile_dataframe(df)
        >>> print(profile['summary']['total_rows'])
    """

    def profile_dataframe(self, df: pd.DataFrame) -> dict[str, Any]:
        """Generate comprehensive profile of a DataFrame.

        Args:
            df: DataFrame to profile

        Returns:
            Dictionary containing profile information with keys:
            - summary: Overall dataset summary
            - columns: Per-column analysis
            - quality_issues: Detected data quality issues
        """
        summary = self._generate_summary(df)
        columns = self._analyze_columns(df)
        quality_issues = self._detect_quality_issues(df, columns)

        return {"summary": summary, "columns": columns, "quality_issues": quality_issues}

    def _generate_summary(self, df: pd.DataFrame) -> dict[str, Any]:
        """Generate overall dataset summary.

        Args:
            df: DataFrame to analyze

        Returns:
            Summary statistics
        """
        return {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
            "duplicate_rows": int(df.duplicated().sum()),
            "duplicate_percentage": round((df.duplicated().sum() / len(df) * 100) if len(df) > 0 else 0, 2),
        }

    def _analyze_columns(self, df: pd.DataFrame) -> list[dict[str, Any]]:
        """Analyze each column in the DataFrame.

        Args:
            df: DataFrame to analyze

        Returns:
            List of column analysis results
        """
        column_analyses = []

        for col in df.columns:
            analysis = self._analyze_column(df, col)
            column_analyses.append(analysis)

        return column_analyses

    def _analyze_column(self, df: pd.DataFrame, col: str) -> dict[str, Any]:
        """Analyze a single column.

        Args:
            df: DataFrame containing the column
            col: Column name

        Returns:
            Column analysis results
        """
        series = df[col]
        total_count = len(series)
        null_count = int(series.isnull().sum())
        non_null_count = total_count - null_count

        analysis = {
            "name": col,
            "dtype": str(series.dtype),
            "total_count": total_count,
            "null_count": null_count,
            "null_percentage": round((null_count / total_count * 100) if total_count > 0 else 0, 2),
            "non_null_count": non_null_count,
            "unique_count": int(series.nunique()),
            "unique_percentage": round((series.nunique() / non_null_count * 100) if non_null_count > 0 else 0, 2),
        }

        # Determine column type and add specific analysis
        # Check boolean first since is_numeric_dtype also returns True for booleans
        if pd.api.types.is_bool_dtype(series):
            analysis["column_type"] = "boolean"
            analysis.update(self._analyze_boolean_column(series))
        elif pd.api.types.is_numeric_dtype(series):
            analysis["column_type"] = "numeric"
            analysis.update(self._analyze_numeric_column(series))
        elif pd.api.types.is_datetime64_any_dtype(series):
            analysis["column_type"] = "datetime"
            analysis.update(self._analyze_datetime_column(series))
        else:
            analysis["column_type"] = "categorical"
            analysis.update(self._analyze_categorical_column(series))

        return analysis

    def _analyze_numeric_column(self, series: pd.Series) -> dict[str, Any]:
        """Analyze numeric column.

        Args:
            series: Numeric series to analyze

        Returns:
            Numeric statistics
        """
        stats = {}
        non_null = series.dropna()

        if len(non_null) > 0:
            stats["min"] = float(non_null.min())
            stats["max"] = float(non_null.max())
            stats["mean"] = round(float(non_null.mean()), 4)
            stats["median"] = float(non_null.median())
            stats["std"] = round(float(non_null.std()), 4)
            stats["q25"] = float(non_null.quantile(0.25))
            stats["q75"] = float(non_null.quantile(0.75))

            # Detect zeros
            zero_count = int((non_null == 0).sum())
            stats["zero_count"] = zero_count
            stats["zero_percentage"] = round((zero_count / len(non_null) * 100) if len(non_null) > 0 else 0, 2)

            # Detect negative values
            negative_count = int((non_null < 0).sum())
            stats["negative_count"] = negative_count
            stats["negative_percentage"] = round(
                (negative_count / len(non_null) * 100) if len(non_null) > 0 else 0, 2
            )

        return stats

    def _analyze_datetime_column(self, series: pd.Series) -> dict[str, Any]:
        """Analyze datetime column.

        Args:
            series: Datetime series to analyze

        Returns:
            Datetime statistics
        """
        stats: dict[str, Any] = {}
        non_null = series.dropna()

        if len(non_null) > 0:
            stats["min_date"] = str(non_null.min())
            stats["max_date"] = str(non_null.max())
            stats["range_days"] = int((non_null.max() - non_null.min()).days)

        return stats

    def _analyze_boolean_column(self, series: pd.Series) -> dict[str, Any]:
        """Analyze boolean column.

        Args:
            series: Boolean series to analyze

        Returns:
            Boolean statistics
        """
        stats: dict[str, Any] = {}
        non_null = series.dropna()

        if len(non_null) > 0:
            true_count = int(non_null.sum())
            false_count = len(non_null) - true_count
            stats["true_count"] = true_count
            stats["false_count"] = false_count
            stats["true_percentage"] = round((true_count / len(non_null) * 100) if len(non_null) > 0 else 0, 2)

        return stats

    def _analyze_categorical_column(self, series: pd.Series) -> dict[str, Any]:
        """Analyze categorical column.

        Args:
            series: Categorical series to analyze

        Returns:
            Categorical statistics
        """
        stats: dict[str, Any] = {}
        non_null = series.dropna()

        if len(non_null) > 0:
            value_counts = non_null.value_counts()
            stats["most_common_value"] = str(value_counts.index[0]) if len(value_counts) > 0 else None
            stats["most_common_count"] = int(value_counts.iloc[0]) if len(value_counts) > 0 else 0
            stats["most_common_percentage"] = round(
                (value_counts.iloc[0] / len(non_null) * 100) if len(value_counts) > 0 and len(non_null) > 0 else 0,
                2,
            )

            # Sample top 10 values
            if len(value_counts) > 0:
                top_values = {str(k): int(v) for k, v in value_counts.head(10).items()}
                stats["top_values"] = top_values

        return stats

    def _detect_quality_issues(self, df: pd.DataFrame, column_analyses: list[dict[str, Any]]) -> list[dict[str, str]]:
        """Detect potential data quality issues.

        Args:
            df: DataFrame being analyzed
            column_analyses: Column analysis results

        Returns:
            List of detected quality issues
        """
        issues = []

        # Check for high null percentages
        for col_analysis in column_analyses:
            if col_analysis["null_percentage"] > 50:
                issues.append(
                    {
                        "severity": "high",
                        "column": col_analysis["name"],
                        "issue": f"High missing value rate ({col_analysis['null_percentage']}%)",
                    }
                )
            elif col_analysis["null_percentage"] > 20:
                issues.append(
                    {
                        "severity": "medium",
                        "column": col_analysis["name"],
                        "issue": f"Moderate missing value rate ({col_analysis['null_percentage']}%)",
                    }
                )

            # Check for low cardinality in potentially unique columns
            if col_analysis["unique_count"] == 1 and col_analysis["non_null_count"] > 1:
                issues.append(
                    {
                        "severity": "medium",
                        "column": col_analysis["name"],
                        "issue": "Constant value (no variation)",
                    }
                )

            # Check for high cardinality
            if col_analysis["unique_percentage"] > 95 and col_analysis["column_type"] == "categorical":
                issues.append(
                    {
                        "severity": "low",
                        "column": col_analysis["name"],
                        "issue": f"Very high cardinality ({col_analysis['unique_percentage']}% unique)",
                    }
                )

        # Check for duplicate rows
        if len(df) > 0:
            dup_pct = (df.duplicated().sum() / len(df) * 100)
            if dup_pct > 10:
                issues.append(
                    {
                        "severity": "high",
                        "column": "ALL",
                        "issue": f"High duplicate row rate ({round(dup_pct, 2)}%)",
                    }
                )
            elif dup_pct > 1:
                issues.append(
                    {
                        "severity": "low",
                        "column": "ALL",
                        "issue": f"Some duplicate rows detected ({round(dup_pct, 2)}%)",
                    }
                )

        return issues


__all__ = ["DataProfiler"]
