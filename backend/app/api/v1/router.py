"""
API v1 router — aggregates all v1 sub-routers.
"""

from fastapi import APIRouter

from app.api.v1 import healing, tasks

api_router = APIRouter()
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(healing.router, prefix="/healing", tags=["healing"])
