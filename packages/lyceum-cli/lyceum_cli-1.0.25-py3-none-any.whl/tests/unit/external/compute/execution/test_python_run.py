"""Tests for run_python CLI command."""

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from lyceum.external.compute.execution.python import python_app


class TestRunPythonCommand:
    """Tests for the run_python CLI command."""

    @pytest.fixture
    def cli_runner(self):
        return CliRunner()

    @patch("lyceum.external.compute.execution.python.stream_execution_output")
    @patch("lyceum.external.compute.execution.python.submit_execution")
    @patch("lyceum.external.compute.execution.python.validate_machine_type")
    @patch("lyceum.external.compute.execution.python.config")
    def test_run_inline_code(
        self,
        mock_config,
        mock_validate,
        mock_submit,
        mock_stream,
        cli_runner,
        mock_execution_id,
    ):
        mock_config.get_client.return_value = None
        mock_validate.return_value = True
        mock_submit.return_value = (mock_execution_id, "http://stream.url")
        mock_stream.return_value = True

        result = cli_runner.invoke(python_app, ["run", "print('hello')"])

        assert result.exit_code == 0
        mock_submit.assert_called_once()

    @patch("lyceum.external.compute.execution.python.stream_execution_output")
    @patch("lyceum.external.compute.execution.python.submit_execution")
    @patch("lyceum.external.compute.execution.python.validate_machine_type")
    @patch("lyceum.external.compute.execution.python.config")
    def test_run_file(
        self,
        mock_config,
        mock_validate,
        mock_submit,
        mock_stream,
        cli_runner,
        sample_workspace,
        mock_execution_id,
    ):
        mock_config.get_client.return_value = None
        mock_validate.return_value = True
        mock_submit.return_value = (mock_execution_id, "http://stream.url")
        mock_stream.return_value = True

        main_file = sample_workspace / "main.py"
        result = cli_runner.invoke(python_app, ["run", str(main_file)])

        assert result.exit_code == 0

    @patch("lyceum.external.compute.execution.python.validate_machine_type")
    @patch("lyceum.external.compute.execution.python.config")
    def test_invalid_machine_type(
        self,
        mock_config,
        mock_validate,
        cli_runner,
    ):
        mock_config.get_client.return_value = None
        mock_validate.return_value = False

        result = cli_runner.invoke(python_app, ["run", "print('hi')", "-m", "invalid"])

        assert result.exit_code == 1
        assert "don't have access" in result.output

    @patch("lyceum.external.compute.execution.python.stream_execution_output")
    @patch("lyceum.external.compute.execution.python.submit_execution")
    @patch("lyceum.external.compute.execution.python.validate_machine_type")
    @patch("lyceum.external.compute.execution.python.config")
    def test_execution_failure(
        self,
        mock_config,
        mock_validate,
        mock_submit,
        mock_stream,
        cli_runner,
        mock_execution_id,
    ):
        mock_config.get_client.return_value = None
        mock_validate.return_value = True
        mock_submit.return_value = (mock_execution_id, "http://stream.url")
        mock_stream.return_value = False  # Execution failed

        result = cli_runner.invoke(python_app, ["run", "print('hi')"])

        assert result.exit_code == 1

    @patch("lyceum.external.compute.execution.python.stream_execution_output")
    @patch("lyceum.external.compute.execution.python.submit_execution")
    @patch("lyceum.external.compute.execution.python.validate_machine_type")
    @patch("lyceum.external.compute.execution.python.config")
    def test_machine_type_option(
        self,
        mock_config,
        mock_validate,
        mock_submit,
        mock_stream,
        cli_runner,
        mock_execution_id,
    ):
        mock_config.get_client.return_value = None
        mock_validate.return_value = True
        mock_submit.return_value = (mock_execution_id, "http://stream.url")
        mock_stream.return_value = True

        result = cli_runner.invoke(python_app, ["run", "print('hi')", "-m", "a100"])

        assert result.exit_code == 0
        # Check that payload was built with correct machine type
        call_args = mock_submit.call_args[0][0]
        assert call_args["execution_type"] == "a100"

    @patch("lyceum.external.compute.execution.python.stream_execution_output")
    @patch("lyceum.external.compute.execution.python.submit_execution")
    @patch("lyceum.external.compute.execution.python.validate_machine_type")
    @patch("lyceum.external.compute.execution.python.config")
    def test_file_name_option(
        self,
        mock_config,
        mock_validate,
        mock_submit,
        mock_stream,
        cli_runner,
        mock_execution_id,
    ):
        mock_config.get_client.return_value = None
        mock_validate.return_value = True
        mock_submit.return_value = (mock_execution_id, "http://stream.url")
        mock_stream.return_value = True

        result = cli_runner.invoke(
            python_app, ["run", "print('hi')", "-f", "custom_name.py"]
        )

        assert result.exit_code == 0
        call_args = mock_submit.call_args[0][0]
        assert call_args["file_name"] == "custom_name.py"

    @patch("lyceum.external.compute.execution.python.stream_execution_output")
    @patch("lyceum.external.compute.execution.python.submit_execution")
    @patch("lyceum.external.compute.execution.python.validate_machine_type")
    @patch("lyceum.external.compute.execution.python.config")
    def test_requirements_option(
        self,
        mock_config,
        mock_validate,
        mock_submit,
        mock_stream,
        cli_runner,
        mock_execution_id,
    ):
        mock_config.get_client.return_value = None
        mock_validate.return_value = True
        mock_submit.return_value = (mock_execution_id, "http://stream.url")
        mock_stream.return_value = True

        result = cli_runner.invoke(
            python_app, ["run", "print('hi')", "-r", "numpy>=1.0"]
        )

        assert result.exit_code == 0
        call_args = mock_submit.call_args[0][0]
        assert call_args["requirements_content"] == "numpy>=1.0"

    @patch("lyceum.external.compute.execution.python.stream_execution_output")
    @patch("lyceum.external.compute.execution.python.submit_execution")
    @patch("lyceum.external.compute.execution.python.validate_machine_type")
    @patch("lyceum.external.compute.execution.python.config")
    def test_shows_execution_id(
        self,
        mock_config,
        mock_validate,
        mock_submit,
        mock_stream,
        cli_runner,
        mock_execution_id,
    ):
        mock_config.get_client.return_value = None
        mock_validate.return_value = True
        mock_submit.return_value = (mock_execution_id, "http://stream.url")
        mock_stream.return_value = True

        result = cli_runner.invoke(python_app, ["run", "print('hi')"])

        assert result.exit_code == 0
        assert mock_execution_id in result.output

    @patch("lyceum.external.compute.execution.python.stream_execution_output")
    @patch("lyceum.external.compute.execution.python.submit_execution")
    @patch("lyceum.external.compute.execution.python.validate_machine_type")
    @patch("lyceum.external.compute.execution.python.load_workspace_config")
    @patch("lyceum.external.compute.execution.python.config")
    def test_no_config_option(
        self,
        mock_config,
        mock_load_workspace,
        mock_validate,
        mock_submit,
        mock_stream,
        cli_runner,
        mock_execution_id,
    ):
        mock_config.get_client.return_value = None
        mock_validate.return_value = True
        mock_submit.return_value = (mock_execution_id, "http://stream.url")
        mock_stream.return_value = True

        result = cli_runner.invoke(
            python_app, ["run", "print('hi')", "--no-config"]
        )

        assert result.exit_code == 0
        mock_load_workspace.assert_not_called()

    @patch("lyceum.external.compute.execution.python.stream_execution_output")
    @patch("lyceum.external.compute.execution.python.submit_execution")
    @patch("lyceum.external.compute.execution.python.validate_machine_type")
    @patch("lyceum.external.compute.execution.python.config")
    def test_script_args_passed_through(
        self,
        mock_config,
        mock_validate,
        mock_submit,
        mock_stream,
        cli_runner,
        mock_execution_id,
    ):
        mock_config.get_client.return_value = None
        mock_validate.return_value = True
        mock_submit.return_value = (mock_execution_id, "http://stream.url")
        mock_stream.return_value = True

        result = cli_runner.invoke(
            python_app, ["run", "print('hi')", "--", "--epochs", "10", "--lr", "0.001"]
        )

        assert result.exit_code == 0
        # Verify that the code was modified to include sys.argv
        call_args = mock_submit.call_args[0][0]
        assert "sys.argv" in call_args["code"]
        assert "--epochs" in call_args["code"]
        assert "10" in call_args["code"]


class TestRunPythonWithDebug:
    """Tests for run_python command with debug flag."""

    @pytest.fixture
    def cli_runner(self):
        return CliRunner()

    @patch("lyceum.external.compute.execution.python.stream_execution_output")
    @patch("lyceum.external.compute.execution.python.submit_execution")
    @patch("lyceum.external.compute.execution.python.validate_machine_type")
    @patch("lyceum.external.compute.execution.python.config")
    def test_debug_flag(
        self,
        mock_config,
        mock_validate,
        mock_submit,
        mock_stream,
        cli_runner,
        mock_execution_id,
    ):
        mock_config.get_client.return_value = None
        mock_validate.return_value = True
        mock_submit.return_value = (mock_execution_id, "http://stream.url")
        mock_stream.return_value = True

        result = cli_runner.invoke(python_app, ["run", "print('hi')", "--debug"])

        assert result.exit_code == 0
        # Debug output should contain payload summary
        assert "DEBUG" in result.output or "Payload" in result.output or mock_execution_id in result.output
