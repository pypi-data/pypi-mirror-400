"""Parallel execution engine for DataCheck."""

from multiprocessing import Pool, cpu_count
from typing import Any

import pandas as pd

from datacheck.exceptions import ValidationError
from datacheck.results import RuleResult


class ParallelExecutor:
    """Execute validation rules in parallel across multiple CPU cores.

    Splits data into chunks and processes each chunk in parallel,
    then aggregates the results. Provides significant speedup for
    large datasets on multi-core systems.

    Example:
        >>> executor = ParallelExecutor(workers=4)
        >>> results = executor.validate_parallel(df, rules)
    """

    def __init__(self, workers: int | None = None, chunk_size: int = 10000) -> None:
        """Initialize parallel executor.

        Args:
            workers: Number of worker processes (default: CPU count)
            chunk_size: Rows per chunk (default: 10000)
        """
        self.workers = workers or cpu_count()
        self.chunk_size = chunk_size

    def validate_parallel(
        self, df: pd.DataFrame, rules: list[Any]
    ) -> list[RuleResult]:
        """Execute validation rules in parallel.

        Args:
            df: DataFrame to validate
            rules: List of validation rules

        Returns:
            List of aggregated RuleResult objects

        Raises:
            ValidationError: If parallel execution fails
        """
        if len(df) < self.chunk_size:
            # Too small for parallel processing
            return self._validate_sequential(df, rules)

        try:
            # Split DataFrame into chunks
            chunks = self._chunk_dataframe(df)

            # Prepare work items (chunk, rules pairs)
            work_items = [(chunk, rules) for chunk in chunks]

            # Execute in parallel
            with Pool(self.workers) as pool:
                chunk_results = pool.starmap(self._validate_chunk, work_items)

            # Aggregate results across chunks
            aggregated_results = self._aggregate_results(chunk_results, len(df))

            return aggregated_results

        except Exception as e:
            raise ValidationError(f"Parallel execution failed: {e}") from e

    def _chunk_dataframe(self, df: pd.DataFrame) -> list[pd.DataFrame]:
        """Split DataFrame into chunks.

        Args:
            df: DataFrame to split

        Returns:
            List of DataFrame chunks
        """
        chunks = []
        for i in range(0, len(df), self.chunk_size):
            chunk = df.iloc[i : i + self.chunk_size].copy()
            chunks.append(chunk)
        return chunks

    @staticmethod
    def _validate_chunk(chunk: pd.DataFrame, rules: list[Any]) -> list[RuleResult]:
        """Validate a single chunk.

        This is a static method so it can be pickled for multiprocessing.

        Args:
            chunk: DataFrame chunk to validate
            rules: List of validation rules

        Returns:
            List of RuleResult objects for this chunk
        """
        results = []
        for rule in rules:
            try:
                result = rule.validate(chunk)
                results.append(result)
            except Exception as e:
                # Create error result
                results.append(
                    RuleResult(
                        rule_name=rule.name,
                        column=rule.column,
                        passed=False,
                        total_rows=len(chunk),
                        failed_rows=len(chunk),
                        error=str(e),
                    )
                )
        return results

    def _aggregate_results(
        self, chunk_results: list[list[RuleResult]], total_rows: int
    ) -> list[RuleResult]:
        """Aggregate results from all chunks.

        Args:
            chunk_results: List of result lists (one per chunk)
            total_rows: Total number of rows in original DataFrame

        Returns:
            List of aggregated RuleResult objects
        """
        if not chunk_results:
            return []

        # Group results by rule name
        results_by_rule: dict[str, list[RuleResult]] = {}

        for chunk_result_list in chunk_results:
            for result in chunk_result_list:
                rule_name = result.rule_name

                if rule_name not in results_by_rule:
                    results_by_rule[rule_name] = []

                results_by_rule[rule_name].append(result)

        # Aggregate each rule's results
        aggregated = []
        for _, results in results_by_rule.items():
            aggregated_result = self._aggregate_rule_results(results, total_rows)
            aggregated.append(aggregated_result)

        return aggregated

    def _aggregate_rule_results(
        self, results: list[RuleResult], total_rows: int
    ) -> RuleResult:
        """Aggregate results for a single rule across chunks.

        Args:
            results: List of RuleResult objects for same rule
            total_rows: Total number of rows

        Returns:
            Aggregated RuleResult
        """
        if not results:
            raise ValueError("No results to aggregate")

        # Use first result as template
        template = results[0]

        # Aggregate failure counts
        total_failures = sum(r.failed_rows for r in results)

        # Check if any chunk had errors
        error_messages = [r.error for r in results if r.error]
        error_message = "; ".join(error_messages) if error_messages else None

        return RuleResult(
            rule_name=template.rule_name,
            column=template.column,
            passed=(total_failures == 0 and not error_message),
            total_rows=total_rows,
            failed_rows=total_failures,
            error=error_message,
            rule_type=template.rule_type,
            check_name=template.check_name,
        )

    def _validate_sequential(
        self, df: pd.DataFrame, rules: list[Any]
    ) -> list[RuleResult]:
        """Fallback to sequential validation for small datasets.

        Args:
            df: DataFrame to validate
            rules: List of validation rules

        Returns:
            List of RuleResult objects
        """
        results = []
        for rule in rules:
            try:
                result = rule.validate(df)
                results.append(result)
            except Exception as e:
                results.append(
                    RuleResult(
                        rule_name=rule.name,
                        column=rule.column,
                        passed=False,
                        total_rows=len(df),
                        failed_rows=len(df),
                        error=str(e),
                    )
                )
        return results


__all__ = ["ParallelExecutor"]
