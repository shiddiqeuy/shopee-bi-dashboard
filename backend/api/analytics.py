from __future__ import annotations

import asyncio
import traceback

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from database.repository import DuckDBRepository
from backend.deps import get_repo
from streamlit_app.services.analytics_service import AnalyticsService
from utils.logger import get_logger

log = get_logger(__name__)

router = APIRouter()


@router.get("/compute")
async def compute_analytics(repo: DuckDBRepository = Depends(get_repo)):
    try:
        service = AnalyticsService(repo)
        results = await asyncio.to_thread(service.compute_all)

        raw_df = await asyncio.to_thread(repo.query, "SELECT * FROM orders LIMIT 5000")
        results["raw_data"] = raw_df.to_dicts()

        return results
    except Exception:
        log.error("Analytics computation failed\n%s", traceback.format_exc())
        return JSONResponse(status_code=500, content={"detail": "Analytics computation failed"})
