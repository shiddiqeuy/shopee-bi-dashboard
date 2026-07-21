from __future__ import annotations

from fastapi import APIRouter, Depends

from database.repository import DuckDBRepository
from backend.deps import get_repo
from streamlit_app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/compute")
def compute_analytics(repo: DuckDBRepository = Depends(get_repo)):
    service = AnalyticsService(repo)
    results = service.compute_all()

    raw_df = repo.query("SELECT * FROM orders LIMIT 5000")
    results["raw_data"] = raw_df.to_dicts()

    return results
