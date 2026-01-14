"""CLI interface for DataCheck."""

from pathlib import Path

import typer
from rich.console import Console

from datacheck import __version__
from datacheck.engine import ValidationEngine
from datacheck.exceptions import ConfigurationError, DataCheckError, DataLoadError, ValidationError
from datacheck.output import JSONExporter, OutputFormatter

app = typer.Typer(
    name="datacheck",
    help="Lightweight data quality validation CLI tool",
    add_completion=False,
)

console = Console()


@app.command()
def validate(
    data_source: str = typer.Argument(
        ...,
        help="Data source: file path or database connection string"
    ),
    config: str | None = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to validation config file (auto-discovered if not provided)",
    ),
    table: str | None = typer.Option(
        None,
        "--table",
        "-t",
        help="Database table name (for database sources)",
    ),
    where: str | None = typer.Option(
        None,
        "--where",
        "-w",
        help="WHERE clause for filtering (for database sources)",
    ),
    query: str | None = typer.Option(
        None,
        "--query",
        "-q",
        help="Custom SQL query (alternative to --table)",
    ),
    sample_rate: float | None = typer.Option(
        None,
        "--sample-rate",
        help="Random sample rate (0.0 to 1.0)",
    ),
    sample_count: int | None = typer.Option(
        None,
        "--sample-count",
        help="Number of rows to sample",
    ),
    top: int | None = typer.Option(
        None,
        "--top",
        help="Validate only first N rows",
    ),
    stratify: str | None = typer.Option(
        None,
        "--stratify",
        help="Column name for stratified sampling (requires --sample-count)",
    ),
    seed: int | None = typer.Option(
        None,
        "--seed",
        help="Random seed for reproducible sampling",
    ),
    parallel: bool = typer.Option(
        False,
        "--parallel",
        help="Enable parallel execution for faster validation",
    ),
    workers: int | None = typer.Option(
        None,
        "--workers",
        help="Number of worker processes (default: CPU count)",
    ),
    slack_webhook: str | None = typer.Option(
        None,
        "--slack-webhook",
        help="Slack webhook URL for sending validation results notifications",
    ),
    output_format: str = typer.Option(
        "terminal",
        "--format",
        "-f",
        help="Output format: 'terminal' or 'json'",
    ),
    output: str | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Path to write output file (for json format)",
    ),
) -> None:
    """Validate data using specified rules.

    Supports both file-based and database sources.

    Exit codes:
      0 - All validation rules passed
      1 - Some validation rules failed
      2 - Configuration error
      3 - Data loading error
      4 - Unexpected error
    """
    try:
        # Validate arguments
        if output_format not in ["terminal", "json"]:
            console.print(
                f"[red]Error:[/red] Invalid output format '{output_format}'. "
                f"Must be 'terminal' or 'json'.",
                style="red",
            )
            raise typer.Exit(code=2)

        if output and output_format == "terminal":
            console.print(
                "[yellow]Warning:[/yellow] --output specified but --format is 'terminal'. "
                "Setting format to 'json'.",
                style="yellow",
            )
            output_format = "json"

        # Initialize Slack notifier if webhook provided
        notifier = None
        if slack_webhook:
            from datacheck.notifications import SlackNotifier
            try:
                notifier = SlackNotifier(slack_webhook)
            except Exception as e:
                console.print(f"[red]Slack Configuration Error:[/red] {e}", style="red")
                raise typer.Exit(code=2) from e

        # Initialize validation engine
        try:
            if config:
                config_path = Path(config)
                engine = ValidationEngine(
                    config_path=config_path, parallel=parallel, workers=workers, notifier=notifier
                )
            else:
                engine = ValidationEngine(parallel=parallel, workers=workers, notifier=notifier)
        except ConfigurationError as e:
            console.print(f"[red]Configuration Error:[/red] {e}", style="red")
            raise typer.Exit(code=2) from e

        # Load and validate data
        try:
            summary = engine.validate_file(
                data_source,
                table=table,
                where=where,
                query=query,
                sample_rate=sample_rate,
                sample_count=sample_count,
                top=top,
                stratify=stratify,
                seed=seed
            )
        except DataLoadError as e:
            console.print(f"[red]Data Load Error:[/red] {e}", style="red")
            raise typer.Exit(code=3) from e

        # Output results
        if output_format == "terminal":
            formatter = OutputFormatter(console=console)
            formatter.print_summary(summary)
        elif output_format == "json":
            json_str = JSONExporter.export_summary(summary, output_path=output, pretty=True)
            if not output:
                # Print to stdout if no output file specified
                console.print(json_str)

        # Determine exit code
        if summary.has_errors:
            # Validation errors occurred (configuration/execution issues)
            raise typer.Exit(code=4)
        elif not summary.all_passed:
            # Validation rules failed
            raise typer.Exit(code=1)
        else:
            # All rules passed
            raise typer.Exit(code=0)

    except typer.Exit:
        # Re-raise typer Exit exceptions (for proper exit codes)
        raise
    except (ConfigurationError, DataLoadError, ValidationError) as e:
        # These should have been handled above, but catch just in case
        console.print(f"[red]Error:[/red] {e}", style="red")
        raise typer.Exit(code=4) from e
    except DataCheckError as e:
        # Generic DataCheck error
        console.print(f"[red]DataCheck Error:[/red] {e}", style="red")
        raise typer.Exit(code=4) from e
    except Exception as e:
        # Unexpected error
        console.print(f"[red]Unexpected Error:[/red] {e}", style="red")
        raise typer.Exit(code=4) from e


