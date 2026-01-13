"""Tests for Python execution helper functions."""

import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.exceptions import Exit as ClickExit

from lyceum.external.compute.execution.python import (
    build_payload,
    inject_script_args,
    load_workspace_config,
    read_code_from_source,
    resolve_import_files,
    resolve_requirements,
    submit_execution,
    validate_machine_type,
)


class TestReadCodeFromSource:
    """Tests for read_code_from_source function."""

    def test_reads_from_file(self, tmp_path):
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        code, file_path, file_name = read_code_from_source(str(test_file))

        assert code == "print('hello')"
        assert file_path == test_file
        assert file_name == "test.py"

    def test_returns_inline_code(self):
        code, file_path, file_name = read_code_from_source("print('inline')")

        assert code == "print('inline')"
        assert file_path is None
        assert file_name is None

    def test_reads_multiline_file(self, tmp_path):
        test_file = tmp_path / "multi.py"
        test_file.write_text("line1\nline2\nline3")

        code, file_path, file_name = read_code_from_source(str(test_file))

        assert code == "line1\nline2\nline3"
        assert file_name == "multi.py"

    def test_with_status_line(self, tmp_path):
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        mock_status = MagicMock()
        code, file_path, file_name = read_code_from_source(str(test_file), status=mock_status)

        mock_status.update.assert_called_once()
        assert "test.py" in mock_status.update.call_args[0][0]


class TestInjectScriptArgs:
    """Tests for inject_script_args function."""

    def test_injects_args(self):
        code = "print(sys.argv)"
        result = inject_script_args(code, ["--flag", "value"], "script.py")

        assert "sys.argv" in result
        assert "script.py" in result
        assert "--flag" in result
        assert "value" in result

    def test_no_injection_without_args(self):
        code = "print('hello')"
        result = inject_script_args(code, [], "script.py")

        assert result == code

    def test_uses_default_script_name(self):
        code = "print(sys.argv)"
        result = inject_script_args(code, ["arg1"], None)

        assert "script.py" in result

    def test_preserves_original_code(self):
        code = "original = 'code'\nprint(original)"
        result = inject_script_args(code, ["--test"], "test.py")

        assert "original = 'code'" in result
        assert "print(original)" in result


class TestResolveRequirements:
    """Tests for resolve_requirements function."""

    def test_from_file(self, tmp_path):
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("numpy==1.24.0\npandas>=2.0.0")

        result = resolve_requirements(str(req_file), None)

        assert "numpy==1.24.0" in result
        assert "pandas>=2.0.0" in result

    def test_from_string(self):
        result = resolve_requirements("numpy>=1.0", None)

        assert result == "numpy>=1.0"

    def test_from_workspace_config(self):
        workspace_config = {"dependencies": {"merged": ["numpy==1.24.0", "pandas>=2.0.0"]}}

        result = resolve_requirements(None, workspace_config)

        assert "numpy==1.24.0" in result
        assert "pandas>=2.0.0" in result

    def test_returns_none_when_empty(self):
        result = resolve_requirements(None, None)

        assert result is None

    def test_returns_none_for_empty_config(self):
        workspace_config = {"dependencies": {"merged": []}}

        result = resolve_requirements(None, workspace_config)

        assert result is None

    def test_returns_none_for_missing_deps(self):
        workspace_config = {"other_key": "value"}

        result = resolve_requirements(None, workspace_config)

        assert result is None

    def test_explicit_takes_precedence(self, tmp_path):
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("explicit==1.0.0")

        workspace_config = {"dependencies": {"merged": ["config==2.0.0"]}}

        result = resolve_requirements(str(req_file), workspace_config)

        assert "explicit==1.0.0" in result
        assert "config==2.0.0" not in result


