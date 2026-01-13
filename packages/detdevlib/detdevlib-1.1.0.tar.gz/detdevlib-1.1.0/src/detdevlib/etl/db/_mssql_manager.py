# detdevlib.etl.db._mssql_manager

import uuid
from typing import Literal, Optional

import pandas as pd
from pydantic import SecretStr, validate_call
from sqlalchemy import URL, Connection

from detdevlib.etl.db._base_manager import DatabaseManager


class MSSQLManager(DatabaseManager):
    """Microsoft SQL Server implementation of DatabaseManager."""

    @validate_call
    def __init__(
        self,
        hostname: str,
        database: str,
        username: str,
        password: SecretStr,
        port: Optional[int] = None,
        driver: str = "ODBC Driver 18 for SQL Server",
        trust_server_certificate: bool = False,
    ):
        """Initialize the MSSQLManager."""
        super().__init__()
        self.hostname = hostname
        self.database = database
        self.username = username
        self.password = password
        self.port = port
        self.driver = driver
        self.trust_server_certificate = trust_server_certificate

    def _get_connection_url(self) -> URL:
        return URL.create(
            "mssql+pyodbc",
            username=self.username,
            password=self.password.get_secret_value(),
            host=self.hostname,
            port=self.port,
            database=self.database,
            query={
                "driver": self.driver,
                "Encrypt": "yes",
                "TrustServerCertificate": (
                    "yes" if self.trust_server_certificate else "no"
                ),
                "ConnectionTimeout": "30",
            },
        )

    def _get_engine_kwargs(self) -> dict:
        """Enables fast_executemany for performance boost on bulk operations."""
        return {"fast_executemany": True}

    @staticmethod
    def quote(identifier: str) -> str:
        """Overrides default quoting to use T-SQL brackets."""
        return f"[{identifier.replace(']', ']]')}]"

    def list_procedures(self, schema: Optional[str] = None) -> list[str]:  # noqa: D102
        query = """
            SELECT ROUTINE_NAME
            FROM INFORMATION_SCHEMA.ROUTINES
            WHERE ROUTINE_TYPE = 'PROCEDURE'
        """
        params = {}
        if schema is not None:
            query += " AND ROUTINE_SCHEMA = :schema"
            params["schema"] = schema

        query += " ORDER BY ROUTINE_NAME;"
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
            method=None,  # for fast_executemany
        )

    def _upsert_df(
        self,
        conn: Connection,
        df: pd.DataFrame,
        pk_cols: list[str],
        table: str,
        schema: Optional[str] = None,
    ):
        # Generate names
        temp_table = f"tmp_{uuid.uuid4().hex}"
        target_name = self.get_full_table_name(table, schema)
        temp_name = self.get_full_table_name(temp_table, schema)

        # Create Staging Table
        create_sql = f"SELECT * INTO {temp_name} FROM {target_name} WHERE 1 = 0"
        self._execute_statement(conn, create_sql)

        try:
            # Bulk Insert into Staging
            self._insert_df(conn, df, temp_table, schema, if_exists="append")

            # Merge staging into the target table
            columns = list(df.columns)
            join_cond = " AND ".join(
                f"target.{self.quote(c)} = source.{self.quote(c)}" for c in pk_cols
            )

            update_cols = [c for c in columns if c not in pk_cols]
            update_clause = ""
            if update_cols:
                updates = ", ".join(
                    f"target.{self.quote(c)} = source.{self.quote(c)}"
                    for c in update_cols
                )
                update_clause = f"WHEN MATCHED THEN UPDATE SET {updates}"

            insert_cols = ", ".join(self.quote(c) for c in columns)
            insert_vals = ", ".join(f"source.{self.quote(c)}" for c in columns)

            merge_sql = f"""
                MERGE {target_name} WITH (HOLDLOCK) AS target
                USING {temp_name} AS source
                ON {join_cond}
                {update_clause}
                WHEN NOT MATCHED THEN INSERT ({insert_cols}) VALUES ({insert_vals});
            """

            final_sql = f"""
                DECLARE @has_identity INT = OBJECTPROPERTY(OBJECT_ID('{target_name.replace("'", "''")}'), 'TableHasIdentity');
                IF @has_identity = 1 SET IDENTITY_INSERT {target_name} ON;
    
                {merge_sql}
    
                IF @has_identity = 1 SET IDENTITY_INSERT {target_name} OFF;
            """

            self._execute_statement(conn, final_sql)

        finally:
            # Cleanup (Only needed on success; Rollback handles failure)
            self._execute_statement(conn, f"DROP TABLE IF EXISTS {temp_name}")
