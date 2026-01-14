"""Unit tests for CloudflareDnsProvider and the minimal Cloudflare client.

These tests mock HTTP requests to verify the provider logic and ensure
our minimal client implementation is compatible with the official SDK API.
"""

from __future__ import annotations

from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
import requests as real_requests

from djb.dns import CloudflareDnsProvider, CloudflareError, DnsRecord
from djb.dns._cloudflare_client import (
    APIError,
    Cloudflare,
    RecordResponse,
    ZoneResponse,
)


class TestCloudflareClient:
    """Tests for the minimal Cloudflare client.

    These tests verify that our client provides the same interface
    as the official cloudflare SDK.
    """

    @pytest.fixture
    def mock_requests(self) -> Generator[MagicMock, None, None]:
        """Mock requests HTTP methods while preserving exception classes."""
        with (
            patch("djb.dns._cloudflare_client.requests.get") as mock_get,
            patch("djb.dns._cloudflare_client.requests.post") as mock_post,
            patch("djb.dns._cloudflare_client.requests.put") as mock_put,
            patch("djb.dns._cloudflare_client.requests.delete") as mock_delete,
        ):
            mock = MagicMock()
            mock.get = mock_get
            mock.post = mock_post
            mock.put = mock_put
            mock.delete = mock_delete
            mock.RequestException = real_requests.RequestException
            yield mock

    def test_zones_list_success(self, mock_requests: MagicMock) -> None:
        """Test listing zones returns ZoneResponse objects."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "result": [
                {"id": "zone-123", "name": "example.com"},
                {"id": "zone-456", "name": "example.org"},
            ],
        }
        mock_requests.get.return_value = mock_response

        client = Cloudflare(api_token="test-token")
        zones = list(client.zones.list(name="example.com"))

        assert len(zones) == 2
        assert isinstance(zones[0], ZoneResponse)
        assert zones[0].id == "zone-123"
        assert zones[0].name == "example.com"
        assert zones[1].id == "zone-456"

    def test_zones_list_api_error(self, mock_requests: MagicMock) -> None:
        """Test zones.list raises APIError on failure."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": False,
            "errors": [{"message": "Invalid API token"}],
        }
        mock_requests.get.return_value = mock_response

        client = Cloudflare(api_token="bad-token")

        with pytest.raises(APIError) as exc_info:
            list(client.zones.list())

        assert "Invalid API token" in str(exc_info.value)

    def test_dns_records_list_success(self, mock_requests: MagicMock) -> None:
        """Test listing DNS records returns RecordResponse objects."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "result": [
                {
                    "id": "rec-123",
                    "name": "example.com",
                    "type": "A",
                    "content": "1.2.3.4",
                    "ttl": 300,
                    "proxied": False,
                },
            ],
        }
        mock_requests.get.return_value = mock_response

        client = Cloudflare(api_token="test-token")
        records = list(client.dns.records.list(zone_id="zone-123", name="example.com", type="A"))

        assert len(records) == 1
        assert isinstance(records[0], RecordResponse)
        assert records[0].id == "rec-123"
        assert records[0].name == "example.com"
        assert records[0].type == "A"
        assert records[0].content == "1.2.3.4"
        assert records[0].ttl == 300
        assert records[0].proxied is False

    def test_dns_records_create_success(self, mock_requests: MagicMock) -> None:
        """Test creating DNS record returns RecordResponse."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "result": {
                "id": "rec-new",
                "name": "www.example.com",
                "type": "A",
                "content": "1.2.3.4",
                "ttl": 60,
                "proxied": True,
            },
        }
        mock_requests.post.return_value = mock_response

        client = Cloudflare(api_token="test-token")
        record = client.dns.records.create(
            zone_id="zone-123",
            type="A",
            name="www.example.com",
            content="1.2.3.4",
            ttl=60,
            proxied=True,
        )

        assert isinstance(record, RecordResponse)
        assert record.id == "rec-new"
        assert record.name == "www.example.com"

    def test_dns_records_update_success(self, mock_requests: MagicMock) -> None:
        """Test updating DNS record returns RecordResponse."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "result": {
                "id": "rec-123",
                "name": "www.example.com",
                "type": "A",
                "content": "5.6.7.8",
                "ttl": 120,
                "proxied": False,
            },
        }
        mock_requests.put.return_value = mock_response

        client = Cloudflare(api_token="test-token")
        record = client.dns.records.update(
            zone_id="zone-123",
            dns_record_id="rec-123",
            type="A",
            name="www.example.com",
            content="5.6.7.8",
            ttl=120,
            proxied=False,
        )

        assert isinstance(record, RecordResponse)
        assert record.content == "5.6.7.8"

    def test_dns_records_delete_success(self, mock_requests: MagicMock) -> None:
        """Test deleting DNS record succeeds."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "result": {"id": "rec-123"},
        }
        mock_requests.delete.return_value = mock_response

        client = Cloudflare(api_token="test-token")
        # Should not raise
        client.dns.records.delete(zone_id="zone-123", dns_record_id="rec-123")

    def test_authorization_header(self, mock_requests: MagicMock) -> None:
        """Test that API token is sent in Authorization header."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True, "result": []}
        mock_requests.get.return_value = mock_response

        client = Cloudflare(api_token="my-secret-token")
        list(client.zones.list())

        # Check that the auth header was passed
        call_kwargs = mock_requests.get.call_args[1]
        assert call_kwargs["headers"]["Authorization"] == "Bearer my-secret-token"


class TestCloudflareDnsProvider:
    """Tests for CloudflareDnsProvider."""

    @pytest.fixture
    def mock_client(self) -> Generator[MagicMock, None, None]:
        """Create a mock Cloudflare client."""
        with patch("djb.dns.cloudflare.Cloudflare") as mock_class:
            mock_client = MagicMock()
            mock_class.return_value = mock_client
            yield mock_client

    def test_get_zone_id_success(self, mock_client: MagicMock) -> None:
        """Test getting zone ID for a domain."""
        mock_zone = MagicMock()
        mock_zone.id = "zone-123"
        # zones.list is called twice: once by _extract_root_domain, once by get_zone_id
        mock_client.zones.list.side_effect = [iter([mock_zone]), iter([mock_zone])]

        provider = CloudflareDnsProvider(api_token="test-token")
        zone_id = provider.get_zone_id("example.com")

        assert zone_id == "zone-123"

    def test_get_zone_id_not_found(self, mock_client: MagicMock) -> None:
        """Test getting zone ID when domain not found."""
        mock_client.zones.list.return_value = iter([])

        provider = CloudflareDnsProvider(api_token="test-token")

        with pytest.raises(CloudflareError) as exc_info:
            provider.get_zone_id("unknown.com")

        assert "No Cloudflare zone found" in str(exc_info.value)

    def test_get_record_found(self, mock_client: MagicMock) -> None:
        """Test getting an existing DNS record."""
        mock_record = MagicMock()
        mock_record.id = "rec-123"
        mock_record.name = "www.example.com"
        mock_record.type = "A"
        mock_record.content = "1.2.3.4"
        mock_record.ttl = 300
        mock_record.proxied = False
        mock_client.dns.records.list.return_value = iter([mock_record])

        provider = CloudflareDnsProvider(api_token="test-token")
        record = provider.get_record("zone-123", "www.example.com", "A")

        assert record is not None
        assert record.id == "rec-123"
        assert record.content == "1.2.3.4"

    def test_get_record_not_found(self, mock_client: MagicMock) -> None:
        """Test getting a non-existent DNS record."""
        mock_client.dns.records.list.return_value = iter([])

        provider = CloudflareDnsProvider(api_token="test-token")
        record = provider.get_record("zone-123", "missing.example.com", "A")

        assert record is None

    def test_set_a_record_creates_new(self, mock_client: MagicMock) -> None:
        """Test creating a new A record."""
        mock_client.dns.records.list.return_value = iter([])  # No existing record

        mock_new_record = MagicMock()
        mock_new_record.id = "rec-new"
        mock_new_record.name = "www.example.com"
        mock_new_record.type = "A"
        mock_new_record.content = "1.2.3.4"
        mock_new_record.ttl = 60
        mock_new_record.proxied = False
        mock_client.dns.records.create.return_value = mock_new_record

        provider = CloudflareDnsProvider(api_token="test-token")
        record = provider.set_a_record("zone-123", "www.example.com", "1.2.3.4")

        assert record.id == "rec-new"
        mock_client.dns.records.create.assert_called_once()

    def test_set_a_record_updates_existing(self, mock_client: MagicMock) -> None:
        """Test updating an existing A record with different IP."""
        mock_existing = MagicMock()
        mock_existing.id = "rec-123"
        mock_existing.name = "www.example.com"
        mock_existing.type = "A"
        mock_existing.content = "1.1.1.1"  # Different IP
        mock_existing.ttl = 60
        mock_existing.proxied = False
        mock_client.dns.records.list.return_value = iter([mock_existing])

        mock_updated = MagicMock()
        mock_updated.id = "rec-123"
        mock_updated.name = "www.example.com"
        mock_updated.type = "A"
        mock_updated.content = "1.2.3.4"
        mock_updated.ttl = 60
        mock_updated.proxied = False
        mock_client.dns.records.update.return_value = mock_updated

        provider = CloudflareDnsProvider(api_token="test-token")
        record = provider.set_a_record("zone-123", "www.example.com", "1.2.3.4")

        assert record.content == "1.2.3.4"
        mock_client.dns.records.update.assert_called_once()

    def test_set_a_record_skips_unchanged(self, mock_client: MagicMock) -> None:
        """Test that unchanged A record is not updated."""
        mock_existing = MagicMock()
        mock_existing.id = "rec-123"
        mock_existing.name = "www.example.com"
        mock_existing.type = "A"
        mock_existing.content = "1.2.3.4"  # Same IP
        mock_existing.ttl = 60
        mock_existing.proxied = False
        mock_client.dns.records.list.return_value = iter([mock_existing])

        provider = CloudflareDnsProvider(api_token="test-token")
        record = provider.set_a_record(
            "zone-123", "www.example.com", "1.2.3.4", ttl=60, proxied=False
        )

        assert record.id == "rec-123"
        mock_client.dns.records.create.assert_not_called()
        mock_client.dns.records.update.assert_not_called()

    def test_set_cname_record_creates_new(self, mock_client: MagicMock) -> None:
        """Test creating a new CNAME record."""
        mock_client.dns.records.list.return_value = iter([])

        mock_new_record = MagicMock()
        mock_new_record.id = "rec-new"
        mock_new_record.name = "www.example.com"
        mock_new_record.type = "CNAME"
        mock_new_record.content = "example.herokudns.com"
        mock_new_record.ttl = 60
        mock_new_record.proxied = False
        mock_client.dns.records.create.return_value = mock_new_record

        provider = CloudflareDnsProvider(api_token="test-token")
        record = provider.set_cname_record("zone-123", "www.example.com", "example.herokudns.com")

        assert record.type == "CNAME"
        assert record.content == "example.herokudns.com"

    def test_set_a_record_deletes_conflicting_cname(self, mock_client: MagicMock) -> None:
        """Test that setting an A record deletes any existing CNAME at same name."""
        mock_existing_cname = MagicMock()
        mock_existing_cname.id = "rec-cname"
        mock_existing_cname.name = "www.example.com"
        mock_existing_cname.type = "CNAME"
        mock_existing_cname.content = "example.herokudns.com"
        mock_existing_cname.ttl = 60
        mock_existing_cname.proxied = False

        # First call: check for A record (none), second call: check for CNAME (exists)
        mock_client.dns.records.list.side_effect = [
            iter([]),  # No A record
            iter([mock_existing_cname]),  # Conflicting CNAME exists
        ]

        mock_new_record = MagicMock()
        mock_new_record.id = "rec-new"
        mock_new_record.name = "www.example.com"
        mock_new_record.type = "A"
        mock_new_record.content = "1.2.3.4"
        mock_new_record.ttl = 60
        mock_new_record.proxied = False
        mock_client.dns.records.create.return_value = mock_new_record

        provider = CloudflareDnsProvider(api_token="test-token")
        record = provider.set_a_record("zone-123", "www.example.com", "1.2.3.4")

        # Verify CNAME was deleted before A record was created
        mock_client.dns.records.delete.assert_called_once_with(
            zone_id="zone-123", dns_record_id="rec-cname"
        )
        mock_client.dns.records.create.assert_called_once()
        assert record.type == "A"
        assert record.content == "1.2.3.4"

    def test_set_cname_record_deletes_conflicting_a(self, mock_client: MagicMock) -> None:
        """Test that setting a CNAME record deletes any existing A record at same name."""
        mock_existing_a = MagicMock()
        mock_existing_a.id = "rec-a"
        mock_existing_a.name = "www.example.com"
        mock_existing_a.type = "A"
        mock_existing_a.content = "1.2.3.4"
        mock_existing_a.ttl = 60
        mock_existing_a.proxied = False

        # First call: check for CNAME (none), second call: check for A (exists)
        mock_client.dns.records.list.side_effect = [
            iter([]),  # No CNAME
            iter([mock_existing_a]),  # Conflicting A record exists
        ]

        mock_new_record = MagicMock()
        mock_new_record.id = "rec-new"
        mock_new_record.name = "www.example.com"
        mock_new_record.type = "CNAME"
        mock_new_record.content = "example.herokudns.com"
        mock_new_record.ttl = 60
        mock_new_record.proxied = False
        mock_client.dns.records.create.return_value = mock_new_record

        provider = CloudflareDnsProvider(api_token="test-token")
        record = provider.set_cname_record("zone-123", "www.example.com", "example.herokudns.com")

        # Verify A record was deleted before CNAME was created
        mock_client.dns.records.delete.assert_called_once_with(
            zone_id="zone-123", dns_record_id="rec-a"
        )
        mock_client.dns.records.create.assert_called_once()
        assert record.type == "CNAME"
        assert record.content == "example.herokudns.com"

    def test_configure_domain_creates_both_records(self, mock_client: MagicMock) -> None:
        """Test configure_domain creates both bare and www A records."""
        mock_client.dns.records.list.return_value = iter([])

        mock_record = MagicMock()
        mock_record.id = "rec-new"
        mock_record.name = "example.com"
        mock_record.type = "A"
        mock_record.content = "1.2.3.4"
        mock_record.ttl = 60
        mock_record.proxied = False
        mock_client.dns.records.create.return_value = mock_record

        provider = CloudflareDnsProvider(api_token="test-token")
        records = provider.configure_domain("zone-123", "example.com", "1.2.3.4")

        assert len(records) == 2
        # Should create both bare domain and www subdomain
        assert mock_client.dns.records.create.call_count == 2

    def test_delete_record_success(self, mock_client: MagicMock) -> None:
        """Test deleting a DNS record."""
        provider = CloudflareDnsProvider(api_token="test-token")
        provider.delete_record("zone-123", "rec-123")

        mock_client.dns.records.delete.assert_called_once_with(
            zone_id="zone-123", dns_record_id="rec-123"
        )

    def test_list_records_success(self, mock_client: MagicMock) -> None:
        """Test listing all DNS records."""
        mock_record1 = MagicMock()
        mock_record1.id = "rec-1"
        mock_record1.name = "example.com"
        mock_record1.type = "A"
        mock_record1.content = "1.2.3.4"
        mock_record1.ttl = 300
        mock_record1.proxied = False

        mock_record2 = MagicMock()
        mock_record2.id = "rec-2"
        mock_record2.name = "www.example.com"
        mock_record2.type = "CNAME"
        mock_record2.content = "example.com"
        mock_record2.ttl = 300
        mock_record2.proxied = True

        mock_client.dns.records.list.return_value = iter([mock_record1, mock_record2])

        provider = CloudflareDnsProvider(api_token="test-token")
        records = provider.list_records("zone-123")

        assert len(records) == 2
        assert records[0].type == "A"
        assert records[1].type == "CNAME"

    def test_list_records_filtered_by_type(self, mock_client: MagicMock) -> None:
        """Test listing DNS records filtered by type."""
        mock_record = MagicMock()
        mock_record.id = "rec-1"
        mock_record.name = "example.com"
        mock_record.type = "A"
        mock_record.content = "1.2.3.4"
        mock_record.ttl = 300
        mock_record.proxied = False
        mock_client.dns.records.list.return_value = iter([mock_record])

        provider = CloudflareDnsProvider(api_token="test-token")
        records = provider.list_records("zone-123", record_type="A")

        assert len(records) == 1
        mock_client.dns.records.list.assert_called_with(zone_id="zone-123", type="A")


class TestDnsRecord:
    """Tests for DnsRecord dataclass."""

    def test_dns_record_creation(self) -> None:
        """Test DnsRecord can be created with all fields."""
        record = DnsRecord(
            id="rec-123",
            name="example.com",
            type="A",
            content="1.2.3.4",
            ttl=300,
            proxied=True,
        )

        assert record.id == "rec-123"
        assert record.name == "example.com"
        assert record.type == "A"
        assert record.content == "1.2.3.4"
        assert record.ttl == 300
        assert record.proxied is True

    def test_dns_record_equality(self) -> None:
        """Test DnsRecord equality comparison."""
        record1 = DnsRecord(
            id="rec-1", name="example.com", type="A", content="1.2.3.4", ttl=60, proxied=False
        )
        record2 = DnsRecord(
            id="rec-1", name="example.com", type="A", content="1.2.3.4", ttl=60, proxied=False
        )
        record3 = DnsRecord(
            id="rec-2", name="example.com", type="A", content="1.2.3.4", ttl=60, proxied=False
        )

        assert record1 == record2
        assert record1 != record3
