"""Reusable Django views for health checking.

Usage in urls.py:
    from djb.django import health_check, health_check_ready

    urlpatterns = [
        path("health/", health_check, name="health"),
        path("health/ready/", health_check_ready, name="health_ready"),
    ]

K8s Probe Configuration:
    livenessProbe:
      httpGet:
        path: /health/
        port: 8000
    readinessProbe:
      httpGet:
        path: /health/ready/
        port: 8000
"""

from __future__ import annotations

import os
import time
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urljoin

import requests
from django.http import HttpRequest, JsonResponse

# Cache for readiness check results (avoid re-validating on every probe)
_ready_cache: dict[str, tuple[float, dict[str, Any]]] = {}
CACHE_TTL = 60  # seconds


def health_check(request: HttpRequest) -> JsonResponse:
    """Liveness probe - is Django alive?

    Fast check for K8s liveness probes. If this fails, pod restarts.

    Returns:
        JsonResponse with {"status": "ok"} and optional X-Version header.
    """
    response = JsonResponse({"status": "ok"})
    if version := os.environ.get("GIT_COMMIT_SHA"):
        response["X-Version"] = version
    return response


def health_check_ready(request: HttpRequest) -> JsonResponse:
    """Readiness probe - are all assets valid?

    Validates homepage URLs internally. If fails, pod removed from LB.
    Results cached for 60s to avoid repeated validation.

    Returns:
        200: {"status": "ok", "urls_checked": N}
        500: {"status": "error", "errors": [...], "urls_checked": N}
    """
    # Check cache
    now = time.time()
    if "result" in _ready_cache:
        cached_time, cached_result = _ready_cache["result"]
        if now - cached_time < CACHE_TTL:
            status_code = 200 if cached_result["status"] == "ok" else 500
            return JsonResponse(cached_result, status=status_code)

    # Perform validation
    result = _validate_homepage_urls()
    _ready_cache["result"] = (now, result)

    status_code = 200 if result["status"] == "ok" else 500
    return JsonResponse(result, status=status_code)


def _validate_homepage_urls() -> dict[str, Any]:
    """Validate all URLs on the homepage are accessible.

    Makes internal HTTP request to localhost:8000/ and validates
    all href/src URLs found in the HTML.
    """
    broken: list[str] = []
    base_url = "http://localhost:8000/"

    # Fetch homepage internally
    try:
        resp = requests.get(base_url, timeout=10)
        resp.raise_for_status()
        html = resp.text
    except Exception as e:
        return {"status": "error", "errors": [f"Failed to fetch /: {e}"], "urls_checked": 0}

    # Extract URLs from HTML
    class URLExtractor(HTMLParser):
        def __init__(self) -> None:
            super().__init__()
            self.urls: set[str] = set()

        def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
            for name, value in attrs:
                if name in ("href", "src") and value:
                    self.urls.add(value)

    extractor = URLExtractor()
    try:
        extractor.feed(html)
    except Exception as e:
        return {"status": "error", "errors": [f"Failed to parse HTML: {e}"], "urls_checked": 0}

    # Validate each URL
    for url in extractor.urls:
        # Skip non-HTTP URLs
        if url.startswith(("data:", "javascript:", "mailto:", "tel:", "#")):
            continue

        # Resolve relative URLs
        full_url = urljoin(base_url, url)

        # Only check same-origin URLs
        if not full_url.startswith(base_url):
            continue

        # Check for __missing__ marker (WhiteNoise fallback for missing assets)
        if "__missing__" in url:
            broken.append(f"{url} [missing static asset]")
            continue

        # Verify URL loads
        try:
            resp = requests.get(full_url, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            broken.append(f"{url} ({e})")

    urls_checked = len(extractor.urls)
    if broken:
        return {"status": "error", "errors": broken, "urls_checked": urls_checked}
    return {"status": "ok", "urls_checked": urls_checked}
