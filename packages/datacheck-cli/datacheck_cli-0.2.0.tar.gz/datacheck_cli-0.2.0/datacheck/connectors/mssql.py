"""Microsoft SQL Server database connector."""


import pandas as pd

try:
    import pyodbc
    PYODBC_AVAILABLE = True
except ImportError:
    PYODBC_AVAILABLE = False

from datacheck.connectors.base import DatabaseConnector
from datacheck.exceptions import DataLoadError


class SQLServerConnector(DatabaseConnector):
    """Microsoft SQL Server database connector.

    Connects to SQL Server databases using pyodbc and loads data into pandas DataFrames.

    Example:
        >>> connector = SQLServerConnector("mssql://user:pass@localhost/mydb")
        >>> with connector:
        ...     df = connector.load_table("users")
    """

    def __init__(self, connection_string: str) -> None:
        """Initialize SQL Server connector.

        Args:
            connection_string: SQL Server connection string

        Raises:
            DataLoadError: If pyodbc is not installed
        """
        if not PYODBC_AVAILABLE:
            raise DataLoadError(
                "pyodbc is not installed. Install it with: pip install pyodbc"
            )

        super().__init__(connection_string)
        self.connection: object = None
        self._build_odbc_connection_string()

    def _build_odbc_connection_string(self) -> None:
        """Build ODBC connection string from URL format."""
        try:
            from sqlalchemy.engine.url import make_url
            url = make_url(self.connection_string)

            driver = "{ODBC Driver 17 for SQL Server}"
            server = url.host or "localhost"
            database = url.database

            if url.username and url.password:
                self.odbc_string = (
                    f"DRIVER={driver};"
                    f"SERVER={server};"
                    f"DATABASE={database};"
                    f"UID={url.username};"
                    f"PWD={url.password}"
                )
            else:
                # Use Windows authentication
                self.odbc_string = (
                    f"DRIVER={driver};"
                    f"SERVER={server};"
                    f"DATABASE={database};"
                    f"Trusted_Connection=yes"
                )
        except Exception as e:
            raise DataLoadError(f"Invalid SQL Server connection string: {e}") from e

    def connect(self) -> None:
        """Establish connection to SQL Server database.

        Raises:
            DataLoadError: If connection fails
        """
        try:
            self.connection = pyodbc.connect(self.odbc_string)
            self._is_connected = True
        except pyodbc.Error as e:
            raise DataLoadError(f"Failed to connect to SQL Server: {e}") from e
        except Exception as e:
            raise DataLoadError(f"Unexpected error connecting to SQL Server: {e}") from e

    def disconnect(self) -> None:
        """Close SQL Server connection."""
        if self.connection:
            try:
                self.connection.close()  # type: ignore[attr-defined]
                self._is_connected = False
            except Exception:
                pass

    def load_table(
        self,
        table_name: str,
        where: str | None = None,
        limit: int | None = None
    ) -> pd.DataFrame:
        """Load data from SQL Server table.

        Args:
            table_name: Name of the table to load
            where: Optional WHERE clause (without 'WHERE' keyword)
            limit: Optional row limit (uses TOP in SQL Server)

        Returns:
            DataFrame containing table data

        Raises:
            DataLoadError: If not connected or table loading fails
        """
        if not self.is_connected:
            raise DataLoadError("Not connected to database. Call connect() first.")

        try:
            # Build query (SQL Server uses TOP instead of LIMIT)
            if limit:
                query = f"SELECT TOP {limit} * FROM [{table_name}]"
            else:
                query = f"SELECT * FROM [{table_name}]"

            if where:
                query += f" WHERE {where}"

            return pd.read_sql_query(query, self.connection)  # type: ignore[call-overload,no-any-return]

        except pyodbc.Error as e:
            raise DataLoadError(f"Failed to load table '{table_name}': {e}") from e
        except Exception as e:
            raise DataLoadError(f"Unexpected error loading table '{table_name}': {e}") from e

    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute SQL query on SQL Server database.

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
        except pyodbc.Error as e:
            raise DataLoadError(f"Failed to execute query: {e}") from e
        except Exception as e:
            raise DataLoadError(f"Unexpected error executing query: {e}") from e
