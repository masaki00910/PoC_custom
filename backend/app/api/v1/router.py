from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.checks import router as checks_router

router = APIRouter()
router.include_router(checks_router)
