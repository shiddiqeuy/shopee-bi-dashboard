from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends

from database.repository import DuckDBRepository
from backend.deps import get_repo
from streamlit_app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/compute")
async def compute_analytics(repo: DuckDBRepository = Depends(get_repo)):
    service = AnalyticsService(repo)
    results = await asyncio.to_thread(service.compute_all)

    raw_df = await asyncio.to_thread(repo.query, "SELECT * FROM orders LIMIT 5000")
    results["raw_data"] = raw_df.to_dicts()

    return results
