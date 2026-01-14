"""E2E tests for djb deploy k8s commands.

These tests use real Docker containers with SSH to test the K8s deployment
workflow. No mocking of SSH - all commands run against real containers.

Requirements:
- Docker must be running
- Tests are skipped if Docker is not available

All tests in this package are marked with e2e_marker.
"""