@app.command()
def profile(
    data_source: str = typer.Argument(
        ...,
        help="Data source: file path or database connection string"
    ),
    table: str | None = typer.Option(
        None,
        "--table",
        "-t",
        help="Database table name (for database sources)",
    ),
    query: str | None = typer.Option(
        None,
        "--query",
        "-q",
        help="Custom SQL query (alternative to --table)",
    ),
    output: str | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Path to write profile report (JSON format)",
    ),
) -> None:
    """Generate data quality profile for a dataset.

    Analyzes data to provide statistical summaries, missing value analysis,
    cardinality, and data quality insights.

    Exit codes:
      0 - Profile generated successfully
      3 - Data loading error
      4 - Unexpected error
    """
    try:
        # Load data
        from datacheck.loader import LoaderFactory

        try:
            df = LoaderFactory.load(data_source, table=table, query=query)
        except DataLoadError as e:
            console.print(f"[red]Data Load Error:[/red] {e}", style="red")
            raise typer.Exit(code=3) from e

        # Generate profile
        from datacheck.profiling import DataProfiler

        profiler = DataProfiler()
        profile_data = profiler.profile_dataframe(df)

        # Output results
        if output:
            # Write to JSON file
            import json
            from pathlib import Path

            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(profile_data, f, indent=2)
            console.print(f"[green]✓[/green] Profile written to {output}")
        else:
            # Print to terminal
            from rich.table import Table

            # Summary section
            console.print("\n[bold]Dataset Summary[/bold]")
            summary_table = Table(show_header=False)
            summary_table.add_column("Metric", style="cyan")
            summary_table.add_column("Value")

            summary = profile_data["summary"]
            summary_table.add_row("Total Rows", f"{summary['total_rows']:,}")
            summary_table.add_row("Total Columns", str(summary['total_columns']))
            summary_table.add_row("Memory Usage", f"{summary['memory_usage_mb']} MB")
            summary_table.add_row("Duplicate Rows", f"{summary['duplicate_rows']:,} ({summary['duplicate_percentage']}%)")
            console.print(summary_table)

            # Column Analysis
            console.print("\n[bold]Column Analysis[/bold]")
            for col_info in profile_data["columns"]:
                console.print(f"\n[cyan]{col_info['name']}[/cyan] ({col_info['column_type']}, {col_info['dtype']})")
                console.print(f"  Nulls: {col_info['null_count']:,} ({col_info['null_percentage']}%)")
                console.print(f"  Unique: {col_info['unique_count']:,} ({col_info['unique_percentage']}%)")

                if col_info["column_type"] == "numeric":
                    if "mean" in col_info:
                        console.print(f"  Range: [{col_info.get('min', 'N/A')} - {col_info.get('max', 'N/A')}]")
                        console.print(f"  Mean: {col_info.get('mean', 'N/A')}, Median: {col_info.get('median', 'N/A')}")
                elif col_info["column_type"] == "categorical":
                    if "most_common_value" in col_info and col_info["most_common_value"]:
                        console.print(f"  Most Common: '{col_info['most_common_value']}' ({col_info['most_common_percentage']}%)")

            # Quality Issues
            if profile_data["quality_issues"]:
                console.print("\n[bold]Data Quality Issues[/bold]")
                issues_table = Table()
                issues_table.add_column("Severity")
                issues_table.add_column("Column")
                issues_table.add_column("Issue")

                for issue in profile_data["quality_issues"]:
                    severity_style = {
                        "high": "[red]HIGH[/red]",
                        "medium": "[yellow]MEDIUM[/yellow]",
                        "low": "[blue]LOW[/blue]",
                    }.get(issue["severity"], issue["severity"])
                    issues_table.add_row(severity_style, issue["column"], issue["issue"])

                console.print(issues_table)
            else:
                console.print("\n[green]✓ No significant data quality issues detected[/green]")

        raise typer.Exit(code=0)

    except typer.Exit:
        raise
    except DataLoadError as e:
        console.print(f"[red]Data Load Error:[/red] {e}", style="red")
        raise typer.Exit(code=3) from e
    except DataCheckError as e:
        console.print(f"[red]DataCheck Error:[/red] {e}", style="red")
        raise typer.Exit(code=4) from e
    except Exception as e:
        console.print(f"[red]Unexpected Error:[/red] {e}", style="red")
        raise typer.Exit(code=4) from e


@app.command()
def version() -> None:
    """Display version information."""
    console.print(f"DataCheck v{__version__}")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """DataCheck - Lightweight data quality validation CLI tool.

    Run 'datacheck validate <file>' to validate a data file.
    Run 'datacheck --help' for more information.
    """
    if ctx.invoked_subcommand is None:
        console.print("[bold]DataCheck[/bold] - Data Quality Validation")
        console.print(f"Version: {__version__}")
        console.print()
        console.print("Usage: datacheck [COMMAND] [OPTIONS]")
        console.print()
        console.print("Commands:")
        console.print("  validate  Validate data file against configured rules")
        console.print("  profile   Generate data quality profile for a dataset")
        console.print("  version   Display version information")
        console.print()
        console.print("Run 'datacheck [COMMAND] --help' for more information on a command.")


if __name__ == "__main__":
    app()
