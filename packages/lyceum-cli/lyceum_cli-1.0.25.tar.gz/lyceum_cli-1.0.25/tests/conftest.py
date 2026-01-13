"""Shared pytest fixtures for CLI tests."""

import json
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest


# --- Basic Fixtures ---


@pytest.fixture
def mock_execution_id() -> str:
    """Consistent execution ID for testing."""
    return "550e8400-e29b-41d4-a716-446655440000"


@pytest.fixture
def mock_streaming_url(mock_execution_id) -> str:
    """Mock streaming URL."""
    return f"https://api.lyceum.dev/stream/{mock_execution_id}"


# --- Config Fixtures ---


@pytest.fixture
def mock_config_data() -> dict:
    """Mock config file data."""
    return {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjk5OTk5OTk5OTl9.test",
        "refresh_token": "test-refresh-token",
        "base_url": "https://api.lyceum.dev",
    }


@pytest.fixture
def setup_config_file(tmp_path, mock_config_data):
    """Setup mock config file in tmp directory."""

    def _setup(config_data: dict = None):
        config_dir = tmp_path / ".lyceum"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / "config.json"
        config_file.write_text(json.dumps(config_data or mock_config_data))
        return config_file

    return _setup


# --- HTTP Response Fixtures (following PR #502 pattern) ---


@pytest.fixture
def setup_httpx_response():
    """Setup mock for httpx response."""

    def _setup(status_code: int = 200, json_data: dict = None, text: str = "OK"):
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = json_data or {}
        mock_response.text = text
        mock_response.content = text.encode()
        return mock_response

    return _setup


@pytest.fixture
def setup_httpx_post(setup_httpx_response):
    """Setup mock for httpx.post calls."""

    def _setup(status_code: int = 200, execution_id: str = "test-exec-id"):
        response = setup_httpx_response(
            status_code=status_code,
            json_data={
                "execution_id": execution_id,
                "streaming_url": f"https://api.lyceum.dev/stream/{execution_id}",
                "status": "queued",
            },
        )
        return response

    return _setup


@pytest.fixture
def setup_httpx_stream():
    """Setup mock for httpx.stream SSE responses."""

    def _setup(events: list[dict], status_code: int = 200):
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.iter_lines.return_value = [
            f"data: {json.dumps(event)}" for event in events
        ]

        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_response
        mock_context.__exit__.return_value = None

        return mock_context

    return _setup


# --- Machine/Quota Fixtures ---


@pytest.fixture
def setup_available_machines():
    """Setup mock for available machines API response."""

    def _setup(machines: list[str] = None):
        machines = machines or ["cpu", "a100", "h100"]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "hardware_profiles": [{"hardware_profile": m} for m in machines]
        }
        return mock_response

    return _setup


# --- File System Fixtures ---


@pytest.fixture
def sample_workspace(tmp_path):
    """Create a sample workspace with Python files and packages."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    # Main file
    main_py = workspace / "main.py"
    main_py.write_text(
        '''"""Main script"""
import numpy as np
from mypackage import helper_function
from standalone import standalone_func

def main():
    print(helper_function())
    print(standalone_func())

if __name__ == "__main__":
    main()
'''
    )

    # Package
    pkg = workspace / "mypackage"
    pkg.mkdir()
    (pkg / "__init__.py").write_text(
        '''"""My package"""
from .utils import helper_function
'''
    )
    (pkg / "utils.py").write_text(
        '''"""Utils module"""
def helper_function():
    return "Hello from utils"
'''
    )

    # Standalone module
    (workspace / "standalone.py").write_text(
        '''"""Standalone module"""
def standalone_func():
    return "Hello from standalone"
'''
    )

    # Requirements file
    (workspace / "requirements.txt").write_text("numpy==1.24.0\n")

    return workspace


@pytest.fixture
def sample_workspace_config(sample_workspace):
    """Create .lyceum/config.json in sample workspace."""

    def _setup(config_data: dict = None):
        lyceum_dir = sample_workspace / ".lyceum"
        lyceum_dir.mkdir()
        config_file = lyceum_dir / "config.json"

        default_config = {
            "workspace": str(sample_workspace),
            "dependencies": {"merged": ["numpy==1.24.0"]},
            "local_packages": ["mypackage"],
        }
        config_file.write_text(json.dumps(config_data or default_config))
        return config_file

    return _setup
