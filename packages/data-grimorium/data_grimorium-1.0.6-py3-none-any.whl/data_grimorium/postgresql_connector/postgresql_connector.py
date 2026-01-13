"""
The module includes the PostgreSQL connector to interact
with the PostgreSQL database.
"""

# Import Standard Libraries
import logging
import psycopg2
import pandas as pd
from pathlib import Path
from typing import Union
from sqlalchemy import create_engine


# Import Package Modules
from data_grimorium.general_utils.general_utils import read_file_from_path
from data_grimorium.postgresql_connector.postgresql_types import (
    PostgreSQLClientConfig,
    PostgreSQLQueryConfig,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M",
)


class PostgreSQLConnector:
    """
    The class implements a PostgreSQL Connector
    in order to query PostgreSQL datasets and tables.

    Attributes:
        _root_path (pathlib.Path): Root path of the project
        _client_config (PostgreSQLClientConfig): Client configurations
    """

    def __init__(self, client_config: PostgreSQLClientConfig, root_path: Path):
        """
        Constructor of the class PostgreSQLConnector

        Args:
            client_config (PostgreSQLClientConfig): Config for instance a PostgreSQL Client
        """
        # Initialise attributes
        self._client_config = client_config
        self._root_path = root_path

    def _get_connection(self, schema: str | None = None):
        """
        Creates and returns a new PostgreSQL connection.
        """
        # Open connection
        connection = psycopg2.connect(**self._client_config.model_dump())

        # Use schema when present
        if schema:
            with connection.cursor() as cur:
                cur.execute("SET search_path TO %s", (schema,))
                connection.commit()

        logging.info(
            f"🛢 Connected to database {connection.info.dbname}"
            + (f" | schema={schema}" if schema else "")
        )

        return connection

    def execute_query_from_config(
        self, query_config: PostgreSQLQueryConfig
    ) -> Union[pd.DataFrame, bool]:
        """
        Execute a query from local path and with a certain set of parameter configurations.

        Args:
            query_config (PostgreSQLQueryConfig): Query configuration

        Returns:
            (Union[pd.DataFrame, bool]): The result of the query execution.
            Either the data or a bool in case of table creation.
        """
        # Check if the schema already exists, otherwise create it
        if not self.schema_exists(query_config.schema):
            logging.info(f"📝 Creating schema {query_config.schema}")
            try:
                with self._get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute(f"CREATE SCHEMA {query_config.schema}")
                        conn.commit()
            except psycopg2.Error as e:
                logging.error(f"❌ Database error: {e}")
                raise

        # Retrieve query path
        query_path = Path(query_config.query_path)

        # Read query
        query = read_file_from_path(query_path, self._root_path)

        # Execute within a context manager to auto-close connection
        try:
            with self._get_connection(schema=query_config.schema) as conn:
                with conn.cursor() as cur:
                    # Execute the query with the parameters (if present)
                    cur.execute(query, query_config.query_parameters or None)

                    # If query returns data (e.g., SELECT), fetch into DataFrame
                    if cur.description:
                        columns = [desc[0] for desc in cur.description]
                        data = cur.fetchall()
                        result = pd.DataFrame(data, columns=columns)
                    else:
                        result = True  # For CREATE, INSERT, UPDATE, etc.

                    conn.commit()
                    logging.info(f"✅ Query executed successfully from {query_path}")
                    return result

        except psycopg2.Error as e:
            logging.error(f"❌ Database error: {e}")
            raise

    def schema_exists(self, schema: str) -> bool:
        """
        Check if a schema exists in the database.

        Args:
            schema (str): Name of the schema to check.

        Returns:
            (bool): True if the schema exists, False otherwise.
        """
        # Execute within a context manager to auto-close connection
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT schema_name FROM information_schema.schemata WHERE schema_name=%s",
                        (schema,),
                    )
                    conn.commit()

                    logging.info(f"🕵🏻 Schema {schema} exists? → {bool(cur.rowcount)}")

                    return bool(cur.rowcount)

        except psycopg2.Error as e:
            logging.error(f"❌ Database error: {e}")
            raise

    def table_exists(self, table_name: str, schema: str | None = None) -> bool:
        """
        Check if a table exists in the database.

        Args:
            table_name (str): Name of the table to check.
            schema (str): Name of the schema to use

        Returns:
            (bool): True if the table exists, False otherwise.
        """
        # Execute within a context manager to auto-close connection
        try:
            with self._get_connection(schema=schema) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "select * from information_schema.tables where table_name=%s", (table_name,)
                    )
                    conn.commit()

                    logging.info(f"🕵🏻 Table {table_name} exists? → {bool(cur.rowcount)}")

                    return bool(cur.rowcount)

        except psycopg2.Error as e:
            logging.error(f"❌ Database error: {e}")
            raise

    def upload_dataframe(
        self, data: pd.DataFrame, table_name: str, schema: str = "public", replace: bool = False
    ) -> Union[int, None]:
        """
        Upload a DataFrame to a PostgreSQL table.

        Args:
            data (pd.DataFrame): Data to upload.
            table_name (str): Name of the table.
            schema (str): Name of the schema to use
            replace (bool): If True, replace the rows if it already exists.

        Returns:
            (Union[int, None]): Number of affected rows or None if an error occurred
        """
        # Check if the DataFrame is empty
        if data.empty:
            raise ValueError("🚨 The provided DataFrame is empty and cannot be uploaded.")

        # Check if the schema already exists, otherwise create it
        if not self.schema_exists(schema):
            logging.info(f"📝 Creating schema {schema}")
            try:
                with self._get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute(f"CREATE SCHEMA {schema}")
                        conn.commit()
            except psycopg2.Error as e:
                logging.error(f"❌ Database error: {e}")
                raise

        # Setup SQLAlchemy engine
        engine = create_engine(self._client_config.as_sqlalchemy_engine_url())
        mode = "replace" if replace else "append"

        logging.info(
            f"🪁 Upload {len(data)} into the table {self._client_config.dbname}.{table_name}"
        )

        # Load the DataFrame to PostgreSQL
        rows = data.to_sql(name=table_name, con=engine, if_exists=mode, schema=schema, index=False)

        # Check the result
        if rows is None:
            raise RuntimeError(f"❌ Upload failed: Pandas returned None for {table_name}")
        else:
            logging.info(f"✅ Data uploaded to {self._client_config.dbname}.{table_name}")

        return rows
