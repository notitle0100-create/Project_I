from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from seoul_mens_daily_edit.core.config import Settings


@dataclass(frozen=True)
class Database:
    engine: Engine
    session_factory: sessionmaker[Session]


def build_database(settings: Settings) -> Database:
    engine = create_engine(
        settings.database_url.unicode_string(),
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5,
        pool_timeout=30,
    )
    return Database(
        engine=engine,
        session_factory=sessionmaker(bind=engine, autoflush=False, expire_on_commit=False),
    )


def check_database_connection(database: Database) -> None:
    with database.engine.connect() as connection:
        connection.execute(text("SELECT 1"))
