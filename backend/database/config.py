"""pydantic model for database configuration."""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


class PostgresConfig(BaseSettings):
    host: str = Field(
        "localhost",
        description="PostgreSQL server host",
    )
    port: int = Field(5432, ge=1, le=65535, description="Port number")
    user: str = Field(..., description="Username for the PostgreSQL server", alias="postgres_user")
    password: SecretStr = Field(..., description="Password for the PostgreSQL server", alias="postgres_password")
    database: str = Field(..., description="Database name", alias="postgres_db")

    def connection_uri(self) -> str:
        # Returns a PostgreSQL URI string for SQLAlchemy or psycopg
        return f"postgresql://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.database}"

    def connection_uri_psycopg(self) -> str:
        # Returns a PostgreSQL URI string for psycopg
        return (
            f"postgresql+psycopg://{self.user}:{self.password.get_secret_value()}@"
            f"{self.host}:{self.port}/{self.database}"
        )

    model_config = {"extra": "ignore"}
