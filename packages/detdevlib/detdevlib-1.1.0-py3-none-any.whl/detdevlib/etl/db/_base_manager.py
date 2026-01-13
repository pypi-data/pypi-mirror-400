# detdevlib.etl.db._base_manager

import logging
import re
from abc import ABC, abstractmethod
from typing import Literal, Optional, Self, final

import pandas as pd
from sqlalchemy import URL, Connection, create_engine, inspect, text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


def _clean_sql(sql: str, max_len: int = 50) -> str:
    """Condenses SQL for logging."""
    clean_sql = re.sub(r"\s+", " ", sql).strip()
    if len(clean_sql) <= max_len:
        return clean_sql
    return clean_sql[:max_len] + "..."


class DatabaseManager(ABC):
    """Abstract base class for database operations."""

    def __init__(self):
        """Initialize the DatabaseManager."""
        self._engine: Engine | None = None

    # -------------------------------------------------------------------------
    # Connection Management
    # -------------------------------------------------------------------------

    @abstractmethod
    def _get_connection_url(self) -> URL | str:
        pass

    def _get_engine_kwargs(self) -> dict:
        return {}

    @final
    def _get_engine(self) -> Engine:
        if self._engine is None:
            raise RuntimeError("Client is not connected. Please call connect() first.")
        return self._engine

    @final
    def connect(self) -> Self:
        """Initializes the SQLAlchemy Engine."""
        if self._engine is not None:
            return self
        try:
            logger.info("Initializing SQLAlchemy engine...")
            self._engine = create_engine(
                self._get_connection_url(),
                **self._get_engine_kwargs(),
            )
            return self
        except Exception as e:
            logger.error(f"Engine initialization failed: {e}")
            self._engine = None
            raise

    @final
    def disconnect(self):
        """Disposes of the SQLAlchemy engine."""
        if self._engine:
            logger.info("Disposing of the SQLAlchemy engine.")
            self._engine.dispose()
            self._engine = None

    @final
    def __enter__(self):
        return self.connect()

    @final
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    # -------------------------------------------------------------------------
    # General Execution
    # -------------------------------------------------------------------------

    @staticmethod
    def quote(identifier: str) -> str:
        """Quotes a database identifier. Default is double quotes."""
        escaped = identifier.replace('"', '""')
        return f'"{escaped}"'

    def get_full_table_name(self, table: str, schema: Optional[str] = None) -> str:
        """Returns schema.table properly quoted."""
        if schema is None:
            return self.quote(table)
        return f"{self.quote(schema)}.{self.quote(table)}"

    @final
    def _execute_statement(
        self, conn: Connection, sql: str, params: Optional[dict] = None
    ) -> None:
        logger.info(f"Executing statement: {_clean_sql(sql)}")
        try:
            conn.execute(text(sql), params)
            logger.info("Statement executed successfully.")
        except Exception as e:
            logger.error(f"Error executing statement: {e}")
            raise

    @final
    def execute_statement(self, sql: str, params: Optional[dict] = None) -> None:
        """Executes a non-returning SQL statement (INSERT, UPDATE, DROP)."""
        with self._get_engine().begin() as conn:
            self._execute_statement(conn, sql, params)

    @final
    def _execute_query(
        self, conn: Connection, sql: str, params: Optional[dict] = None
    ) -> pd.DataFrame:
        logger.info(f"Executing query: {_clean_sql(sql)}")
        try:
            df = pd.read_sql(text(sql), conn, params=params)
            logger.info(f"Query returned {len(df)} rows.")
            return df
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise

    @final
    def execute_query(self, sql: str, params: Optional[dict] = None) -> pd.DataFrame:
        """Executes a SQL query and returns results as a DataFrame."""
        with self._get_engine().connect() as conn:
            return self._execute_query(conn, sql, params)

    # -------------------------------------------------------------------------
    # Schema Inspection
    # -------------------------------------------------------------------------

    @final
    def list_tables(self, schema: Optional[str] = None) -> list[str]:
        """List all table names in the specified schema."""
        logger.info(f"Fetching tables for schema: {schema or 'default'}")
        try:
            inspector = inspect(self._get_engine())
            return inspector.get_table_names(schema=schema)
        except Exception as e:
            logger.error(f"Failed to list tables: {e}")
            raise

    @final
    def describe_table(self, table: str, schema: Optional[str] = None) -> pd.DataFrame:
        """Return a DataFrame describing the columns of the specified table."""
        full_table_name = self.get_full_table_name(table, schema)
        logger.info(f"Describing table: {full_table_name}")
        try:
            inspector = inspect(self._get_engine())
            columns = inspector.get_columns(table, schema=schema)
            return pd.DataFrame(columns)
        except Exception as e:
            logger.error(f"Failed to describe table: {e}")
            raise

    @final
    def table_exists(self, table: str, schema: Optional[str] = None) -> bool:
        """Check if a specific table exists in the database."""
        full_name = self.get_full_table_name(table, schema)
        logger.info(f"Checking existence of table: {full_name}")
        try:
            inspector = inspect(self._get_engine())
            return inspector.has_table(table, schema=schema)
        except Exception as e:
            logger.error(f"Failed to check table existence: {e}")
            raise

    @final
    def get_pk_columns(self, table: str, schema: Optional[str] = None) -> list[str]:
        """Retrieve the primary key column names for the specified table."""
        full_table_name = self.get_full_table_name(table, schema)
        logger.info(f"Fetching primary keys for: {full_table_name}")
        try:
            inspector = inspect(self._get_engine())
            pk_constraint = inspector.get_pk_constraint(table, schema=schema)
            pks = pk_constraint.get("constrained_columns", [])
            if not pks:
                logger.info(f"No primary key found for {full_table_name}.")
            return pks
        except Exception as e:
            logger.error(f"Failed to fetch primary keys: {e}")
            raise

    # -------------------------------------------------------------------------
    # Database Specific Logic
    # -------------------------------------------------------------------------

    @final
    def insert_df(
        self,
        df: pd.DataFrame,
        table: str,
        schema: Optional[str] = None,
        if_exists: Literal["fail", "append"] = "fail",
    ) -> None:
        """Insert a pandas DataFrame into a database table."""
        full_table_name = self.get_full_table_name(table, schema)
        if df.empty:
            logger.warning(
                f"DataFrame is empty, skipping insert into {full_table_name}."
            )
            return

        logger.info(f"Inserting {len(df)} rows into {full_table_name}...")
        try:
            with self._get_engine().begin() as conn:
                self._insert_df(conn, df, table, schema, if_exists)
            logger.info("Bulk insert successful.")
        except Exception as e:
            logger.error(f"Bulk insert failed: {e}")
            raise

    @abstractmethod
    def _insert_df(
        self,
        conn: Connection,
        df: pd.DataFrame,
        table: str,
        schema: Optional[str] = None,
        if_exists: Literal["fail", "append"] = "fail",
    ):
        pass

    @final
    def upsert_df(
        self,
        df: pd.DataFrame,
        table: str,
        schema: Optional[str] = None,
        pk_cols: Optional[list[str]] = None,
    ) -> None:
        """Upsert (Update or Insert) a DataFrame into a database table."""
        full_table_name = self.get_full_table_name(table, schema)
        if df.empty:
            logger.warning(f"DataFrame is empty, skipping upsert to {full_table_name}.")
            return

        if pk_cols is None:
            pk_cols = self.get_pk_columns(table, schema)
            if not pk_cols:
                raise ValueError(
                    f"Cannot upsert into '{full_table_name}': Table has no Primary Key."
                )

        if not pk_cols:
            raise ValueError(
                f"Cannot upsert into '{full_table_name}': No primary key columns specified."
            )

        missing_pk_in_df = set(pk_cols) - set(df.columns)
        if missing_pk_in_df:
            raise ValueError(f"DataFrame is missing pk columns: {missing_pk_in_df}")

        with self._get_engine().begin() as conn:
            self._upsert_df(conn, df, pk_cols, table, schema)

    @abstractmethod
    def _upsert_df(
        self,
        conn: Connection,
        df: pd.DataFrame,
        pk_cols: list[str],
        table: str,
        schema: Optional[str] = None,
    ):
        pass

    @abstractmethod
    def list_procedures(self, schema: Optional[str] = None) -> list[str]:
        """List stored procedures in the specified schema."""
        pass
