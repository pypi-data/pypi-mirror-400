"""Data sampling utilities for efficient validation."""


import pandas as pd

from datacheck.exceptions import DataLoadError


class DataSampler:
    """Provides various sampling strategies for data validation.

    Sampling is useful for validating large datasets where checking every row
    would be too slow. Different strategies serve different use cases.

    Example:
        >>> sampler = DataSampler()
        >>> sample = sampler.random_sample(df, rate=0.1, seed=42)
        >>> # Validate 10% random sample
    """

    @staticmethod
    def random_sample(
        df: pd.DataFrame,
        rate: float | None = None,
        count: int | None = None,
        seed: int | None = None
    ) -> pd.DataFrame:
        """Perform random sampling on DataFrame.

        Args:
            df: DataFrame to sample
            rate: Fraction of rows to sample (0.0 to 1.0)
            count: Exact number of rows to sample
            seed: Random seed for reproducibility

        Returns:
            Sampled DataFrame

        Raises:
            DataLoadError: If both rate and count are specified or neither

        Example:
            >>> # Sample 10% of rows
            >>> sample = DataSampler.random_sample(df, rate=0.1)

            >>> # Sample exact 1000 rows
            >>> sample = DataSampler.random_sample(df, count=1000)
        """
        if rate is not None and count is not None:
            raise DataLoadError("Specify either 'rate' or 'count', not both")

        if rate is None and count is None:
            raise DataLoadError("Must specify either 'rate' or 'count'")

        if rate is not None:
            if not 0.0 < rate <= 1.0:
                raise DataLoadError(f"Sample rate must be between 0 and 1, got {rate}")
            return df.sample(frac=rate, random_state=seed)

        if count is not None:
            if count <= 0:
                raise DataLoadError(f"Sample count must be positive, got {count}")
            actual_count = min(count, len(df))
            return df.sample(n=actual_count, random_state=seed)

        return df

    @staticmethod
    def stratified_sample(
        df: pd.DataFrame,
        column: str,
        count: int,
        seed: int | None = None
    ) -> pd.DataFrame:
        """Perform stratified sampling based on a column.

        Samples a fixed number of rows from each unique value in the specified column.
        Useful for ensuring representation from all categories.

        Args:
            df: DataFrame to sample
            column: Column to stratify by
            count: Number of rows to sample from each stratum
            seed: Random seed for reproducibility

        Returns:
            Stratified sample DataFrame

        Raises:
            DataLoadError: If column doesn't exist or count is invalid

        Example:
            >>> # Sample 100 rows from each country
            >>> sample = DataSampler.stratified_sample(df, "country", count=100)
        """
        if column not in df.columns:
            raise DataLoadError(f"Column '{column}' not found in DataFrame")

        if count <= 0:
            raise DataLoadError(f"Sample count must be positive, got {count}")

        try:
            # Sample from each group
            sampled = df.groupby(column, group_keys=False).apply(
                lambda x: x.sample(n=min(len(x), count), random_state=seed)
            )
            return sampled  # type: ignore[no-any-return]
        except Exception as e:
            raise DataLoadError(f"Error in stratified sampling: {e}") from e

    @staticmethod
    def top_n(df: pd.DataFrame, n: int) -> pd.DataFrame:
        """Return the first N rows.

        Simple head() operation, useful for quick validation of first rows.

        Args:
            df: DataFrame to sample
            n: Number of rows to return

        Returns:
            First N rows of DataFrame

        Raises:
            DataLoadError: If n is invalid

        Example:
            >>> # Validate first 1000 rows
            >>> sample = DataSampler.top_n(df, 1000)
        """
        if n <= 0:
            raise DataLoadError(f"n must be positive, got {n}")

        return df.head(n)

    @staticmethod
    def systematic_sample(
        df: pd.DataFrame,
        interval: int,
        start: int = 0
    ) -> pd.DataFrame:
        """Perform systematic sampling (every Nth row).

        Args:
            df: DataFrame to sample
            interval: Sample every Nth row
            start: Starting index (default 0)

        Returns:
            Systematically sampled DataFrame

        Raises:
            DataLoadError: If interval is invalid

        Example:
            >>> # Sample every 10th row
            >>> sample = DataSampler.systematic_sample(df, interval=10)
        """
        if interval <= 0:
            raise DataLoadError(f"Interval must be positive, got {interval}")

        if start < 0:
            raise DataLoadError(f"Start index must be non-negative, got {start}")

        indices = range(start, len(df), interval)
        return df.iloc[list(indices)]
