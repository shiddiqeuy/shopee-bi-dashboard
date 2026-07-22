from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.deps import get_repo
from backend.main import app


@pytest.fixture(autouse=True)
def _mock_pool_lifecycle():
    with (
        patch("backend.main.init_pool"),
        patch("backend.main.close_pool"),
    ):
        yield


@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.staging_count.return_value = 42
    return repo


@pytest.fixture
def client(mock_repo):
    app.dependency_overrides[get_repo] = lambda: mock_repo
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestETLStatus:
    def test_status_returns_data_available(self, client, mock_repo):
        mock_repo.staging_count.return_value = 5
        resp = client.get("/api/etl/status")
        assert resp.status_code == 200
        assert resp.json() == {"data_available": True, "total_rows": 5}

    def test_status_no_data(self, client, mock_repo):
        mock_repo.staging_count.return_value = 0
        resp = client.get("/api/etl/status")
        assert resp.status_code == 200
        assert resp.json() == {"data_available": False, "total_rows": 0}

    def test_status_error_returns_json_500(self, client, mock_repo):
        mock_repo.staging_count.side_effect = Exception("DB error")
        resp = client.get("/api/etl/status")
        assert resp.status_code == 500
        assert resp.json() == {"detail": "ETL status check failed"}

    def test_status_calls_staging_count(self, client, mock_repo):
        client.get("/api/etl/status")
        mock_repo.staging_count.assert_called_once()


class TestETLUpload:
    @patch("backend.api.etl.ETLService")
    @patch("backend.api.etl.asyncio.to_thread", side_effect=lambda fn, *a, **kw: fn(*a, **kw))
    def test_upload_success(self, mock_to_thread, mock_etl_service_class, client, mock_repo):
        instance = mock_etl_service_class.return_value
        instance.save_upload.return_value = Path("/tmp/upload.xlsx")
        instance.run.return_value = {
            "rows_loaded": 50,
            "warehouse_built": True,
            "total_rows": 50,
            "status": "success",
        }

        resp = client.post(
            "/api/etl/upload",
            files={"file": ("test.xlsx", b"sheet content", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )

        assert resp.status_code == 200
        assert resp.json() == {
            "filename": "test.xlsx",
            "rows_loaded": 50,
            "warehouse_built": True,
            "total_rows": 50,
            "status": "success",
        }

        mock_etl_service_class.assert_called_once_with(mock_repo)
        instance.save_upload.assert_called_once()
        instance.run.assert_called_once()

    @patch("backend.api.etl.ETLService")
    @patch("backend.api.etl.asyncio.to_thread", side_effect=lambda fn, *a, **kw: fn(*a, **kw))
    def test_upload_zero_rows(self, mock_to_thread, mock_etl_service_class, client, mock_repo):
        instance = mock_etl_service_class.return_value
        instance.save_upload.return_value = Path("/tmp/empty.xlsx")
        instance.run.return_value = {
            "rows_loaded": 0,
            "status": "success",
        }

        resp = client.post(
            "/api/etl/upload",
            files={"file": ("empty.xlsx", b"", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["rows_loaded"] == 0
        assert data["warehouse_built"] is False
        assert data["total_rows"] == 0
        assert data["status"] == "success"

    @patch("backend.api.etl.ETLService")
    @patch("backend.api.etl.asyncio.to_thread", side_effect=lambda fn, *a, **kw: fn(*a, **kw))
    def test_upload_error_returns_json_500(self, mock_to_thread, mock_etl_service_class, client, mock_repo):
        instance = mock_etl_service_class.return_value
        instance.save_upload.side_effect = Exception("Upload failed")

        resp = client.post(
            "/api/etl/upload",
            files={"file": ("bad.xlsx", b"corrupt", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )

        assert resp.status_code == 500
        assert resp.json() == {"detail": "ETL upload failed"}

    @patch("backend.api.etl.ETLService")
    @patch("backend.api.etl.asyncio.to_thread", side_effect=lambda fn, *a, **kw: fn(*a, **kw))
    def test_upload_multiple_success(self, mock_to_thread, mock_etl_service_class, client, mock_repo):
        instance = mock_etl_service_class.return_value
        instance.save_upload.side_effect = [Path("/tmp/test1.xlsx"), Path("/tmp/test2.xlsx")]
        instance.run.return_value = {
            "rows_loaded": 25,
            "warehouse_built": True,
            "total_rows": 50,
            "status": "success",
        }

        resp = client.post(
            "/api/etl/upload-multiple",
            files=[
                ("files", ("test1.xlsx", b"content1", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")),
                ("files", ("test2.xlsx", b"content2", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")),
            ],
        )

        assert resp.status_code == 200
        data = resp.json()
        assert "results" in data
        assert len(data["results"]) == 2
        assert data["results"][0]["filename"] == "test1.xlsx"
        assert data["results"][0]["rows_loaded"] == 25
        assert data["results"][1]["filename"] == "test2.xlsx"
