# detdevlib.etl.db._sqlite_manager

import uuid
from pathlib import Path
from typing import Literal, Optional

import pandas as pd
from pydantic import validate_call
from sqlalchemy import URL, Connection

from detdevlib.etl.db._base_manager import DatabaseManager, logger


class SQLiteManager(DatabaseManager):
    """SQLite implementation of DatabaseManager."""

    @validate_call
    def __init__(self, database: Path | Literal[":memory:"]):
        """Initialize the SQLiteManager."""
        super().__init__()
        self.database = database

    def _get_connection_url(self) -> str | URL:
        """Constructs the sqlite connection URL."""
        if self.database == ":memory:":
            return "sqlite://"
        return URL.create("sqlite", database=str(self.database.resolve()))

    def list_procedures(self, schema: Optional[str] = None) -> list[str]:  # noqa: D102
        logger.warning("SQLite does not support procedures. Returning empty list.")
        return []

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
        target_name = self.get_full_table_name(table, schema)
        temp_table = f"tmp_{uuid.uuid4().hex}"
        temp_name = self.get_full_table_name(temp_table, schema)

        # Create Temp Table
        create_sql = (
            f"CREATE TABLE {temp_name} AS SELECT * FROM {target_name} WHERE 0 = 1"
        )
        self._execute_statement(conn, create_sql)

        try:
            self._insert_df(conn, df, temp_table, schema, if_exists="append")

            columns = list(df.columns)
            keys_str = ", ".join(self.quote(c) for c in pk_cols)
            cols_str = ", ".join(self.quote(c) for c in columns)

            upsert_sql = f"""
                INSERT INTO {target_name} ({cols_str})
                SELECT {cols_str} FROM {temp_name}
                WHERE 1=1
                ON CONFLICT ({keys_str})
            """

            update_cols = [c for c in columns if c not in pk_cols]
            if not update_cols:
                upsert_sql += " DO NOTHING;"
            else:
                update_stmt = ", ".join(
                    f"{self.quote(c)} = excluded.{self.quote(c)}" for c in update_cols
                )
                upsert_sql += f" DO UPDATE SET {update_stmt};"

            self._execute_statement(conn, upsert_sql)

        finally:
            self._execute_statement(conn, f"DROP TABLE IF EXISTS {temp_name}")
