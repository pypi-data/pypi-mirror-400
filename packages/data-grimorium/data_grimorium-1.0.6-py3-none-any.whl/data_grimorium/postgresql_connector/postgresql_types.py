"""
The module includes Pydantic types for PostgreSQL Connector.
"""

# Import Standard Modules
import pandas as pd
from typing import Dict, Any
from pydantic import BaseModel, Field


class PostgreSQLClientConfig(BaseModel):
    """
    PostgreSQL client configuration.

    Attributes:
        dbname (str): Database name.
        user (str): Username.
        password (str): Password.
        host (str): Host URL.
        port (str): Port number.
    """

    dbname: str = Field(..., description="Database name", alias="dbname")
    user: str = Field(..., description="Username", alias="user")
    password: str = Field(..., description="Password", alias="password")
    host: str = Field(..., description="Host URL", alias="host")
    port: int = Field(..., description="Port number", alias="port")

    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Return the JSON schema.
        """
        return {
            "type": "object",
            "description": "PostgreSQL client configuration.",
            "properties": {
                "dbname": {
                    "type": "string",
                    "description": "Database name.",
                },
                "user": {
                    "type": "string",
                    "description": "Username.",
                },
                "password": {
                    "type": "string",
                    "description": "User password.",
                },
                "host": {
                    "type": "string",
                    "description": "Host url.",
                },
                "port": {
                    "type": "integer",
                    "description": "Port number.",
                },
            },
            "required": ["dbname", "user", "password", "host", "port"],
        }

    def as_dict(self) -> Dict[str, Any]:
        """
        Return the model as a Python dictionary (using field aliases).
        """
        return self.model_dump(by_alias=True)

    def as_json(self) -> str:
        """
        Return the model as a JSON string (with indentation for readability).
        """
        return self.model_dump_json(by_alias=True, indent=2)

    def as_df(self) -> pd.DataFrame:
        """
        Return the model as a single-row pandas DataFrame.
        """
        return pd.DataFrame([self.as_dict()])

    def as_sqlalchemy_engine_url(self):
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"


class PostgreSQLQueryConfig(BaseModel):
    """
    PostgreSQL query configuration with information on how to execute the query.

    Attributes:
        query_path (str): Path to the query file.
        schema (str): Schema name (``public`` default)
        local_path (str): [Optional] Local path where to save the data
        table_name (str): [Optional] Table name
        query_parameters (dict): [Optional] Query parameters
    """

    query_path: str = Field(..., description="Path to the query file", alias="query_path")
    schema: str = Field("public", description="Schema name", alias="schema")
    local_path: str = Field(
        None, description="Local path where to save the data", alias="local_path"
    )
    table_name: str = Field(None, description="Table name", alias="table_name")
    query_parameters: Dict[str, Any] = Field(
        None, description="Query parameters", alias="query_parameters"
    )

    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Return the JSON schema.
        """
        return {
            "type": "object",
            "description": "PostgreSQL query configuration with information on how to execute the query.",
            "properties": {
                "query_path": {
                    "type": "string",
                    "description": "Path to the query file.",
                },
                "schema": {
                    "type": "string",
                    "default": "public",
                    "description": "Schema name.",
                },
                "local_path": {
                    "type": ["string", "null"],
                    "description": "Local path where to save the data.",
                },
                "table_name": {
                    "type": ["string", "null"],
                    "description": "Table name.",
                },
                "query_parameters": {
                    "type": ["Dict[str, Any]", "null"],
                    "description": "Query parameters.",
                },
            },
            "required": ["query_path"],
        }

    def as_dict(self) -> Dict[str, Any]:
        """
        Return the model as a Python dictionary (using field aliases).
        """
        return self.model_dump(by_alias=True)

    def as_json(self) -> str:
        """
        Return the model as a JSON string (with indentation for readability).
        """
        return self.model_dump_json(by_alias=True, indent=2)

    def as_df(self) -> pd.DataFrame:
        """
        Return the model as a single-row pandas DataFrame.
        """
        return pd.DataFrame([self.as_dict()])
