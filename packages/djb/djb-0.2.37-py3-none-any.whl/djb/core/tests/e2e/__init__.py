"""E2E tests for djb.core module.

These tests use real subprocess execution and require actual command-line tools.
Mark with e2e_marker to allow skipping with --no-e2e.
"""

import pytest

pytestmark = pytest.mark.e2e_marker
