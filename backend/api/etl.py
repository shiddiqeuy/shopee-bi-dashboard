from __future__ import annotations

import json
import shutil
from pathlib import Path

from fastapi import APIRouter, Request, UploadFile, File

from config.config import INPUT_DIR
from streamlit_app.services.etl_service import ETLService

router = APIRouter()


@router.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    repo = request.app.state.repo
    service = ETLService(repo)

    contents = await file.read()
    saved_path = service.save_upload(contents, file.filename)

    result = service.run(str(saved_path))
    return {
        "filename": file.filename,
        "rows_loaded": result.get("rows_loaded", 0),
        "warehouse_built": result.get("warehouse_built", False),
        "total_rows": result.get("total_rows", 0),
        "status": result.get("status", "error"),
    }


@router.get("/status")
def etl_status(request: Request):
    repo = request.app.state.repo
    try:
        count = repo.staging_count()
        return {"data_available": count > 0, "total_rows": count}
    except Exception:
        return {"data_available": False, "total_rows": 0}
