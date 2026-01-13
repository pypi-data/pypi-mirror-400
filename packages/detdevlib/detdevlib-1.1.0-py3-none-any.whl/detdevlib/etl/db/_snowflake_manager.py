# detdevlib.etl.db._snowflake_manager

import uuid
from typing import Literal, Optional

import pandas as pd
from pydantic import SecretStr, validate_call
from sqlalchemy import URL, Connection

from detdevlib.etl.db._base_manager import DatabaseManager
from detdevlib.utils.etc import clean_dict


class SnowflakeManager(DatabaseManager):
    """Snowflake implementation of DatabaseManager."""

    @validate_call
    def __init__(
        self,
        account: str,
        username: str,
        password: SecretStr,
        database: str,
        schema_name: str,
        warehouse: str,
        role: Optional[str] = None,
    ):
        """Initialize the SnowflakeManager."""
        super().__init__()
        self.account = account
        self.username = username
        self.password = password
        self.database = database
        self.schema_name = schema_name
        self.warehouse = warehouse
        self.role = role

    def _get_connection_url(self) -> URL:
        """Constructs the snowflake connection URL."""
        return URL.create(
            "snowflake",
            username=self.username,
            password=self.password.get_secret_value(),
            host=self.account,
            database=f"{self.database}/{self.schema_name}",
            query=clean_dict(
                {
                    "warehouse": self.warehouse,
                    "role": self.role,
                }
            ),
        )

    def list_procedures(self, schema: Optional[str] = None) -> list[str]:
        """Lists procedures from information_schema.procedures."""
        query = """
            SELECT procedure_name
            FROM information_schema.procedures
            WHERE procedure_schema = :schema
            ORDER BY procedure_name; 
        """
        # Snowflake metadata is often uppercase
        target_schema = (schema or self.schema_name).upper()
        df = self.execute_query(query, params={"schema": target_schema})
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
        # Snowflake typically prefers 'multi' or standard inserts for smaller batches
        # For very large batches, pd_writer (bulk load) is preferred but requires optional deps.
        # We stick to standard SQL method here for compatibility.
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

        # Create Temp Table (Snowflake supports CREATE TABLE ... LIKE)
        self._execute_statement(conn, f"CREATE TABLE {temp_name} LIKE {target_name}")

        try:
            self._insert_df(conn, df, temp_table, schema, if_exists="append")

            join_cond = " AND ".join(
                f"target.{self.quote(c)} = source.{self.quote(c)}" for c in pk_cols
            )

            columns = list(df.columns)
            update_cols = [c for c in columns if c not in pk_cols]

            # Construct MERGE
            merge_sql = f"MERGE INTO {target_name} AS target USING {temp_name} AS source ON {join_cond}"

            if update_cols:
                update_stmt = ", ".join(
                    f"target.{self.quote(c)} = source.{self.quote(c)}"
                    for c in update_cols
                )
                merge_sql += f" WHEN MATCHED THEN UPDATE SET {update_stmt}"

            cols_str = ", ".join(self.quote(c) for c in columns)
            src_cols_str = ", ".join(f"source.{self.quote(c)}" for c in columns)

            merge_sql += (
                f" WHEN NOT MATCHED THEN INSERT ({cols_str}) VALUES ({src_cols_str});"
            )

            self._execute_statement(conn, merge_sql)

        finally:
            self._execute_statement(conn, f"DROP TABLE IF EXISTS {temp_name}")
