from pathlib import Path

from database.config import PostgresConfig
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ENV_PATH = Path(__file__).resolve().parents[2] / "dev.env"
config = PostgresConfig(_env_file=ENV_PATH)  # type: ignore[call-arg]

engine = create_engine(config.connection_uri_psycopg(), pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency that provides a database session.
    Yields a database session and closes it after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
