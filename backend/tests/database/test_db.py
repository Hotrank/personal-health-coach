from pathlib import Path

import psycopg
import pytest
from database.config import PostgresConfig

"""Test database connection and query execution.
This module contains tests for the database connection and query execution.
It uses pytest to run the tests and psycopg to connect to the PostgreSQL database.
"""

@pytest.fixture(scope="module")
def db_connection():
    """Fixture to create a database connection."""
    env_path = Path(__file__).resolve().parents[3] / "dev.env"
    config = PostgresConfig(_env_file=env_path)  # Load configuration from .env file
    conn = psycopg.connect(config.connection_uri())
    conn.autocommit = True
    # Yield the connection to be used in tests
    yield conn
    conn.close()


# Test database connection
def test_db_connection(db_connection):
    """Test if the database connection is established."""
    assert db_connection is not None
    assert db_connection.closed == 0  # 0 means the connection is open

# Test query execution
def test_query_execution(db_connection):
    """Test if a simple query can be executed."""
    with db_connection.cursor() as cursor:
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()
        assert result == (1,)