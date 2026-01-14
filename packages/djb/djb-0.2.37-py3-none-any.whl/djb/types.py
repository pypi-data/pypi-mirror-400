"""
djb types - Core type definitions for djb configuration.

Provides enums for mode and platform that are used throughout the djb CLI
and can be synced to deployment environments.
"""

from __future__ import annotations

from enum import Enum
from typing import Union

__all__ = ["DomainNameManager", "K8sClusterType", "K8sProvider", "Mode", "NestedDict", "Platform"]

# Recursive type for nested dictionaries with primitive values
# Note: Union is required here because recursive type aliases with | and forward refs
# don't work at runtime (TypeError: unsupported operand type(s) for |: 'type' and 'str')
NestedDict = dict[str, Union[str, int, float, bool, None, "NestedDict"]]


class Mode(str, Enum):
    """Deployment mode for djb projects.

    Modes control behavior and which secrets are loaded:
    - development: Local development (default)
    - staging: Staging/test environment
    - production: Production deployment
    """

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def parse(cls, value: str | None, default: Mode | None = None) -> Mode | None:
        """Parse a string to Mode, returning default on failure.

        Args:
            value: String to parse (case-insensitive)
            default: Value to return if parsing fails

        Returns:
            Parsed Mode or default value
        """
        if value is None or not isinstance(value, str):
            return default
        try:
            return cls(value.lower())
        except ValueError:
            return default

    @classmethod
    def all(cls) -> list[Mode]:
        """Return all modes."""
        return list(cls)

    @classmethod
    def dev(cls) -> list[Mode]:
        """Development modes (local only, gitignored)."""
        return [cls.DEVELOPMENT]

    @classmethod
    def public(cls) -> list[Mode]:
        """Public modes (shared across team, committed)."""
        return [cls.STAGING, cls.PRODUCTION]


class Platform(str, Enum):
    """Deployment platform.

    Platforms control where and how the application is deployed:
    - heroku: Deploy to Heroku (default)
    - k8s: Deploy to Kubernetes
    """

    HEROKU = "heroku"
    K8S = "k8s"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def parse(cls, value: str | None, default: Platform | None = None) -> Platform | None:
        """Parse a string to Platform, returning default on failure.

        Args:
            value: String to parse (case-insensitive)
            default: Value to return if parsing fails

        Returns:
            Parsed Platform or default value
        """
        if value is None or not isinstance(value, str):
            return default
        try:
            return cls(value.lower())
        except ValueError:
            return default


class K8sProvider(str, Enum):
    """Cloud provider for K8s VPS provisioning.

    Controls how the VPS is provisioned:
    - manual: Requires explicit --host for remote deployments
    - hetzner: Auto-provisions a VPS via Hetzner Cloud API
    """

    MANUAL = "manual"
    HETZNER = "hetzner"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def parse(cls, value: str | None, default: K8sProvider | None = None) -> K8sProvider | None:
        """Parse a string to K8sProvider, returning default on failure.

        Args:
            value: String to parse (case-insensitive)
            default: Value to return if parsing fails

        Returns:
            Parsed K8sProvider or default value
        """
        if value is None or not isinstance(value, str):
            return default
        try:
            return cls(value.lower())
        except ValueError:
            return default


class K8sClusterType(str, Enum):
    """K8s cluster distribution type.

    Controls which K8s distribution is used:
    - k3d: Lightweight K3s in Docker (default for local development)
    - microk8s: Canonical's MicroK8s
    """

    K3D = "k3d"
    MICROK8S = "microk8s"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def parse(
        cls, value: str | None, default: K8sClusterType | None = None
    ) -> K8sClusterType | None:
        """Parse a string to K8sClusterType, returning default on failure.

        Args:
            value: String to parse (case-insensitive)
            default: Value to return if parsing fails

        Returns:
            Parsed K8sClusterType or default value
        """
        if value is None or not isinstance(value, str):
            return default
        try:
            return cls(value.lower())
        except ValueError:
            return default


class DomainNameManager(str, Enum):
    """DNS management provider for a domain.

    Controls how DNS records are managed for a domain:
    - cloudflare: Managed via Cloudflare API
    - platform: Managed by the deploy platform (e.g. used for *.herokuapp.com)
    - manual: No automatic DNS management
    """

    CLOUDFLARE = "cloudflare"
    PLATFORM = "platform"
    MANUAL = "manual"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def parse(
        cls, value: str | None, default: DomainNameManager | None = None
    ) -> DomainNameManager | None:
        """Parse a string to DomainManager, returning default on failure.

        Args:
            value: String to parse (case-insensitive)
            default: Value to return if parsing fails

        Returns:
            Parsed DomainManager or default value
        """
        if value is None or not isinstance(value, str):
            return default
        try:
            return cls(value.lower())
        except ValueError:
            return default
