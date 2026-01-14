"""
SSH utilities for djb.

This module provides a simple SSH client using subprocess calls to the system ssh command.
This avoids the need for paramiko and uses the same SSH configuration as the user's command line.

Exports:
    SSHClient: SSH client using system ssh command
    SSHError: SSH operation failed
"""

from djb.ssh.client import SSHClient, SSHError

__all__ = [
    "SSHClient",
    "SSHError",
]
