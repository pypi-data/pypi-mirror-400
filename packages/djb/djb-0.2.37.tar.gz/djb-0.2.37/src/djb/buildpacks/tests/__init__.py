"""
Buildpacks module tests.

Test structure:
- test_specs.py - Pure function tests for parse(), BuildpackSpec, BuildpackChainSpec
- test_resolvers.py - Version resolution tests (resolvers.py utilities and metadata.py functions)
- test_base.py - BuildpackChain ABC tests (pure unit tests)
- test_remote.py - RemoteBuildpackChain with mocked SSH
- test_local.py - LocalBuildpackChain with mocked CmdRunner
- e2e/ - Tests that do file I/O (create temp Dockerfiles)

Fixtures (from conftest.py):
- mock_ssh - Mocked SSHClient
- mock_cmd_runner - Mocked CmdRunner (re-exported from djb.testing.fixtures)
- make_pyproject_with_gdal - pyproject.toml with gdal dependency

Fixtures (from e2e/conftest.py):
- make_buildpack_dockerfiles - Temporary dockerfiles directory with test Dockerfiles
"""
