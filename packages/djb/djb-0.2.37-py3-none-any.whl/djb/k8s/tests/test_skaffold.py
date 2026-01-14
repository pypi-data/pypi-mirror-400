"""Tests for Skaffold configuration generation."""

from __future__ import annotations

from pathlib import Path

import yaml

from djb.k8s.skaffold import (
    SkaffoldConfig,
    SkaffoldGenerator,
    generate_skaffold_config,
)


class TestSkaffoldConfig:
    """Tests for SkaffoldConfig dataclass."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = SkaffoldConfig(
            project_name="myapp",
            project_package="myapp",
            registry_address="k3d-registry.localhost:5000",
            buildpack_image="k3d-registry.localhost:5000/python3.14-slim:latest",
        )
        assert config.project_name == "myapp"
        assert config.project_package == "myapp"
        assert config.registry_address == "k3d-registry.localhost:5000"
        assert config.buildpack_image == "k3d-registry.localhost:5000/python3.14-slim:latest"
        assert config.local_port == 8000
        assert config.container_port == 8000
        assert config.dockerfile == "Dockerfile"
        assert config.sync_patterns == []
        assert config.manifests_dir == "k8s"

    def test_custom_values(self) -> None:
        """Test configuration with custom values."""
        config = SkaffoldConfig(
            project_name="myapp",
            project_package="myproject",
            registry_address="localhost:32000",
            buildpack_image="localhost:32000/python3.14-slim-gdal:latest",
            local_port=8080,
            container_port=8000,
            dockerfile="docker/Dockerfile.dev",
            sync_patterns=[{"src": "custom/**/*", "dest": "/custom"}],
            manifests_dir="kubernetes",
        )
        assert config.project_package == "myproject"
        assert config.registry_address == "localhost:32000"
        assert config.buildpack_image == "localhost:32000/python3.14-slim-gdal:latest"
        assert config.local_port == 8080
        assert config.dockerfile == "docker/Dockerfile.dev"
        assert len(config.sync_patterns) == 1
        assert config.manifests_dir == "kubernetes"


class TestSkaffoldGenerator:
    """Tests for SkaffoldGenerator."""

    def test_generate_valid_yaml(self) -> None:
        """Test that generated content is valid YAML."""
        config = SkaffoldConfig(
            project_name="myapp",
            project_package="myapp",
            registry_address="k3d-registry.localhost:5000",
            buildpack_image="k3d-registry.localhost:5000/python3.14-slim:latest",
        )
        generator = SkaffoldGenerator()
        content = generator.generate(config)

        # Should be valid YAML
        parsed = yaml.safe_load(content)
        assert parsed is not None
        assert isinstance(parsed, dict)

    def test_generate_correct_api_version(self) -> None:
        """Test that generated config has correct API version."""
        config = SkaffoldConfig(
            project_name="myapp",
            project_package="myapp",
            registry_address="k3d-registry.localhost:5000",
            buildpack_image="k3d-registry.localhost:5000/python3.14-slim:latest",
        )
        generator = SkaffoldGenerator()
        content = generator.generate(config)
        parsed = yaml.safe_load(content)

        assert parsed["apiVersion"] == "skaffold/v4beta13"
        assert parsed["kind"] == "Config"

    def test_generate_project_name_in_metadata(self) -> None:
        """Test that project name is in metadata."""
        config = SkaffoldConfig(
            project_name="myapp",
            project_package="myapp",
            registry_address="k3d-registry.localhost:5000",
            buildpack_image="k3d-registry.localhost:5000/python3.14-slim:latest",
        )
        generator = SkaffoldGenerator()
        content = generator.generate(config)
        parsed = yaml.safe_load(content)

        assert parsed["metadata"]["name"] == "myapp"

    def test_generate_build_config(self) -> None:
        """Test build configuration."""
        config = SkaffoldConfig(
            project_name="myapp",
            project_package="myapp",
            registry_address="k3d-registry.localhost:5000",
            buildpack_image="k3d-registry.localhost:5000/python3.14-slim:latest",
            dockerfile="Dockerfile.custom",
        )
        generator = SkaffoldGenerator()
        content = generator.generate(config)
        parsed = yaml.safe_load(content)

        build = parsed["build"]
        assert build["local"]["push"] is False
        assert len(build["artifacts"]) == 1

        artifact = build["artifacts"][0]
        assert artifact["image"] == "k3d-registry.localhost:5000/myapp"
        assert artifact["docker"]["dockerfile"] == "Dockerfile.custom"
        assert (
            artifact["docker"]["buildArgs"]["BUILDPACK_IMAGE"]
            == "k3d-registry.localhost:5000/python3.14-slim:latest"
        )

    def test_generate_sync_patterns(self) -> None:
        """Test file sync patterns."""
        config = SkaffoldConfig(
            project_name="myapp",
            project_package="beachresort25",
            registry_address="k3d-registry.localhost:5000",
            buildpack_image="k3d-registry.localhost:5000/python3.14-slim:latest",
        )
        generator = SkaffoldGenerator()
        content = generator.generate(config)
        parsed = yaml.safe_load(content)

        sync = parsed["build"]["artifacts"][0]["sync"]["manual"]
        assert len(sync) >= 3  # At least Python, templates, frontend

        # Check for Python sync pattern
        python_patterns = [p for p in sync if "**/*.py" in p["src"]]
        assert len(python_patterns) >= 1
        assert python_patterns[0]["dest"] == "/app"

        # Check for templates sync pattern
        template_patterns = [p for p in sync if "templates" in p["src"]]
        assert len(template_patterns) >= 1

    def test_generate_custom_sync_patterns(self) -> None:
        """Test custom sync patterns are included."""
        config = SkaffoldConfig(
            project_name="myapp",
            project_package="myapp",
            registry_address="k3d-registry.localhost:5000",
            buildpack_image="k3d-registry.localhost:5000/python3.14-slim:latest",
            sync_patterns=[
                {"src": "custom/**/*", "dest": "/custom"},
            ],
        )
        generator = SkaffoldGenerator()
        content = generator.generate(config)
        parsed = yaml.safe_load(content)

        sync = parsed["build"]["artifacts"][0]["sync"]["manual"]
        custom_patterns = [p for p in sync if p["src"] == "custom/**/*"]
        assert len(custom_patterns) == 1
        assert custom_patterns[0]["dest"] == "/custom"

    def test_generate_deploy_config(self) -> None:
        """Test deploy configuration."""
        config = SkaffoldConfig(
            project_name="myapp",
            project_package="myapp",
            registry_address="k3d-registry.localhost:5000",
            buildpack_image="k3d-registry.localhost:5000/python3.14-slim:latest",
            manifests_dir="kubernetes",
        )
        generator = SkaffoldGenerator()
        content = generator.generate(config)
        parsed = yaml.safe_load(content)

        deploy = parsed["deploy"]
        assert "kubectl" in deploy
        assert "kubernetes/*.yaml" in deploy["kubectl"]["manifests"]

    def test_generate_port_forward(self) -> None:
        """Test port forwarding configuration."""
        config = SkaffoldConfig(
            project_name="myapp",
            project_package="myapp",
            registry_address="k3d-registry.localhost:5000",
            buildpack_image="k3d-registry.localhost:5000/python3.14-slim:latest",
            local_port=8080,
            container_port=8000,
        )
        generator = SkaffoldGenerator()
        content = generator.generate(config)
        parsed = yaml.safe_load(content)

        port_forward = parsed["portForward"]
        assert len(port_forward) == 1
        pf = port_forward[0]
        assert pf["resourceType"] == "service"
        assert pf["resourceName"] == "myapp"
        assert pf["port"] == 8000
        assert pf["localPort"] == 8080

    def test_generate_dev_profile(self) -> None:
        """Test dev profile configuration."""
        config = SkaffoldConfig(
            project_name="myapp",
            project_package="myapp",
            registry_address="k3d-registry.localhost:5000",
            buildpack_image="k3d-registry.localhost:5000/python3.14-slim:latest",
        )
        generator = SkaffoldGenerator()
        content = generator.generate(config)
        parsed = yaml.safe_load(content)

        profiles = parsed["profiles"]
        assert len(profiles) >= 1

        dev_profile = next(p for p in profiles if p["name"] == "dev")
        assert dev_profile["activation"][0]["command"] == "dev"

    def test_write_to_file(self, tmp_path: Path) -> None:
        """Test writing configuration to file."""
        config = SkaffoldConfig(
            project_name="myapp",
            project_package="myapp",
            registry_address="k3d-registry.localhost:5000",
            buildpack_image="k3d-registry.localhost:5000/python3.14-slim:latest",
        )
        generator = SkaffoldGenerator()

        output_path = tmp_path / "skaffold.yaml"
        generator.write(config, output_path)

        assert output_path.exists()
        content = output_path.read_text()
        parsed = yaml.safe_load(content)
        assert parsed["metadata"]["name"] == "myapp"


class TestGenerateSkaffoldConfig:
    """Tests for generate_skaffold_config convenience function."""

    def test_generate_with_required_args(self) -> None:
        """Test generation with required arguments only."""
        content = generate_skaffold_config(
            project_name="myapp",
            project_package="myapp",
            registry_address="k3d-registry.localhost:5000",
            buildpack_image="k3d-registry.localhost:5000/python3.14-slim:latest",
        )

        parsed = yaml.safe_load(content)
        assert parsed["metadata"]["name"] == "myapp"
        assert "k3d-registry.localhost:5000/myapp" in str(parsed)

    def test_generate_with_optional_args(self) -> None:
        """Test generation with optional arguments."""
        content = generate_skaffold_config(
            project_name="myapp",
            project_package="myproject",
            registry_address="localhost:32000",
            buildpack_image="localhost:32000/python3.14-slim:latest",
            local_port=8080,
        )

        parsed = yaml.safe_load(content)
        assert parsed["portForward"][0]["localPort"] == 8080
