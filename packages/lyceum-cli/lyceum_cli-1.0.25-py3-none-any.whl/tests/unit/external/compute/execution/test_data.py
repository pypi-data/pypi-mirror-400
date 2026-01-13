"""Shared test data for CLI tests."""

VALID_EXECUTION_PAYLOAD = {
    "code": "print('hello')",
    "execution_type": "cpu",
    "timeout": 60,
}

VALID_EXECUTION_WITH_REQUIREMENTS = {
    **VALID_EXECUTION_PAYLOAD,
    "requirements_content": "numpy==1.24.0",
}

VALID_EXECUTION_WITH_IMPORTS = {
    **VALID_EXECUTION_PAYLOAD,
    "import_files": '{"mypackage/__init__.py": "# init", "mypackage/utils.py": "def foo(): pass"}',
}

SAMPLE_SSE_OUTPUT_EVENT = {"output": {"content": "Hello, World!\n"}}

SAMPLE_SSE_JOB_FINISHED = {
    "jobFinished": {"job": {"result": {"returnCode": "0"}}}
}

SAMPLE_SSE_JOB_FAILED = {
    "jobFinished": {"job": {"result": {"returnCode": "1"}}}
}

SAMPLE_WORKSPACE_CONFIG = {
    "workspace": "/path/to/workspace",
    "dependencies": {"merged": ["numpy==1.24.0", "pandas>=2.0.0"]},
    "local_packages": ["mypackage"],
}
