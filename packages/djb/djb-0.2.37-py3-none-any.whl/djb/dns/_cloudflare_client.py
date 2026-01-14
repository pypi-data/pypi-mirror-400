"""
Minimal Cloudflare API client with SDK-compatible interface.

TEMPORARY - DELETE WHEN CLOUDFLARE SDK SUPPORTS PYTHON 3.14
============================================================
This module exists because the official cloudflare SDK uses pydantic.v1 which
breaks on Python 3.14. See cloudflare.py docstring for revert instructions.

The interface is identical to the official SDK for the subset we use:
- Cloudflare(api_token=...) client
- client.zones.list(name=...)
- client.dns.records.list/create/update/delete(...)
- APIError exception
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterator

import requests

BASE_URL = "https://api.cloudflare.com/client/v4"


class APIError(Exception):
    """Cloudflare API error (matches cloudflare._exceptions.APIError)."""

    pass


@dataclass
class ZoneResponse:
    """Zone response object (matches cloudflare.types.zones.Zone)."""

    id: str
    name: str


@dataclass
class RecordResponse:
    """DNS record response object (matches cloudflare.types.dns.RecordResponse)."""

    id: str | None
    name: str | None
    type: str | None
    content: str | None
    ttl: int | None
    proxied: bool | None


class _ZonesResource:
    """Zones API resource (matches cloudflare.resources.zones.Zones)."""

    def __init__(self, headers: dict[str, str]) -> None:
        self._headers = headers

    def list(self, *, name: str | None = None) -> Iterator[ZoneResponse]:
        """List zones, optionally filtered by name."""
        params: dict[str, Any] = {}
        if name:
            params["name"] = name

        try:
            response = requests.get(
                f"{BASE_URL}/zones",
                headers=self._headers,
                params=params or None,
                timeout=30,
            )
            data = response.json()

            if not data.get("success", False):
                errors = data.get("errors", [])
                error_msg = (
                    "; ".join(e.get("message", str(e)) for e in errors)
                    if errors
                    else "Unknown error"
                )
                raise APIError(f"API error: {error_msg}")

            for zone in data.get("result", []):
                yield ZoneResponse(id=zone["id"], name=zone["name"])
        except requests.RequestException as e:
            raise APIError(f"Request failed: {e}") from e


class _DnsRecordsResource:
    """DNS records API resource (matches cloudflare.resources.dns.records.Records)."""

    def __init__(self, headers: dict[str, str]) -> None:
        self._headers = headers

    def list(
        self,
        *,
        zone_id: str,
        name: str | None = None,
        type: str | None = None,
    ) -> Iterator[RecordResponse]:
        """List DNS records in a zone."""
        params: dict[str, Any] = {}
        if name:
            params["name"] = name
        if type:
            params["type"] = type

        try:
            response = requests.get(
                f"{BASE_URL}/zones/{zone_id}/dns_records",
                headers=self._headers,
                params=params or None,
                timeout=30,
            )
            data = response.json()

            if not data.get("success", False):
                errors = data.get("errors", [])
                error_msg = (
                    "; ".join(e.get("message", str(e)) for e in errors)
                    if errors
                    else "Unknown error"
                )
                raise APIError(f"API error: {error_msg}")

            for record in data.get("result", []):
                yield RecordResponse(
                    id=record.get("id"),
                    name=record.get("name"),
                    type=record.get("type"),
                    content=record.get("content"),
                    ttl=record.get("ttl"),
                    proxied=record.get("proxied"),
                )
        except requests.RequestException as e:
            raise APIError(f"Request failed: {e}") from e

    def create(
        self,
        *,
        zone_id: str,
        type: str,
        name: str,
        content: str,
        ttl: int,
        proxied: bool,
    ) -> RecordResponse:
        """Create a DNS record."""
        try:
            response = requests.post(
                f"{BASE_URL}/zones/{zone_id}/dns_records",
                headers=self._headers,
                json={
                    "type": type,
                    "name": name,
                    "content": content,
                    "ttl": ttl,
                    "proxied": proxied,
                },
                timeout=30,
            )
            data = response.json()

            if not data.get("success", False):
                errors = data.get("errors", [])
                error_msg = (
                    "; ".join(e.get("message", str(e)) for e in errors)
                    if errors
                    else "Unknown error"
                )
                raise APIError(f"API error: {error_msg}")

            result = data.get("result", {})
            return RecordResponse(
                id=result.get("id"),
                name=result.get("name"),
                type=result.get("type"),
                content=result.get("content"),
                ttl=result.get("ttl"),
                proxied=result.get("proxied"),
            )
        except requests.RequestException as e:
            raise APIError(f"Request failed: {e}") from e

    def update(
        self,
        *,
        zone_id: str,
        dns_record_id: str,
        type: str,
        name: str,
        content: str,
        ttl: int,
        proxied: bool,
    ) -> RecordResponse:
        """Update a DNS record."""
        try:
            response = requests.put(
                f"{BASE_URL}/zones/{zone_id}/dns_records/{dns_record_id}",
                headers=self._headers,
                json={
                    "type": type,
                    "name": name,
                    "content": content,
                    "ttl": ttl,
                    "proxied": proxied,
                },
                timeout=30,
            )
            data = response.json()

            if not data.get("success", False):
                errors = data.get("errors", [])
                error_msg = (
                    "; ".join(e.get("message", str(e)) for e in errors)
                    if errors
                    else "Unknown error"
                )
                raise APIError(f"API error: {error_msg}")

            result = data.get("result", {})
            return RecordResponse(
                id=result.get("id"),
                name=result.get("name"),
                type=result.get("type"),
                content=result.get("content"),
                ttl=result.get("ttl"),
                proxied=result.get("proxied"),
            )
        except requests.RequestException as e:
            raise APIError(f"Request failed: {e}") from e

    def delete(self, *, zone_id: str, dns_record_id: str) -> None:
        """Delete a DNS record."""
        try:
            response = requests.delete(
                f"{BASE_URL}/zones/{zone_id}/dns_records/{dns_record_id}",
                headers=self._headers,
                timeout=30,
            )
            data = response.json()

            if not data.get("success", False):
                errors = data.get("errors", [])
                error_msg = (
                    "; ".join(e.get("message", str(e)) for e in errors)
                    if errors
                    else "Unknown error"
                )
                raise APIError(f"API error: {error_msg}")
        except requests.RequestException as e:
            raise APIError(f"Request failed: {e}") from e


class _DnsResource:
    """DNS API resource (matches cloudflare.resources.dns.DNS)."""

    def __init__(self, headers: dict[str, str]) -> None:
        self.records = _DnsRecordsResource(headers)


class Cloudflare:
    """Cloudflare API client (matches cloudflare.Cloudflare).

    This is a minimal implementation that provides the same interface as the
    official cloudflare SDK, but only implements the subset of methods we use.
    """

    def __init__(self, *, api_token: str) -> None:
        """Initialize the Cloudflare client.

        Args:
            api_token: Cloudflare API token with Zone:DNS:Edit permission
        """
        self._headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }
        self.zones = _ZonesResource(self._headers)
        self.dns = _DnsResource(self._headers)
