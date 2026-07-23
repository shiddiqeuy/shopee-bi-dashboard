from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import JSONResponse

from config.config import INPUT_DIR
from database.repository import DuckDBRepository
from backend.deps import get_repo
from etl.log_writer import ETLLogWriter
from streamlit_app.services.etl_service import ETLService
from utils.logger import get_logger, log_error_context

log = get_logger(__name__)

router = APIRouter()

PUBLIC_ETL_ERROR = "Upload atau proses ETL gagal. Cek backend log untuk detail teknis."


def _upload_context(file: UploadFile, contents: bytes | None = None) -> dict:
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": len(contents) if contents is not None else None,
    }


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), repo: DuckDBRepository = Depends(get_repo)):
    contents: bytes | None = None
    stage = "upload"
    try:
        service = ETLService(repo)
        contents = await file.read()
        await asyncio.to_thread(service.save_upload, contents, file.filename)
        stage = "etl"
        result = await asyncio.to_thread(service.rebuild_all)
        return {
            "filename": file.filename,
            "rows_loaded": result.get("rows_loaded", 0),
            "warehouse_built": result.get("warehouse_built", False),
            "total_rows": result.get("total_rows", 0),
            "status": result.get("status", "error"),
        }
    except Exception as exc:
        log_error_context(log, "ETL upload failed", exc=exc, stage=stage, **_upload_context(file, contents))
        return JSONResponse(status_code=500, content={"detail": PUBLIC_ETL_ERROR})


@router.post("/upload-multiple")
async def upload_multiple_files(files: list[UploadFile] = File(...), repo: DuckDBRepository = Depends(get_repo)):
    try:
        service = ETLService(repo)
        results = []
        uploaded_names = []
        for file in files:
            contents: bytes | None = None
            stage = "upload"
            try:
                contents = await file.read()
                await asyncio.to_thread(service.save_upload, contents, file.filename)
                uploaded_names.append(file.filename)
                results.append({
                    "filename": file.filename,
                    "rows_loaded": 0,
                    "warehouse_built": False,
                    "total_rows": 0,
                    "status": "success",
                })
            except Exception as e:
                log_error_context(log, "ETL upload failed for file", exc=e, stage=stage, **_upload_context(file, contents))
                results.append({
                    "filename": file.filename,
                    "rows_loaded": 0,
                    "warehouse_built": False,
                    "total_rows": 0,
                    "status": "error",
                    "error": PUBLIC_ETL_ERROR,
                })
        if uploaded_names:
            stage = "etl"
            rebuild = await asyncio.to_thread(service.rebuild_all)
            rebuilt_by_name = {r["filename"]: r for r in rebuild.get("results", [])}
            for result in results:
                if result["status"] == "success":
                    result.update(rebuilt_by_name.get(result["filename"], {
                        "warehouse_built": rebuild.get("warehouse_built", False),
                        "total_rows": rebuild.get("total_rows", 0),
                    }))
        return {"results": results}
    except Exception as exc:
        log_error_context(log, "ETL multiple upload failed", exc=exc, stage="upload")
        return JSONResponse(status_code=500, content={"detail": PUBLIC_ETL_ERROR})


@router.post("/reload/{filename}")
async def reload_file(filename: str, repo: DuckDBRepository = Depends(get_repo)):
    try:
        service = ETLService(repo)
        file_path = INPUT_DIR / filename
        if not file_path.exists() or not file_path.is_file():
            return JSONResponse(status_code=404, content={"detail": f"File {filename} not found"})
        rebuild = await asyncio.to_thread(service.rebuild_all)
        result = next((r for r in rebuild.get("results", []) if r.get("filename") == filename), rebuild)
        return {
            "filename": filename,
            "rows_loaded": result.get("rows_loaded", 0),
            "warehouse_built": result.get("warehouse_built", False),
            "total_rows": result.get("total_rows", 0),
            "status": result.get("status", "success"),
        }
    except Exception as exc:
        log_error_context(log, "ETL reload failed", exc=exc, stage="etl", filename=filename)
        return JSONResponse(status_code=500, content={"detail": PUBLIC_ETL_ERROR})


@router.post("/reload-all")
async def reload_all_files(repo: DuckDBRepository = Depends(get_repo)):
    try:
        service = ETLService(repo)
        result = await asyncio.to_thread(service.rebuild_all)
        return {"results": result.get("results", [])}
    except Exception as exc:
        log_error_context(log, "ETL reload-all failed", exc=exc, stage="etl")
        return JSONResponse(status_code=500, content={"detail": PUBLIC_ETL_ERROR})


@router.get("/status")
def etl_status(repo: DuckDBRepository = Depends(get_repo)):
    try:
        count = repo.staging_count()
        return {"data_available": count > 0, "total_rows": count}
    except Exception as exc:
        log_error_context(log, "ETL status check failed", exc=exc, stage="status")
        return JSONResponse(status_code=500, content={"detail": "ETL status check failed"})


@router.get("/logs")
def etl_logs(limit: int = 25):
    try:
        logs = ETLLogWriter().read_runs(limit)
        logs.reverse()
        return {"logs": logs}
    except Exception as exc:
        log_error_context(log, "ETL logs read failed", exc=exc, stage="logs")
        return JSONResponse(status_code=500, content={"detail": "ETL logs read failed"})


@router.get("/status/{filename}")
def file_etl_status(filename: str, repo: DuckDBRepository = Depends(get_repo)):
    try:
        file_path = INPUT_DIR / filename
        exists = file_path.exists() and file_path.is_file()
        if not exists:
            return JSONResponse(status_code=404, content={"detail": f"File {filename} not found"})
        count = repo.staging_count()
        return {
            "filename": filename,
            "exists": True,
            "status": "completed" if count > 0 else "pending",
            "total_rows": count,
        }
    except Exception as exc:
        log_error_context(log, "ETL file status check failed", exc=exc, stage="status", filename=filename)
        return JSONResponse(status_code=500, content={"detail": "ETL file status check failed"})
