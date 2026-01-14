"""
DNS provider module for djb.

This module provides DNS provider implementations for managing domain records.
Currently supports Cloudflare DNS management.

Exports:
    CloudflareDnsProvider: Cloudflare DNS implementation
    CloudflareError: Cloudflare-specific errors
    DnsRecord: Dataclass with DNS record information
"""

from djb.dns.cloudflare import CloudflareDnsProvider, CloudflareError, DnsRecord

__all__ = [
    "CloudflareDnsProvider",
    "CloudflareError",
    "DnsRecord",
]
