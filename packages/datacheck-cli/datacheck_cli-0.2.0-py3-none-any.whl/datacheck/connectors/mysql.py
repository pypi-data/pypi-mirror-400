"""MySQL database connector."""


import pandas as pd

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

from datacheck.connectors.base import DatabaseConnector
from datacheck.exceptions import DataLoadError


class MySQLConnector(DatabaseConnector):
    """MySQL database connector.

    Connects to MySQL databases using mysql-connector-python and loads data
    into pandas DataFrames.

    Example:
        >>> connector = MySQLConnector("mysql://user:pass@localhost:3306/mydb")
        >>> with connector:
        ...     df = connector.load_table("users")
    """

    def __init__(self, connection_string: str) -> None:
        """Initialize MySQL connector.

        Args:
            connection_string: MySQL connection string

        Raises:
            DataLoadError: If mysql-connector-python is not installed
        """
        if not MYSQL_AVAILABLE:
            raise DataLoadError(
                "mysql-connector-python is not installed. "
                "Install it with: pip install mysql-connector-python"
            )

        super().__init__(connection_string)
        self.connection: object = None
        self._parse_connection_string()

    def _parse_connection_string(self) -> None:
        """Parse MySQL connection string into components."""
        # Simple parsing of mysql://user:pass@host:port/database
        try:
            from sqlalchemy.engine.url import make_url
            url = make_url(self.connection_string)

            self.config = {
                "host": url.host or "localhost",
                "port": url.port or 3306,
                "user": url.username,
                "password": url.password,
                "database": url.database,
            }
        except Exception as e:
            raise DataLoadError(f"Invalid MySQL connection string: {e}") from e

    def connect(self) -> None:
        """Establish connection to MySQL database.

        Raises:
            DataLoadError: If connection fails
        """
        try:
            self.connection = mysql.connector.connect(**self.config)
            self._is_connected = True
        except MySQLError as e:
            raise DataLoadError(f"Failed to connect to MySQL: {e}") from e
        except Exception as e:
            raise DataLoadError(f"Unexpected error connecting to MySQL: {e}") from e

    def disconnect(self) -> None:
        """Close MySQL connection."""
        if self.connection and self.connection.is_connected():  # type: ignore[attr-defined]
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
        """Load data from MySQL table.

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
            # Build query
            query = f"SELECT * FROM `{table_name}`"

            if where:
                query += f" WHERE {where}"

            if limit:
                query += f" LIMIT {limit}"

            return pd.read_sql_query(query, self.connection)  # type: ignore[call-overload,no-any-return]

        except MySQLError as e:
            raise DataLoadError(f"Failed to load table '{table_name}': {e}") from e
        except Exception as e:
            raise DataLoadError(f"Unexpected error loading table '{table_name}': {e}") from e

    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute SQL query on MySQL database.

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
        except MySQLError as e:
            raise DataLoadError(f"Failed to execute query: {e}") from e
        except Exception as e:
            raise DataLoadError(f"Unexpected error executing query: {e}") from e
