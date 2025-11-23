"""Integration tests for Docker container build and dependencies."""

import subprocess
import pytest
import time


class TestDockerBuild:
    """Test Docker image builds correctly."""

    def test_dockerfile_exists(self):
        """Test Dockerfile exists."""
        import os
        dockerfile_path = "docker/Dockerfile"
        assert os.path.exists(dockerfile_path), f"Dockerfile not found at {dockerfile_path}"

    def test_docker_compose_exists(self):
        """Test docker-compose.yml exists."""
        import os
        compose_path = "docker-compose.yml"
        assert os.path.exists(compose_path), f"docker-compose.yml not found at {compose_path}"

    @pytest.mark.skipif(
        not pytest.config.getoption("--test-docker", default=False),
        reason="Docker tests require --test-docker flag"
    )
    def test_docker_image_builds(self):
        """Test Docker image builds successfully."""
        result = subprocess.run(
            ["docker", "build", "-f", "docker/Dockerfile", "-t", "payments-agent:test", "."],
            capture_output=True,
            text=True,
            timeout=300,
        )
        assert result.returncode == 0, f"Docker build failed: {result.stderr}"

    @pytest.mark.skipif(
        not pytest.config.getoption("--test-docker", default=False),
        reason="Docker tests require --test-docker flag"
    )
    def test_docker_image_has_dependencies(self):
        """Test Docker image has all required dependencies."""
        result = subprocess.run(
            [
                "docker", "run", "--rm",
                "--env", "GOOGLE_API_KEY=test-key",
                "payments-agent:test",
                "python", "-c",
                "from google.adk import Agent; from fastapi import FastAPI; from pydantic import BaseModel; print('OK')"
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"Dependencies check failed: {result.stderr}"
        assert "OK" in result.stdout

    @pytest.mark.skipif(
        not pytest.config.getoption("--test-docker", default=False),
        reason="Docker tests require --test-docker flag"
    )
    def test_docker_compose_builds(self):
        """Test docker-compose builds successfully."""
        result = subprocess.run(
            ["docker-compose", "build"],
            capture_output=True,
            text=True,
            timeout=300,
        )
        assert result.returncode == 0, f"docker-compose build failed: {result.stderr}"

    @pytest.mark.skipif(
        not pytest.config.getoption("--test-docker", default=False),
        reason="Docker tests require --test-docker flag"
    )
    def test_docker_compose_starts(self):
        """Test docker-compose starts container successfully."""
        try:
            # Start container
            subprocess.run(
                ["docker-compose", "up", "-d"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            
            # Wait for container to be ready
            time.sleep(5)
            
            # Check container is running
            result = subprocess.run(
                ["docker-compose", "ps"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            assert "payments-agent" in result.stdout
            assert "Up" in result.stdout
            
        finally:
            # Cleanup
            subprocess.run(
                ["docker-compose", "down"],
                capture_output=True,
                text=True,
                timeout=30,
            )

