from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, UploadFile, File

from database.repository import DuckDBRepository
from backend.deps import get_repo
from streamlit_app.services.etl_service import ETLService

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), repo: DuckDBRepository = Depends(get_repo)):
    service = ETLService(repo)
    contents = await file.read()
    saved_path = await asyncio.to_thread(service.save_upload, contents, file.filename)
    result = await asyncio.to_thread(service.run, str(saved_path))
    return {
        "filename": file.filename,
        "rows_loaded": result.get("rows_loaded", 0),
        "warehouse_built": result.get("warehouse_built", False),
        "total_rows": result.get("total_rows", 0),
        "status": result.get("status", "error"),
    }


@router.get("/status")
def etl_status(repo: DuckDBRepository = Depends(get_repo)):
    try:
        count = repo.staging_count()
        return {"data_available": count > 0, "total_rows": count}
    except Exception:
        return {"data_available": False, "total_rows": 0}
