# detdevlib.etl.db._mysql_manager

import uuid
from typing import Literal, Optional

import pandas as pd
from pydantic import SecretStr, validate_call
from sqlalchemy import URL, Connection

from detdevlib.etl.db._base_manager import DatabaseManager


class MySQLManager(DatabaseManager):
    """MySQL implementation of DatabaseManager."""

    @validate_call
    def __init__(
        self,
        hostname: str,
        database: str,
        username: str,
        password: SecretStr,
        port: int = 3306,
    ):
        """Initialize the MySQLManager."""
        super().__init__()
        self.hostname = hostname
        self.database = database
        self.username = username
        self.password = password
        self.port = port

    def _get_connection_url(self) -> URL:
        """Constructs the mysql+pymysql connection URL."""
        return URL.create(
            "mysql+pymysql",
            username=self.username,
            password=self.password.get_secret_value(),
            host=self.hostname,
            port=self.port,
            database=self.database,
        )

    @staticmethod
    def quote(identifier: str) -> str:
        """Overrides default quoting to use backticks."""
        return f"`{identifier.replace('`', '``')}`"

    def list_procedures(self, schema: Optional[str] = None) -> list[str]:
        """Lists procedures from information_schema.routines."""
        query = """
            SELECT ROUTINE_NAME
            FROM INFORMATION_SCHEMA.ROUTINES
            WHERE ROUTINE_TYPE = 'PROCEDURE' AND ROUTINE_SCHEMA = :schema
            ORDER BY ROUTINE_NAME;
        """
        # Default to the connected database if schema is not provided
        params = {"schema": schema or self.database}
        df = self.execute_query(query, params=params)
        if df.empty:
            return []
        return df.iloc[:, 0].tolist()

    def _insert_df(
        self,
        conn: Connection,
        df: pd.DataFrame,
        table: str,
        schema: Optional[str] = None,
        if_exists: Literal["fail", "append"] = "fail",
    ):
        df.to_sql(
            name=table,
            con=conn,
            schema=schema,
            if_exists=if_exists,
            index=False,
            chunksize=1000,
            method="multi",
        )

    def _upsert_df(
        self,
        conn: Connection,
        df: pd.DataFrame,
        pk_cols: list[str],
        table: str,
        schema: Optional[str] = None,
    ):
        # Stage data in a temporary table
        target_name = self.get_full_table_name(table, schema)
        temp_table = f"tmp_{uuid.uuid4().hex}"
        temp_name = self.get_full_table_name(temp_table, schema)

        # Create temp table with same structure (LIKE)
        # This commits, which is fine because we drop the table at the end via finally.
        self._execute_statement(conn, f"CREATE TABLE {temp_name} LIKE {target_name}")

        try:
            # Insert data into temp table
            self._insert_df(conn, df, temp_table, schema, if_exists="append")

            # Construct Upsert SQL (ON DUPLICATE KEY UPDATE)
            columns = list(df.columns)
            cols_str = ", ".join(self.quote(c) for c in columns)

            update_cols = [c for c in columns if c not in pk_cols]

            if not update_cols:
                # Dummy update to satisfy syntax if only PKs exist
                pk = pk_cols[0]
                update_stmt = f"{self.quote(pk)} = {self.quote(pk)}"
            else:
                # Use VALUES() reference for MySQL 8.0+ compatibility
                update_stmt = ", ".join(
                    f"{self.quote(c)} = VALUES({self.quote(c)})" for c in update_cols
                )

            upsert_sql = f"""
                INSERT INTO {target_name} ({cols_str})
                SELECT {cols_str} FROM {temp_name}
                ON DUPLICATE KEY UPDATE {update_stmt};
            """

            self._execute_statement(conn, upsert_sql)

        finally:
            self._execute_statement(conn, f"DROP TABLE IF EXISTS {temp_name}")
