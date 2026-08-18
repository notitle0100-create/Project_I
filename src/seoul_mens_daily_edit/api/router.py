from fastapi import APIRouter

from seoul_mens_daily_edit.api.health import router as health_router

api_router = APIRouter()
api_router.include_router(health_router)
