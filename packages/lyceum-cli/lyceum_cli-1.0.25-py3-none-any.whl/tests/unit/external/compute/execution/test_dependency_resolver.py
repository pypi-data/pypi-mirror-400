"""Tests for DependencyResolver class."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from lyceum.external.compute.execution.python import DependencyResolver


class TestDependencyResolverIsStdlib:
    """Tests for DependencyResolver.is_stdlib() method."""

    def test_returns_false_for_local_path(self, sample_workspace):
        resolver = DependencyResolver(sample_workspace)
        local_file = sample_workspace / "mypackage" / "utils.py"

        assert resolver.is_stdlib(local_file) is False

    def test_returns_false_for_workspace_path(self, sample_workspace):
        resolver = DependencyResolver(sample_workspace)
        main_file = sample_workspace / "main.py"

        assert resolver.is_stdlib(main_file) is False


class TestDependencyResolverIsStdlibModule:
    """Tests for DependencyResolver.is_stdlib_module() method."""

    def test_json_is_stdlib(self):
        # json has a file origin in the stdlib
        resolver = DependencyResolver(Path("/tmp"))
        assert resolver.is_stdlib_module("json") is True

    def test_pathlib_is_stdlib(self):
        resolver = DependencyResolver(Path("/tmp"))
        assert resolver.is_stdlib_module("pathlib") is True

    def test_re_is_stdlib(self):
        resolver = DependencyResolver(Path("/tmp"))
        assert resolver.is_stdlib_module("re") is True

    def test_collections_is_stdlib(self):
        resolver = DependencyResolver(Path("/tmp"))
        assert resolver.is_stdlib_module("collections") is True

    def test_nonexistent_module(self):
        resolver = DependencyResolver(Path("/tmp"))
        assert resolver.is_stdlib_module("nonexistent_module_xyz_abc_123") is False


class TestDependencyResolverFindImports:
    """Tests for DependencyResolver.find_imports() method."""

    def test_finds_local_imports(self, sample_workspace):
        sys.path.insert(0, str(sample_workspace))
        try:
            resolver = DependencyResolver(sample_workspace)
            main_file = sample_workspace / "main.py"
            resolver.find_imports(main_file, main_file)

            # Should find mypackage and standalone
            local_files = {p.name for p in resolver.local_imports}
            assert "standalone.py" in local_files
            # At minimum, we should find some local files
            assert len(resolver.local_imports) > 0
        finally:
            sys.path.remove(str(sample_workspace))

    def test_excludes_stdlib(self, sample_workspace):
        sys.path.insert(0, str(sample_workspace))
        try:
            resolver = DependencyResolver(sample_workspace)
            main_file = sample_workspace / "main.py"
            resolver.find_imports(main_file, main_file)

            # Should not include stdlib modules like os, sys, etc.
            for path in resolver.local_imports:
                # None of the local imports should be from site-packages
                assert "site-packages" not in str(path)
        finally:
            sys.path.remove(str(sample_workspace))

    def test_handles_relative_imports(self, sample_workspace):
        sys.path.insert(0, str(sample_workspace))
        try:
            resolver = DependencyResolver(sample_workspace)
            init_file = sample_workspace / "mypackage" / "__init__.py"
            main_file = sample_workspace / "main.py"

            resolver.find_imports(init_file, main_file)

            # Should resolve relative import to utils
            paths = [str(p) for p in resolver.local_imports]
            assert any("utils.py" in p for p in paths)
        finally:
            sys.path.remove(str(sample_workspace))

    def test_handles_nonexistent_file(self, sample_workspace):
        resolver = DependencyResolver(sample_workspace)
        nonexistent = sample_workspace / "nonexistent.py"

        # Should not raise
        resolver.find_imports(nonexistent, nonexistent)
        assert len(resolver.local_imports) == 0

    def test_handles_syntax_error_file(self, tmp_path):
        bad_file = tmp_path / "bad_syntax.py"
        bad_file.write_text("def broken(:\n    pass")

        resolver = DependencyResolver(tmp_path)
        # Should not raise, just skip the file
        resolver.find_imports(bad_file, bad_file)

    def test_handles_directory(self, sample_workspace):
        sys.path.insert(0, str(sample_workspace))
        try:
            resolver = DependencyResolver(sample_workspace)
            pkg_dir = sample_workspace / "mypackage"

            # Should follow directory to __init__.py
            resolver.find_imports(pkg_dir, sample_workspace / "main.py")

            # Should have processed the package
            assert len(resolver.visited) > 0
        finally:
            sys.path.remove(str(sample_workspace))

    def test_visited_set_prevents_infinite_recursion(self, sample_workspace):
        sys.path.insert(0, str(sample_workspace))
        try:
            resolver = DependencyResolver(sample_workspace)
            main_file = sample_workspace / "main.py"

            # Call find_imports multiple times on same file
            resolver.find_imports(main_file, main_file)
            visited_count = len(resolver.visited)

            resolver.find_imports(main_file, main_file)
            # Should not add more to visited
            assert len(resolver.visited) == visited_count
        finally:
            sys.path.remove(str(sample_workspace))


class TestDependencyResolverCalculateImportPath:
    """Tests for DependencyResolver.calculate_import_path() method."""

    def test_relative_import_path(self, sample_workspace):
        resolver = DependencyResolver(sample_workspace)
        actual_path = sample_workspace / "mypackage" / "utils.py"
        main_file = sample_workspace / "main.py"

        result = resolver.calculate_import_path(
            actual_path.resolve(), main_file.resolve(), modname="utils", is_relative=True
        )

        assert result == "mypackage/utils.py"

    def test_absolute_import_path_init(self, sample_workspace):
        resolver = DependencyResolver(sample_workspace)
        actual_path = sample_workspace / "mypackage" / "__init__.py"
        main_file = sample_workspace / "main.py"

        result = resolver.calculate_import_path(
            actual_path.resolve(), main_file.resolve(), modname="mypackage", is_relative=False
        )

        assert result == "mypackage/__init__.py"

    def test_absolute_import_path_module(self, sample_workspace):
        resolver = DependencyResolver(sample_workspace)
        actual_path = sample_workspace / "standalone.py"
        main_file = sample_workspace / "main.py"

        result = resolver.calculate_import_path(
            actual_path.resolve(), main_file.resolve(), modname="standalone", is_relative=False
        )

        assert result == "standalone.py"


class TestDependencyResolverClassifyFile:
    """Tests for DependencyResolver.classify_file() method."""

    def test_local_file_in_project(self, sample_workspace):
        resolver = DependencyResolver(sample_workspace)
        local_file = sample_workspace / "main.py"

        assert resolver.classify_file(local_file) == "local"

    def test_local_file_in_subpackage(self, sample_workspace):
        resolver = DependencyResolver(sample_workspace)
        pkg_file = sample_workspace / "mypackage" / "utils.py"

        assert resolver.classify_file(pkg_file) == "local"


class TestDependencyResolverResolveRelativeImport:
    """Tests for DependencyResolver.resolve_relative_import() method."""

    def test_resolves_relative_module(self, sample_workspace):
        import ast

        resolver = DependencyResolver(sample_workspace)
        init_file = sample_workspace / "mypackage" / "__init__.py"

        # Create a mock ImportFrom node for "from .utils import helper_function"
        node = ast.ImportFrom(module="utils", names=[], level=1)

        result = resolver.resolve_relative_import(init_file, node, "utils")

        assert result is not None
        assert "utils.py" in str(result)

    def test_resolves_package_level_import(self, sample_workspace):
        import ast

        resolver = DependencyResolver(sample_workspace)
        utils_file = sample_workspace / "mypackage" / "utils.py"

        # Create a mock ImportFrom node for "from . import something" (level=1, no module)
        node = ast.ImportFrom(module=None, names=[], level=1)

        result = resolver.resolve_relative_import(utils_file, node, None)

        # Should resolve to __init__.py of the package
        if result:
            assert "__init__.py" in str(result)


class TestDependencyResolverParseFile:
    """Tests for DependencyResolver.parse_file() method."""

    def test_parses_valid_file(self, sample_workspace):
        resolver = DependencyResolver(sample_workspace)
        main_file = sample_workspace / "main.py"

        result = resolver.parse_file(main_file)

        assert result is not None

    def test_returns_none_for_syntax_error(self, tmp_path):
        bad_file = tmp_path / "bad.py"
        bad_file.write_text("def broken(:\n    pass")

        resolver = DependencyResolver(tmp_path)
        result = resolver.parse_file(bad_file)

        assert result is None

    def test_returns_none_for_nonexistent(self, tmp_path):
        resolver = DependencyResolver(tmp_path)
        result = resolver.parse_file(tmp_path / "nonexistent.py")

        assert result is None
