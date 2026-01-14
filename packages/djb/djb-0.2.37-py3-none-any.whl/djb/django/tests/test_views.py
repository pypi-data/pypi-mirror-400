"""Unit tests for djb.django.views health check endpoints.

Tests the health check and readiness views including URL validation
and caching behavior.
"""

from __future__ import annotations

import json
import time
from unittest.mock import patch

import pytest
from django.test import RequestFactory

from djb.django.views import (
    CACHE_TTL,
    _ready_cache,
    _validate_homepage_urls,
    health_check,
    health_check_ready,
)


class MockResponse:
    """Mock requests.Response for testing."""

    def __init__(
        self,
        text: str,
        status_code: int = 200,
    ) -> None:
        self.text = text
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")


@pytest.fixture
def request_factory() -> RequestFactory:
    """Create a Django request factory."""
    return RequestFactory()


@pytest.fixture(autouse=True)
def clear_cache() -> None:
    """Clear the readiness cache before each test."""
    _ready_cache.clear()


class TestHealthCheck:
    """Tests for health_check (liveness probe)."""

    def test_returns_ok_status(self, request_factory: RequestFactory) -> None:
        """Test that health check returns OK status."""
        request = request_factory.get("/health/")
        response = health_check(request)

        assert response.status_code == 200
        assert json.loads(response.content) == {"status": "ok"}

    def test_includes_version_header_when_set(self, request_factory: RequestFactory) -> None:
        """Test that X-Version header is included when GIT_COMMIT_SHA is set."""
        request = request_factory.get("/health/")
        with patch.dict("os.environ", {"GIT_COMMIT_SHA": "abc1234"}):
            response = health_check(request)

        assert response.status_code == 200
        assert response["X-Version"] == "abc1234"

    def test_no_version_header_when_not_set(self, request_factory: RequestFactory) -> None:
        """Test that X-Version header is absent when GIT_COMMIT_SHA is not set."""
        request = request_factory.get("/health/")
        with patch.dict("os.environ", {}, clear=True):
            response = health_check(request)

        assert response.status_code == 200
        assert "X-Version" not in response


class TestHealthCheckReady:
    """Tests for health_check_ready (readiness probe)."""

    def test_returns_ok_when_all_urls_valid(self, request_factory: RequestFactory) -> None:
        """Test readiness returns OK when all homepage URLs are valid."""
        html = """
        <html>
        <head>
            <link rel="stylesheet" href="/static/css/main.css">
        </head>
        <body></body>
        </html>
        """

        request = request_factory.get("/health/ready/")
        with patch("djb.django.views.requests.get") as mock_get:
            mock_get.side_effect = [
                MockResponse(html),
                MockResponse("body { color: black; }"),
            ]
            response = health_check_ready(request)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["status"] == "ok"
        assert data["urls_checked"] > 0

    def test_returns_error_when_missing_asset(self, request_factory: RequestFactory) -> None:
        """Test readiness returns error when __missing__ marker found."""
        html = """
        <html>
        <head>
            <link rel="stylesheet" href="/static/__missing__/main.css">
        </head>
        <body></body>
        </html>
        """

        request = request_factory.get("/health/ready/")
        with patch("djb.django.views.requests.get") as mock_get:
            mock_get.return_value = MockResponse(html)
            response = health_check_ready(request)

        assert response.status_code == 500
        data = json.loads(response.content)
        assert data["status"] == "error"
        assert len(data["errors"]) == 1
        assert "__missing__" in data["errors"][0]

    def test_caches_result(self, request_factory: RequestFactory) -> None:
        """Test that readiness result is cached."""
        html = "<html><body></body></html>"

        request = request_factory.get("/health/ready/")
        with patch("djb.django.views.requests.get") as mock_get:
            mock_get.return_value = MockResponse(html)

            # First call should hit the endpoint
            response1 = health_check_ready(request)
            call_count1 = mock_get.call_count

            # Second call should use cache
            response2 = health_check_ready(request)
            call_count2 = mock_get.call_count

        assert response1.status_code == 200
        assert response2.status_code == 200
        # Should not have made additional calls
        assert call_count2 == call_count1

    def test_cache_expires(self, request_factory: RequestFactory) -> None:
        """Test that cache expires after TTL."""
        html = "<html><body></body></html>"

        request = request_factory.get("/health/ready/")
        with patch("djb.django.views.requests.get") as mock_get:
            mock_get.return_value = MockResponse(html)

            # First call
            health_check_ready(request)
            call_count1 = mock_get.call_count

            # Simulate cache expiry by manipulating cache directly
            if "result" in _ready_cache:
                # Set cache time to past
                _ready_cache["result"] = (time.time() - CACHE_TTL - 1, _ready_cache["result"][1])

            # Second call should re-fetch
            health_check_ready(request)
            call_count2 = mock_get.call_count

        assert call_count2 > call_count1


