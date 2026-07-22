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
    return repo


@pytest.fixture
def client(mock_repo):
    app.dependency_overrides[get_repo] = lambda: mock_repo
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestFilesAPI:
    @patch("backend.api.files.ETLService.list_files")
    def test_list_files(self, mock_list, client):
        mock_list.return_value = [{"name": "test.xlsx", "size": 100, "size_display": "100 B", "modified": 1234567890}]
        resp = client.get("/api/files/")
        assert resp.status_code == 200
        assert resp.json() == {"files": [{"name": "test.xlsx", "size": 100, "size_display": "100 B", "modified": 1234567890}]}

    @patch("backend.api.files.ETLService.delete_file")
    def test_delete_file(self, mock_delete, client):
        mock_delete.return_value = True
        resp = client.delete("/api/files/test.xlsx")
        assert resp.status_code == 200
        assert resp.json() == {"deleted": True}
        mock_delete.assert_called_once_with("test.xlsx")

    @patch("backend.api.files.ETLService.clear_all")
    def test_clear_files(self, mock_clear, client):
        mock_clear.return_value = 3
        resp = client.post("/api/files/clear")
        assert resp.status_code == 200
        assert resp.json() == {"deleted_count": 3}

    @patch("backend.api.files.ETLService")
    @patch("backend.api.files.asyncio.to_thread", side_effect=lambda fn, *a, **kw: fn(*a, **kw))
    def test_replace_file(self, mock_to_thread, mock_etl_service_class, client, mock_repo):
        instance = mock_etl_service_class.return_value
        instance.save_upload.return_value = Path("/tmp/test.xlsx")
        instance.run.return_value = {
            "rows_loaded": 30,
            "warehouse_built": True,
            "total_rows": 30,
            "status": "success",
        }

        resp = client.put(
            "/api/files/test.xlsx",
            files={"file": ("test.xlsx", b"new content", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["filename"] == "test.xlsx"
        assert data["replaced"] is True
        assert data["rows_loaded"] == 30
        assert data["status"] == "success"
        instance.save_upload.assert_called_once()
        instance.run.assert_called_once()