class TestResolveImportFiles:
    """Tests for resolve_import_files function."""

    def test_resolves_local_imports(self, sample_workspace):
        sys.path.insert(0, str(sample_workspace))
        try:
            main_file = sample_workspace / "main.py"
            result = resolve_import_files(main_file, None)

            assert result is not None
            parsed = json.loads(result)

            # Should contain package files
            keys = list(parsed.keys())
            assert len(keys) > 0
        finally:
            sys.path.remove(str(sample_workspace))

    def test_returns_none_for_no_file(self):
        result = resolve_import_files(None, None)

        assert result is None

    def test_returns_none_for_nonexistent_file(self, tmp_path):
        nonexistent = tmp_path / "nonexistent.py"

        result = resolve_import_files(nonexistent, None)

        assert result is None

    def test_returns_none_for_no_imports(self, tmp_path):
        simple_file = tmp_path / "simple.py"
        simple_file.write_text("print('hello')")

        result = resolve_import_files(simple_file, None)

        # No local imports, so returns None
        assert result is None

    def test_uses_workspace_config_root(self, sample_workspace, sample_workspace_config):
        sample_workspace_config()

        sys.path.insert(0, str(sample_workspace))
        try:
            main_file = sample_workspace / "main.py"

            workspace_config = {
                "_config_dir": sample_workspace,
                "dependencies": {"merged": []},
            }

            result = resolve_import_files(main_file, workspace_config)

            assert result is not None
        finally:
            sys.path.remove(str(sample_workspace))


class TestBuildPayload:
    """Tests for build_payload function."""

    def test_minimal_payload(self):
        payload = build_payload(code="print('hello')", machine_type="cpu")

        assert payload["code"] == "print('hello')"
        assert payload["execution_type"] == "cpu"
        assert "timeout" in payload
        assert payload["nbcode"] == 0

    def test_full_payload(self):
        payload = build_payload(
            code="print('hello')",
            machine_type="a100",
            file_name="test.py",
            requirements_content="numpy>=1.0",
            imports=["os", "sys"],
            import_files='{"test.py": "code"}',
        )

        assert payload["execution_type"] == "a100"
        assert payload["file_name"] == "test.py"
        assert payload["requirements_content"] == "numpy>=1.0"
        assert payload["prior_imports"] == ["os", "sys"]
        assert payload["import_files"] == '{"test.py": "code"}'

    def test_omits_none_values(self):
        payload = build_payload(
            code="print('hello')",
            machine_type="cpu",
            file_name=None,
            requirements_content=None,
        )

        assert "file_name" not in payload
        assert "requirements_content" not in payload


class TestSubmitExecution:
    """Tests for submit_execution function."""

    @patch("lyceum.external.compute.execution.python.httpx.post")
    @patch("lyceum.external.compute.execution.python.config")
    def test_success(self, mock_config, mock_post, setup_httpx_post, mock_execution_id):
        mock_config.base_url = "https://api.lyceum.dev"
        mock_config.api_key = "test-key"
        mock_post.return_value = setup_httpx_post(execution_id=mock_execution_id)

        exec_id, stream_url = submit_execution({"code": "print('hi')"})

        assert exec_id == mock_execution_id
        assert stream_url is not None

    @patch("lyceum.external.compute.execution.python.httpx.post")
    @patch("lyceum.external.compute.execution.python.config")
    def test_auth_error(self, mock_config, mock_post, setup_httpx_response):
        mock_config.base_url = "https://api.lyceum.dev"
        mock_config.api_key = "invalid-key"
        mock_post.return_value = setup_httpx_response(status_code=401, text="Unauthorized")

        with pytest.raises(ClickExit):
            submit_execution({"code": "print('hi')"})

    @patch("lyceum.external.compute.execution.python.httpx.post")
    @patch("lyceum.external.compute.execution.python.config")
    def test_server_error(self, mock_config, mock_post, setup_httpx_response):
        mock_config.base_url = "https://api.lyceum.dev"
        mock_config.api_key = "test-key"
        mock_post.return_value = setup_httpx_response(status_code=500, text="Server Error")

        with pytest.raises(ClickExit):
            submit_execution({"code": "print('hi')"})

    @patch("lyceum.external.compute.execution.python.httpx.post")
    @patch("lyceum.external.compute.execution.python.config")
    def test_with_status_line(self, mock_config, mock_post, setup_httpx_post, mock_execution_id):
        mock_config.base_url = "https://api.lyceum.dev"
        mock_config.api_key = "test-key"
        mock_post.return_value = setup_httpx_post(execution_id=mock_execution_id)

        mock_status = MagicMock()
        exec_id, stream_url = submit_execution({"code": "print('hi')"}, status=mock_status)

        mock_status.update.assert_called_once_with("Submitting execution...")


