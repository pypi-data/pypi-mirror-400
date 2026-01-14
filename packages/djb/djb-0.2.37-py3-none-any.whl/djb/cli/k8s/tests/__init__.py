"""Tests for djb deploy k8s commands.

This package contains unit tests and E2E tests for Kubernetes deployment commands.

Test organization:
- Unit tests: test_*.py files in this directory (help text, validation only)
- E2E tests: e2e/ subdirectory (real I/O via project_dir, make_djb_config)

Fixtures:
- cli_runner: Click test runner (both unit and E2E)
- make_djb_config: Config factory (E2E only, requires project_dir)
- require_docker: Skip marker if Docker unavailable (E2E only)
- make_local_vps_container: Docker container with SSH for E2E testing
"""
