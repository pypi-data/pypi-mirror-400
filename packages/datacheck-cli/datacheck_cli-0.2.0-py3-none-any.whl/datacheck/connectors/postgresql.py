"""PostgreSQL database connector."""


import pandas as pd

try:
    import psycopg2
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

from datacheck.connectors.base import DatabaseConnector
from datacheck.exceptions import DataLoadError


class PostgreSQLConnector(DatabaseConnector):
    """PostgreSQL database connector.

    Connects to PostgreSQL databases using psycopg2 and loads data into pandas DataFrames.

    Example:
        >>> connector = PostgreSQLConnector("postgresql://user:pass@localhost:5432/mydb")
        >>> with connector:
        ...     df = connector.load_table("users", where="active = true")
    """

    def __init__(self, connection_string: str) -> None:
        """Initialize PostgreSQL connector.

        Args:
            connection_string: PostgreSQL connection string

        Raises:
            DataLoadError: If psycopg2 is not installed
        """
        if not PSYCOPG2_AVAILABLE:
            raise DataLoadError(
                "psycopg2 is not installed. Install it with: pip install psycopg2-binary"
            )

        super().__init__(connection_string)
        self.connection: object = None

    def connect(self) -> None:
        """Establish connection to PostgreSQL database.

        Raises:
            DataLoadError: If connection fails
        """
        try:
            self.connection = psycopg2.connect(self.connection_string)
            self._is_connected = True
        except psycopg2.Error as e:
            raise DataLoadError(f"Failed to connect to PostgreSQL: {e}") from e
        except Exception as e:
            raise DataLoadError(f"Unexpected error connecting to PostgreSQL: {e}") from e

    def disconnect(self) -> None:
        """Close PostgreSQL connection."""
        if self.connection:
            try:
                self.connection.close()  # type: ignore[attr-defined]
                self._is_connected = False
            except Exception:
                pass  # Ignore errors when closing

    def load_table(
        self,
        table_name: str,
        where: str | None = None,
        limit: int | None = None
    ) -> pd.DataFrame:
        """Load data from PostgreSQL table.

        Args:
            table_name: Name of the table to load
            where: Optional WHERE clause (without 'WHERE' keyword)
            limit: Optional row limit

        Returns:
            DataFrame containing table data

        Raises:
            DataLoadError: If not connected or table loading fails
        """
        if not self.is_connected:
            raise DataLoadError("Not connected to database. Call connect() first.")

        try:
            # Build query string - use simple string formatting with quoted identifiers
            # This approach works with both real connections and mocked connections in tests
            query_parts = [f'SELECT * FROM "{table_name}"']

            if where:
                query_parts.append(f" WHERE {where}")

            if limit:
                query_parts.append(f" LIMIT {limit}")

            query_string = "".join(query_parts)

            # Execute query
            return pd.read_sql_query(query_string, self.connection)  # type: ignore[call-overload,no-any-return]

        except psycopg2.Error as e:
            raise DataLoadError(f"Failed to load table '{table_name}': {e}") from e
        except Exception as e:
            raise DataLoadError(f"Unexpected error loading table '{table_name}': {e}") from e

    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute SQL query on PostgreSQL database.

        Args:
            query: SQL query to execute

        Returns:
            DataFrame containing query results

        Raises:
            DataLoadError: If not connected or query execution fails
        """
        if not self.is_connected:
            raise DataLoadError("Not connected to database. Call connect() first.")

        try:
            return pd.read_sql_query(query, self.connection)  # type: ignore[call-overload,no-any-return]
        except psycopg2.Error as e:
            raise DataLoadError(f"Failed to execute query: {e}") from e
        except Exception as e:
            raise DataLoadError(f"Unexpected error executing query: {e}") from e