class TestValidateMachineType:
    """Tests for validate_machine_type function."""

    @patch("lyceum.external.compute.execution.python.get_available_machines")
    def test_valid_machine(self, mock_get_machines):
        mock_get_machines.return_value = ["cpu", "a100", "h100"]

        assert validate_machine_type("cpu") is True
        assert validate_machine_type("a100") is True

    @patch("lyceum.external.compute.execution.python.get_available_machines")
    def test_invalid_machine(self, mock_get_machines):
        mock_get_machines.return_value = ["cpu"]

        assert validate_machine_type("a100") is False

    @patch("lyceum.external.compute.execution.python.get_available_machines")
    def test_empty_available_returns_true(self, mock_get_machines):
        # When we can't fetch available machines, assume valid
        mock_get_machines.return_value = []

        assert validate_machine_type("any_machine") is True


class TestLoadWorkspaceConfig:
    """Tests for load_workspace_config function."""

    def test_finds_config_in_workspace(self, sample_workspace, sample_workspace_config):
        sample_workspace_config()

        main_file = sample_workspace / "main.py"

        # Change cwd to tmp to avoid picking up real config
        original_cwd = os.getcwd()
        try:
            os.chdir(sample_workspace)
            config = load_workspace_config(main_file)
        finally:
            os.chdir(original_cwd)

        assert config is not None
        assert "dependencies" in config

    def test_returns_none_without_config(self, tmp_path):
        # Create a completely isolated workspace with no .lyceum config
        isolated = tmp_path / "isolated_workspace"
        isolated.mkdir()
        main_file = isolated / "main.py"
        main_file.write_text("print('hello')")

        # Change cwd to the isolated dir to avoid picking up real config
        original_cwd = os.getcwd()
        try:
            os.chdir(isolated)
            config = load_workspace_config(main_file)
        finally:
            os.chdir(original_cwd)

        assert config is None

    def test_searches_parent_directories(self, sample_workspace, sample_workspace_config):
        sample_workspace_config()

        # Create a nested file
        nested_dir = sample_workspace / "nested" / "deep"
        nested_dir.mkdir(parents=True)
        nested_file = nested_dir / "script.py"
        nested_file.write_text("print('hi')")

        original_cwd = os.getcwd()
        try:
            os.chdir(sample_workspace)
            config = load_workspace_config(nested_file)
        finally:
            os.chdir(original_cwd)

        assert config is not None
        assert "_config_dir" in config

    def test_returns_none_for_nonexistent_file(self, tmp_path):
        # Create an isolated directory
        isolated = tmp_path / "isolated"
        isolated.mkdir()
        nonexistent = isolated / "nonexistent.py"

        original_cwd = os.getcwd()
        try:
            os.chdir(isolated)
            config = load_workspace_config(nonexistent)
        finally:
            os.chdir(original_cwd)

        # Should not crash, returns None
        assert config is None

    def test_adds_config_dir_to_result(self, sample_workspace, sample_workspace_config):
        sample_workspace_config()

        main_file = sample_workspace / "main.py"

        original_cwd = os.getcwd()
        try:
            os.chdir(sample_workspace)
            config = load_workspace_config(main_file)
        finally:
            os.chdir(original_cwd)

        assert config is not None
        assert "_config_dir" in config
        assert config["_config_dir"] == sample_workspace
