from fastapi import APIRouter
from .healthcheck import router as healthcheck_router
from .db import router as db_router

router = APIRouter()
router.include_router(healthcheck_router)
router.include_router(db_router)