from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from seoul_mens_daily_edit.api.router import api_router
from seoul_mens_daily_edit.core.config import Settings, get_settings
from seoul_mens_daily_edit.core.logging import configure_logging
from seoul_mens_daily_edit.db.session import build_database


def create_app(settings: Settings | None = None) -> FastAPI:
    active_settings = settings or get_settings()
    database = build_database(active_settings)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        configure_logging(active_settings.log_level)
        try:
            yield
        finally:
            database.engine.dispose()

    app = FastAPI(
        title="SEOUL MEN'S DAILY EDIT",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.state.settings = active_settings
    app.state.database = database
    app.include_router(api_router)
    return app
