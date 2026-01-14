"""Base classes for database connectors."""

from abc import ABC, abstractmethod

import pandas as pd


class DatabaseConnector(ABC):
    """Abstract base class for database connectors.

    This class defines the interface that all database connectors must implement.
    Connectors handle connection management, query execution, and data loading.

    Example:
        >>> connector = PostgreSQLConnector("postgresql://localhost/mydb")
        >>> connector.connect()
        >>> df = connector.load_table("users")
        >>> connector.disconnect()
    """

    def __init__(self, connection_string: str) -> None:
        """Initialize database connector.

        Args:
            connection_string: Database connection string (e.g., postgresql://user:pass@host/db)
        """
        self.connection_string = connection_string
        self.connection: object | None = None
        self._is_connected = False

    @abstractmethod
    def connect(self) -> None:
        """Establish connection to database.

        Raises:
            DataLoadError: If connection fails
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close database connection."""
        pass

    @abstractmethod
    def load_table(
        self,
        table_name: str,
        where: str | None = None,
        limit: int | None = None
    ) -> pd.DataFrame:
        """Load data from a database table.

        Args:
            table_name: Name of the table to load
            where: Optional WHERE clause (without 'WHERE' keyword)
            limit: Optional row limit

        Returns:
            DataFrame containing table data

        Raises:
            DataLoadError: If table loading fails
        """
        pass

    @abstractmethod
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute a SQL query and return results.

        Args:
            query: SQL query to execute

        Returns:
            DataFrame containing query results

        Raises:
            DataLoadError: If query execution fails
        """
        pass

    def __enter__(self) -> "DatabaseConnector":
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: object) -> None:
        """Context manager exit."""
        self.disconnect()

    @property
    def is_connected(self) -> bool:
        """Check if connector is connected to database."""
        return self._is_connected
