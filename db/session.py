from contextlib import contextmanager
from typing import Iterator, Optional
import os

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

from config.settings import settings

# Optional: Cloud SQL Python Connector (only needed on GCP when using IAM auth)
_connector = None  # type: ignore[var-annotated]

_engine: Optional[Engine] = None
_SessionLocal: Optional[sessionmaker] = None


def _make_cloudsql_engine() -> Engine:
    """
    Create an Engine using Cloud SQL Python Connector with IAM auth (no JSON key).
    Required envs:
      - CLOUD_SQL_CONNECTION_NAME: "project:region:instance"
      - DB_USER: Cloud SQL user (e.g., postgres)
      - DB_NAME: database name
    Optional envs:
      - DB_PASSWORD: if using password auth (not needed for IAM if configured)
    """
    from google.cloud.sql.connector import Connector
    import pg8000

    connection_name = os.getenv("CLOUD_SQL_CONNECTION_NAME")
    db_user = os.getenv("DB_USER", "postgres")
    db_name = os.getenv("DB_NAME", "postgres")
    db_password = os.getenv("DB_PASSWORD")  # optional

    if not connection_name:
        raise RuntimeError("CLOUD_SQL_CONNECTION_NAME is required for USE_IAM_AUTH=true")

    # Use a single Connector instance
    global _connector  # noqa: PLW0603
    if _connector is None:
        _connector = Connector()

    def getconn():
        return _connector.connect(
            connection_name,
            driver="pg8000",
            user=db_user,
            db=db_name,
            enable_iam_auth=True,
            password=db_password,
        )

    # Create SQLAlchemy engine using the connector
    engine = create_engine(
        "postgresql+pg8000://",
        creator=getconn,
        pool_pre_ping=True,
        future=True,
    )
    return engine


def get_engine() -> Engine:
    global _engine, _SessionLocal
    if _engine is None:
        use_iam = os.getenv("USE_IAM_AUTH", "false").lower() in ("1", "true", "yes")
        if settings.database_url:
            _engine = create_engine(settings.database_url, pool_pre_ping=True, future=True)
        elif use_iam:
            _engine = _make_cloudsql_engine()
        else:
            raise RuntimeError(
                "No database configuration provided. Set DATABASE_URL or USE_IAM_AUTH=true with CLOUD_SQL_CONNECTION_NAME/DB_USER/DB_NAME."
            )
        _SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False, future=True)
    return _engine


@contextmanager
def get_session() -> Iterator[Session]:
    if _SessionLocal is None:
        get_engine()
    assert _SessionLocal is not None
    session = _SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def ping() -> bool:
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
