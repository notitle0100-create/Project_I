from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from seoul_mens_daily_edit.core.config import Settings
from seoul_mens_daily_edit.db.session import Database, build_database, check_database_connection


def test_build_database_uses_postgres_engine_and_session_defaults(settings: Settings) -> None:
    database = build_database(settings)

    try:
        assert database.engine.url.drivername == "postgresql+psycopg"
        assert database.session_factory.kw["autoflush"] is False
        assert database.session_factory.kw["expire_on_commit"] is False
    finally:
        database.engine.dispose()


def test_check_database_connection_executes_minimal_query() -> None:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    database = Database(engine=engine, session_factory=sessionmaker[Session](bind=engine))

    try:
        check_database_connection(database)
    finally:
        engine.dispose()
