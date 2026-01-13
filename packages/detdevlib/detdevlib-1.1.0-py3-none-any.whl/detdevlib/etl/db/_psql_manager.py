# detdevlib.etl.db._psql_manager

import csv
import uuid
from io import StringIO
from typing import Literal, Optional

import pandas as pd
from pydantic import SecretStr, validate_call
from sqlalchemy import URL, Connection

from detdevlib.etl.db._base_manager import DatabaseManager


class PSQLManager(DatabaseManager):
    """PostgreSQL implementation of DatabaseManager."""

    @validate_call
    def __init__(
        self,
        hostname: str,
        database: str,
        username: str,
        password: SecretStr,
        port: int = 5432,
    ):
        """Initialize the PSQLManager."""
        super().__init__()
        self.hostname = hostname
        self.database = database
        self.username = username
        self.password = password
        self.port = port

    def _get_connection_url(self) -> URL:
        """Constructs the postgresql+psycopg2 connection URL."""
        return URL.create(
            "postgresql+psycopg2",
            username=self.username,
            password=self.password.get_secret_value(),
            host=self.hostname,
            port=self.port,
            database=self.database,
        )

    def list_procedures(self, schema: Optional[str] = None) -> list[str]:
        """Lists procedures from information_schema.routines."""
        if schema is None:
            schema = "public"

        query = """
            SELECT routine_name
            FROM information_schema.routines
            WHERE specific_schema = :schema AND routine_type = 'PROCEDURE'
            ORDER BY routine_name;
        """
        df = self.execute_query(query, params={"schema": schema})
        if df.empty:
            return []
        return df.iloc[:, 0].tolist()

    @staticmethod
    def _psql_insert_copy(table, conn, keys, data_iter):
        """Custom execution method for pandas `to_sql` to use PostgreSQL COPY."""
        dbapi_conn = conn.connection
        null_marker = f"NULL_{uuid.uuid4().hex}"

        def clean_data(data):
            for row in data:
                # Replace Python None with our custom null marker
                yield [null_marker if x is None else x for x in row]

        with dbapi_conn.cursor() as cur:
            s_buf = StringIO()
            writer = csv.writer(s_buf)
            writer.writerows(clean_data(data_iter))
            s_buf.seek(0)

            # handle quoting manually for the COPY statement
            table_name = f'"{table.name}"'
            if table.schema:
                table_name = f'"{table.schema}".{table_name}'

            columns = ", ".join(f'"{k}"' for k in keys)

            sql = f"COPY {table_name} ({columns}) FROM STDIN WITH (FORMAT CSV, NULL '{null_marker}')"
            cur.copy_expert(sql=sql, file=s_buf)

    def _insert_df(
        self,
        conn: Connection,
        df: pd.DataFrame,
        table: str,
        schema: Optional[str] = None,
        if_exists: Literal["fail", "append"] = "fail",
    ):
        """Overrides insert to use the high-performance COPY method."""
        df.to_sql(
            name=table,
            con=conn,
            schema=schema,
            if_exists=if_exists,
            index=False,
            chunksize=10000,  # Larger chunksize is safe with COPY
            method=self._psql_insert_copy,
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
        temp_table_name = f"tmp_{uuid.uuid4().hex}"
        temp_name = self.get_full_table_name(temp_table_name, schema)

        # ON COMMIT DROP: Automatically drops table at end of transaction block
        create_temp_sql = f"""
            CREATE TEMP TABLE {temp_name} 
            ON COMMIT DROP 
            AS SELECT * FROM {target_name} WHERE 0 = 1
        """
        self._execute_statement(conn, create_temp_sql)

        self._insert_df(conn, df, temp_table_name, schema=schema, if_exists="append")

        columns = list(df.columns)
        cols_str = ", ".join(self.quote(c) for c in columns)
        keys_str = ", ".join(self.quote(c) for c in pk_cols)

        update_cols = [c for c in columns if c not in pk_cols]
        on_conflict_action = "DO NOTHING"

        if update_cols:
            update_stmt = ", ".join(
                f"{self.quote(c)} = EXCLUDED.{self.quote(c)}" for c in update_cols
            )
            on_conflict_action = f"DO UPDATE SET {update_stmt}"

        upsert_sql = f"""
            INSERT INTO {target_name} ({cols_str})
            SELECT {cols_str} FROM {self.quote(temp_table_name)}
            ON CONFLICT ({keys_str})
            {on_conflict_action};
        """

        self._execute_statement(conn, upsert_sql)
