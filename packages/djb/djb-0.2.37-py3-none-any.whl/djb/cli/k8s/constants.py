"""Constants for djb deploy k8s commands.

Timeout Constants:
    MICROK8S_OPERATION_TIMEOUT, KUBECTL_WAIT_TIMEOUT,
    DOCKER_CHECK_TIMEOUT, TOOL_AVAILABILITY_TIMEOUT

Local Development:
    DEFAULT_DEV_PORT

Note: SSH-related constants have been moved to djb.ssh.client
"""

from typing import Final

# MicroK8s operation timeouts (seconds)
MICROK8S_OPERATION_TIMEOUT: Final[int] = 120
KUBECTL_WAIT_TIMEOUT: Final[int] = 150

# Docker check timeout (seconds)
DOCKER_CHECK_TIMEOUT: Final[int] = 10

# Tool availability check timeout (seconds)
TOOL_AVAILABILITY_TIMEOUT: Final[int] = 5

# Default port for local development (port forwarding)
DEFAULT_DEV_PORT: Final[int] = 8000

__all__ = [
    "MICROK8S_OPERATION_TIMEOUT",
    "KUBECTL_WAIT_TIMEOUT",
    "DOCKER_CHECK_TIMEOUT",
    "TOOL_AVAILABILITY_TIMEOUT",
    "DEFAULT_DEV_PORT",
]