class TestValidateHomepageUrls:
    """Tests for _validate_homepage_urls helper function."""

    def test_detects_missing_marker_in_css(self) -> None:
        """Test that __missing__ marker in CSS URLs is detected."""
        html = """
        <html>
        <head>
            <link rel="stylesheet" href="/static/__missing__/main.css">
        </head>
        <body></body>
        </html>
        """
        with patch("djb.django.views.requests.get") as mock_get:
            mock_get.return_value = MockResponse(html)
            result = _validate_homepage_urls()

        assert result["status"] == "error"
        assert len(result["errors"]) == 1
        assert "__missing__" in result["errors"][0]
        assert "main.css" in result["errors"][0]

    def test_detects_missing_marker_in_js(self) -> None:
        """Test that __missing__ marker in JS URLs is detected."""
        html = """
        <html>
        <head>
            <script src="/static/__missing__/main.js"></script>
        </head>
        <body></body>
        </html>
        """
        with patch("djb.django.views.requests.get") as mock_get:
            mock_get.return_value = MockResponse(html)
            result = _validate_homepage_urls()

        assert result["status"] == "error"
        assert len(result["errors"]) == 1
        assert "__missing__" in result["errors"][0]
        assert "main.js" in result["errors"][0]

    def test_multiple_missing_assets_all_reported(self) -> None:
        """Test that multiple missing assets are all reported."""
        html = """
        <html>
        <head>
            <link rel="stylesheet" href="/static/__missing__/main.css">
            <script src="/static/__missing__/main.js"></script>
            <script src="/static/__missing__/vendor.js"></script>
        </head>
        <body></body>
        </html>
        """
        with patch("djb.django.views.requests.get") as mock_get:
            mock_get.return_value = MockResponse(html)
            result = _validate_homepage_urls()

        assert result["status"] == "error"
        assert len(result["errors"]) == 3
        assert any("main.css" in e for e in result["errors"])
        assert any("main.js" in e for e in result["errors"])
        assert any("vendor.js" in e for e in result["errors"])

    def test_skips_external_urls(self) -> None:
        """Test that external URLs are not validated."""
        html = """
        <html>
        <head>
            <link rel="stylesheet" href="https://example.com/external.css">
        </head>
        <body></body>
        </html>
        """
        with patch("djb.django.views.requests.get") as mock_get:
            mock_get.return_value = MockResponse(html)
            result = _validate_homepage_urls()

        # Should be OK - external URLs are skipped
        assert result["status"] == "ok"

    def test_skips_data_urls(self) -> None:
        """Test that data: URLs are not validated."""
        html = """
        <html>
        <body>
            <img src="data:image/png;base64,iVBORw0KGgo=">
        </body>
        </html>
        """
        with patch("djb.django.views.requests.get") as mock_get:
            mock_get.return_value = MockResponse(html)
            result = _validate_homepage_urls()

        assert result["status"] == "ok"

    def test_homepage_fetch_error(self) -> None:
        """Test handling of homepage fetch failure."""
        with patch("djb.django.views.requests.get") as mock_get:
            mock_get.side_effect = Exception("Connection refused")
            result = _validate_homepage_urls()

        assert result["status"] == "error"
        assert len(result["errors"]) == 1
        assert "Failed to fetch" in result["errors"][0]
