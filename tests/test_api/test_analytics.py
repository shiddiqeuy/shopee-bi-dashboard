from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.deps import get_repo
from backend.main import app

MODULE_NAMES = {
    "customer",
    "product",
    "city",
    "province",
    "trend",
    "shipping",
    "payment",
    "cancellation",
}

RAW_DATA_QUERY = "SELECT * FROM orders LIMIT 5000"


@pytest.fixture(autouse=True)
def _mock_pool_lifecycle():
    with (
        patch("backend.main.init_pool"),
        patch("backend.main.close_pool"),
    ):
        yield


@pytest.fixture
def mock_repo():
    return MagicMock()


@pytest.fixture
def client(mock_repo):
    app.dependency_overrides[get_repo] = lambda: mock_repo
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestAnalyticsCompute:
    @patch("backend.api.analytics.AnalyticsService")
    @patch(
        "backend.api.analytics.asyncio.to_thread",
        side_effect=lambda fn, *args, **kwargs: fn(*args, **kwargs),
    )
    def test_compute_returns_complete_response(
        self,
        mock_to_thread,
        mock_service_class,
        client,
        mock_repo,
    ):
        service = mock_service_class.return_value

        analytics_results = {
            "customer": {"total_customers": 10},
            "product": {"total_products": 5},
            "city": {"total_cities": 3},
            "province": {"total_provinces": 2},
            "trend": {"growth": 12.5},
            "shipping": {"providers": 2},
            "payment": {"methods": 3},
            "cancellation": {"rate": 1.5},
            "insights": [{"message": "Test insight"}],
        }
        service.compute_all.return_value = analytics_results.copy()

        raw_data = [{"order_id": "ORD-001"}]
        raw_df = MagicMock()
        raw_df.to_dicts.return_value = raw_data
        mock_repo.query.return_value = raw_df

        response = client.get("/api/analytics/compute")

        assert response.status_code == 200

        data = response.json()
        assert MODULE_NAMES.issubset(data)
        assert data["insights"] == analytics_results["insights"]
        assert data["raw_data"] == raw_data

        mock_service_class.assert_called_once_with(mock_repo)
        service.compute_all.assert_called_once_with()
        mock_repo.query.assert_called_once_with(RAW_DATA_QUERY)
        raw_df.to_dicts.assert_called_once_with()

        assert mock_to_thread.call_count == 2
        mock_to_thread.assert_any_call(service.compute_all)
        mock_to_thread.assert_any_call(mock_repo.query, RAW_DATA_QUERY)

    @patch("backend.api.analytics.AnalyticsService")
    @patch(
        "backend.api.analytics.asyncio.to_thread",
        side_effect=lambda fn, *args, **kwargs: fn(*args, **kwargs),
    )
    def test_compute_service_error_returns_json_500(
        self,
        mock_to_thread,
        mock_service_class,
        client,
        mock_repo,
    ):
        service = mock_service_class.return_value
        service.compute_all.side_effect = Exception("Analytics error")

        response = client.get("/api/analytics/compute")

        assert response.status_code == 500
        assert response.json() == {
            "detail": "Analytics computation failed"
        }

        mock_service_class.assert_called_once_with(mock_repo)
        mock_to_thread.assert_called_once_with(service.compute_all)
        mock_repo.query.assert_not_called()
