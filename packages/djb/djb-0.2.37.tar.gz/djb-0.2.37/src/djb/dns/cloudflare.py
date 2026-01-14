"""
Cloudflare DNS provider implementation.

Uses direct HTTP requests to the Cloudflare API v4.

TEMPORARY WORKAROUND (December 2024)
====================================
The official cloudflare SDK (v3.x/v4.x) uses pydantic.v1 internally, which is
incompatible with Python 3.14. This causes a warning on import:

    UserWarning: Core Pydantic V1 functionality isn't compatible with Python 3.14

We use a minimal SDK-compatible client (_cloudflare_client.py) as a drop-in replacement.

TO REVERT WHEN CLOUDFLARE SDK IS FIXED:
1. Add "cloudflare>=3.0.0" to djb/pyproject.toml dependencies
2. Change imports below:
   - from cloudflare import Cloudflare
   - from cloudflare._exceptions import APIError
3. Change TYPE_CHECKING import:
   - from cloudflare.types.dns import RecordResponse
4. Delete djb/src/djb/dns/_cloudflare_client.py
5. Run: uv sync

Track issue: https://github.com/cloudflare/cloudflare-python/issues
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal, cast

from djb.core.exceptions import DjbError
from djb.core.logging import get_logger
from djb.dns._cloudflare_client import APIError, Cloudflare

if TYPE_CHECKING:
    from djb.dns._cloudflare_client import RecordResponse

logger = get_logger(__name__)

# Type alias for record types
RecordType = Literal[
    "A",
    "AAAA",
    "CAA",
    "CERT",
    "CNAME",
    "DNSKEY",
    "DS",
    "HTTPS",
    "LOC",
    "MX",
    "NAPTR",
    "NS",
    "OPENPGPKEY",
    "PTR",
    "SMIMEA",
    "SRV",
    "SSHFP",
    "SVCB",
    "TLSA",
    "TXT",
    "URI",
]


class CloudflareError(DjbError):
    """Cloudflare API error."""

    pass


@dataclass
class DnsRecord:
    """Information about a DNS record."""

    id: str
    name: str
    type: str
    content: str
    ttl: int
    proxied: bool


def _record_to_dns_record(record: RecordResponse, default_ttl: int = 1) -> DnsRecord:
    """Convert a Cloudflare record response to a DnsRecord.

    Args:
        record: Cloudflare record response
        default_ttl: Default TTL to use if record TTL is None

    Returns:
        DnsRecord with the record details

    Raises:
        CloudflareError: If required fields are missing
    """
    if record.id is None or record.name is None or record.type is None:
        raise CloudflareError("Record missing required fields (id, name, or type)")

    content = record.content if record.content else ""
    ttl_value = int(record.ttl) if record.ttl else default_ttl
    proxied_value = bool(record.proxied) if record.proxied is not None else False

    return DnsRecord(
        id=record.id,
        name=record.name,
        type=record.type,
        content=content,
        ttl=ttl_value,
        proxied=proxied_value,
    )


class CloudflareDnsProvider:
    """Cloudflare DNS provider implementation.

    Provides methods to manage DNS records for domains.

    Example:
        provider = CloudflareDnsProvider(api_token="cftoken_xxx...")
        zone_id = provider.get_zone_id("staging.example.com")
        records = provider.configure_domain(
            zone_id=zone_id,
            domain="staging.example.com",
            ip="116.203.x.x",
            ttl=60,
            proxied=False,
        )
        for record in records:
            print(f"Configured: {record.name} -> {record.content}")
    """

    def __init__(self, api_token: str) -> None:
        """Initialize Cloudflare DNS provider.

        Args:
            api_token: Cloudflare API token with Zone:DNS:Edit permission
        """
        self._client = Cloudflare(api_token=api_token)

    def _extract_root_domain(self, domain: str) -> str:
        """Extract root domain from a domain name.

        Uses Cloudflare's zone list to find the matching zone.

        Args:
            domain: Full domain name (e.g., "staging.example.com")

        Returns:
            Root domain (e.g., "example.com")

        Raises:
            CloudflareError: If no matching zone is found
        """
        # Split domain into parts and try progressively shorter suffixes
        parts = domain.split(".")
        for i in range(len(parts)):
            candidate = ".".join(parts[i:])
            try:
                # Use cast to satisfy type checker - the SDK accepts string
                zones = list(self._client.zones.list(name=cast(Any, candidate)))
                if zones:
                    return candidate
            except APIError:
                continue

        raise CloudflareError(
            f"No Cloudflare zone found for domain '{domain}'. "
            f"Ensure the domain is added to your Cloudflare account."
        )

    def get_zone_id(self, domain: str) -> str:
        """Get the zone ID for a domain.

        Auto-detects the root domain from subdomains.

        Args:
            domain: Domain name (e.g., "staging.example.com")

        Returns:
            Cloudflare zone ID

        Raises:
            CloudflareError: If zone not found
        """
        root_domain = self._extract_root_domain(domain)
        zones = list(self._client.zones.list(name=cast(Any, root_domain)))
        if not zones:
            raise CloudflareError(f"Zone not found for domain '{root_domain}'")
        return zones[0].id

    def get_record(
        self,
        zone_id: str,
        name: str,
        record_type: RecordType,
    ) -> DnsRecord | None:
        """Get a DNS record by name and type.

        Args:
            zone_id: Cloudflare zone ID
            name: Record name (e.g., "example.com", "www.example.com")
            record_type: Record type (e.g., "A", "CNAME")

        Returns:
            DnsRecord if found, None otherwise
        """
        try:
            records = list(
                self._client.dns.records.list(
                    zone_id=zone_id,
                    name=cast(Any, name),
                    type=record_type,
                )
            )
            if not records:
                return None

            return _record_to_dns_record(records[0])
        except APIError as e:
            raise CloudflareError(f"Failed to get DNS record: {e}") from e

    def set_dns_record(
        self,
        zone_id: str,
        name: str,
        record_type: Literal["A", "CNAME"],
        content: str,
        ttl: int = 60,
        proxied: bool = False,
    ) -> DnsRecord:
        """Set a DNS record (create or update).

        This method is idempotent:
        - Creates the record if it doesn't exist
        - Updates the record if the content differs
        - Skips the update if the record already has the correct content
        - Deletes conflicting record types (A vs CNAME can't coexist at same name)

        Args:
            zone_id: Cloudflare zone ID
            name: Record name (e.g., "example.com", "www.example.com")
            record_type: Record type ("A" or "CNAME")
            content: Record content (IP address for A, target for CNAME)
            ttl: Time to live in seconds (default: 60)
            proxied: Whether to proxy through Cloudflare (default: False)

        Returns:
            DnsRecord with the record details
        """
        existing = self.get_record(zone_id, name, record_type)

        if existing:
            # Check if update is needed
            if existing.content == content and existing.ttl == ttl and existing.proxied == proxied:
                logger.debug(f"{record_type} record {name} already points to {content}, skipping")
                return existing

            # Update existing record
            logger.info(f"Updating {record_type} record: {name} -> {content}")
            try:
                record = self._client.dns.records.update(
                    zone_id=zone_id,
                    dns_record_id=existing.id,
                    type=record_type,
                    name=name,
                    content=content,
                    ttl=ttl,
                    proxied=proxied,
                )
                if record is None:
                    raise CloudflareError(f"{record_type} record update returned no response")
                return _record_to_dns_record(record, default_ttl=ttl)
            except APIError as e:
                raise CloudflareError(f"Failed to update {record_type} record: {e}") from e
        else:
            # Delete conflicting record type (A and CNAME can't coexist at same name)
            conflicting_type: Literal["A", "CNAME"] = "CNAME" if record_type == "A" else "A"
            conflicting = self.get_record(zone_id, name, conflicting_type)
            if conflicting:
                logger.info(
                    f"Deleting {conflicting_type} record {name} -> {conflicting.content} "
                    f"(replacing with {record_type})"
                )
                self.delete_record(zone_id, conflicting.id)

            # Create new record
            logger.info(f"Creating {record_type} record: {name} -> {content}")
            try:
                record = self._client.dns.records.create(
                    zone_id=zone_id,
                    type=record_type,
                    name=name,
                    content=content,
                    ttl=ttl,
                    proxied=proxied,
                )
                if record is None:
                    raise CloudflareError(f"{record_type} record create returned no response")
                return _record_to_dns_record(record, default_ttl=ttl)
            except APIError as e:
                raise CloudflareError(f"Failed to create {record_type} record: {e}") from e

    def set_a_record(
        self,
        zone_id: str,
        name: str,
        ip: str,
        ttl: int = 60,
        proxied: bool = False,
    ) -> DnsRecord:
        """Set an A record (create or update).

        Convenience wrapper around set_dns_record() for A records.

        Args:
            zone_id: Cloudflare zone ID
            name: Record name (e.g., "example.com", "www.example.com")
            ip: IPv4 address
            ttl: Time to live in seconds (default: 60)
            proxied: Whether to proxy through Cloudflare (default: False)

        Returns:
            DnsRecord with the record details
        """
        return self.set_dns_record(zone_id, name, "A", ip, ttl, proxied)

    def set_cname_record(
        self,
        zone_id: str,
        name: str,
        target: str,
        ttl: int = 60,
        proxied: bool = False,
    ) -> DnsRecord:
        """Set a CNAME record (create or update).

        Convenience wrapper around set_dns_record() for CNAME records.

        Args:
            zone_id: Cloudflare zone ID
            name: Record name (e.g., "www.example.com")
            target: CNAME target (e.g., "example.com.herokudns.com")
            ttl: Time to live in seconds (default: 60)
            proxied: Whether to proxy through Cloudflare (default: False)

        Returns:
            DnsRecord with the record details
        """
        return self.set_dns_record(zone_id, name, "CNAME", target, ttl, proxied)

    def configure_domain(
        self,
        zone_id: str,
        domain: str,
        ip: str,
        ttl: int = 60,
        proxied: bool = False,
    ) -> list[DnsRecord]:
        """Configure DNS for a domain (both bare and www).

        Sets A records for both the bare domain and www subdomain.

        Args:
            zone_id: Cloudflare zone ID
            domain: Domain name (e.g., "example.com")
            ip: IPv4 address
            ttl: Time to live in seconds (default: 60)
            proxied: Whether to proxy through Cloudflare (default: False)

        Returns:
            List of configured DnsRecord objects
        """
        records = []

        # Set A record for bare domain
        bare_record = self.set_a_record(zone_id, domain, ip, ttl, proxied)
        records.append(bare_record)

        # Set A record for www subdomain
        www_domain = f"www.{domain}"
        www_record = self.set_a_record(zone_id, www_domain, ip, ttl, proxied)
        records.append(www_record)

        return records

    def delete_record(self, zone_id: str, record_id: str) -> None:
        """Delete a DNS record.

        Args:
            zone_id: Cloudflare zone ID
            record_id: Record ID to delete

        Raises:
            CloudflareError: If deletion fails
        """
        try:
            self._client.dns.records.delete(zone_id=zone_id, dns_record_id=record_id)
        except APIError as e:
            raise CloudflareError(f"Failed to delete DNS record: {e}") from e

    def list_records(
        self,
        zone_id: str,
        record_type: RecordType | None = None,
    ) -> list[DnsRecord]:
        """List all DNS records in a zone.

        Args:
            zone_id: Cloudflare zone ID
            record_type: Optional filter by record type (e.g., "A", "CNAME")

        Returns:
            List of DnsRecord objects
        """
        try:
            if record_type:
                records = list(self._client.dns.records.list(zone_id=zone_id, type=record_type))
            else:
                records = list(self._client.dns.records.list(zone_id=zone_id))

            return [_record_to_dns_record(r) for r in records]
        except APIError as e:
            raise CloudflareError(f"Failed to list DNS records: {e}") from e
