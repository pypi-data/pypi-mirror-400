"""Shared utilities for Python import analysis and resolution."""

import ast
import importlib.util
import site
import sys
import sysconfig
from pathlib import Path
from typing import Optional


# Standard library path
stdlib_path = Path(sysconfig.get_paths()["stdlib"]).resolve()

# Site-packages paths
site_packages: set[Path] = set()
try:
    for p in site.getsitepackages():
        site_packages.add(Path(p).resolve())
    user_site = site.getusersitepackages()
    if user_site:
        for p in user_site.split(":"):
            if p:
                site_packages.add(Path(p).resolve())
except Exception:
    pass

# Known standard library modules (for fast lookup without spec resolution)
STDLIB_MODULES = {
    "abc", "argparse", "ast", "asyncio", "base64", "bisect", "calendar",
    "collections", "concurrent", "contextlib", "copy", "csv", "ctypes",
    "dataclasses", "datetime", "decimal", "difflib", "dis", "email",
    "enum", "errno", "faulthandler", "filecmp", "fileinput", "fnmatch",
    "fractions", "functools", "gc", "getopt", "getpass", "glob", "gzip",
    "hashlib", "heapq", "hmac", "html", "http", "imaplib", "importlib",
    "inspect", "io", "ipaddress", "itertools", "json", "keyword",
    "linecache", "locale", "logging", "lzma", "mailbox", "math",
    "mimetypes", "mmap", "modulefinder", "multiprocessing", "netrc",
    "numbers", "operator", "os", "pathlib", "pdb", "pickle", "pickletools",
    "pkgutil", "platform", "plistlib", "poplib", "posixpath", "pprint",
    "profile", "pstats", "pty", "pwd", "py_compile", "pyclbr", "pydoc",
    "queue", "quopri", "random", "re", "readline", "reprlib", "resource",
    "rlcompleter", "runpy", "sched", "secrets", "select", "selectors",
    "shelve", "shlex", "shutil", "signal", "site", "smtpd", "smtplib",
    "sndhdr", "socket", "socketserver", "sqlite3", "ssl", "stat",
    "statistics", "string", "stringprep", "struct", "subprocess",
    "sunau", "symtable", "sys", "sysconfig", "syslog", "tabnanny",
    "tarfile", "telnetlib", "tempfile", "termios", "test", "textwrap",
    "threading", "time", "timeit", "tkinter", "token", "tokenize",
    "trace", "traceback", "tracemalloc", "tty", "turtle", "turtledemo",
    "types", "typing", "unicodedata", "unittest", "urllib", "uu", "uuid",
    "venv", "warnings", "wave", "weakref", "webbrowser", "winreg",
    "winsound", "wsgiref", "xdrlib", "xml", "xmlrpc", "zipapp",
    "zipfile", "zipimport", "zlib", "_thread",
}

# Directories to skip when scanning
SKIP_DIRS = {
    ".git", ".hg", ".svn",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "venv", "env", ".venv", ".env",
    "node_modules",
    ".lyceum",
    "build", "dist",
}


def is_stdlib_module_by_name(name: str) -> bool:
    """Check if a module name is part of the standard library (fast lookup)."""
    if name in sys.builtin_module_names:
        return True
    return name in STDLIB_MODULES


def is_stdlib_path(path: Path) -> bool:
    """Check if a path is in the standard library."""
    for site_pkg in site_packages:
        try:
            path.relative_to(site_pkg)
            return False
        except ValueError:
            continue
    return stdlib_path in path.parents


def is_site_package_path(path: Path) -> bool:
    """Check if a path is in site-packages."""
    return any(site_pkg in path.parents for site_pkg in site_packages)


def is_virtual_environment(path: Path) -> bool:
    """Check if a path is inside a virtual environment."""
    current = path
    while current != current.parent:
        if (current / "pyvenv.cfg").exists():
            return True
        current = current.parent
    return False


def is_stdlib_module_by_spec(module_name: str) -> bool:
    """Check if a module is stdlib by resolving its spec (slower but more accurate)."""
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            return False
        if spec.origin is None:
            return True
        if spec.origin:
            module_path = Path(spec.origin).resolve()
            return is_stdlib_path(module_path)
    except (ImportError, ValueError, AttributeError):
        pass
    return False


def resolve_module_path(module_name: str) -> Optional[Path]:
    """Resolve a module name to its file path."""
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            return None
        if spec.origin:
            return Path(spec.origin).resolve()
        if spec.submodule_search_locations:
            return Path(spec.submodule_search_locations[0]).resolve()
    except (ImportError, ValueError):
        pass
    return None


def should_skip_path(path: Path) -> bool:
    """Check if a path should be skipped during scanning."""
    for part in path.parts:
        if part in SKIP_DIRS or part.startswith("."):
            return True
        if part.endswith(".egg-info"):
            return True
    return False


def parse_file_ast(file_path: Path) -> Optional[ast.AST]:
    """Parse a Python file and return its AST."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return ast.parse(f.read(), filename=str(file_path))
    except (SyntaxError, UnicodeDecodeError, Exception):
        return None


def find_imports_in_file(file_path: Path) -> set[str]:
    """Parse a Python file and extract all top-level import names."""
    tree = parse_file_ast(file_path)
    if tree is None:
        return set()

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                imports.add(node.module.split(".")[0])
    return imports


class DependencyResolver:
    """Recursively resolves Python dependencies from a target file."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.visited: set[Path] = set()
        self.local_imports: set[Path] = set()
        self.import_path_map: dict[Path, str] = {}

    def classify_file(self, file_path: Path) -> str:
        """Classify a file as local, library, or virtual_env."""
        if is_virtual_environment(file_path):
            return "virtual_env"
        elif self.project_root in file_path.parents or file_path.parent == self.project_root:
            return "local"
        elif is_site_package_path(file_path):
            return "library"
        else:
            return "local"

    def resolve_relative_import(
        self, file_path: Path, node: ast.ImportFrom, modname: str | None = None
    ) -> Optional[Path]:
        """Resolve a relative import to its file path."""
        current_path = file_path.parent
        for _ in range(node.level - 1):
            current_path = current_path.parent

        if modname:
            resolved_path = current_path / modname.replace(".", "/")
            if resolved_path.with_suffix(".py").exists():
                return resolved_path.with_suffix(".py").resolve()
            elif (resolved_path / "__init__.py").exists():
                return (resolved_path / "__init__.py").resolve()
        else:
            init_path = file_path.parent / "__init__.py"
            if init_path.exists():
                return init_path.resolve()
        return None

    def resolve_package_init(self, path: Path) -> Path:
        """If path is a directory, return its __init__.py."""
        if path.is_dir():
            init_path = path / "__init__.py"
            if init_path.exists():
                return init_path
        return path

    def calculate_import_path(
        self, actual_path: Path, main_file: Path, modname: str | None = None, is_relative: bool = False
    ) -> str:
        """Calculate the relative import path for a file."""
        if is_relative:
            try:
                return str(actual_path.relative_to(main_file.parent))
            except ValueError:
                rel_import_path = modname.replace(".", "/") if modname else ""
                if actual_path.name == "__init__.py":
                    rel_import_path += "/__init__.py"
                elif actual_path.suffix == ".py":
                    rel_import_path += ".py"
                return rel_import_path
        else:
            rel_import_path = modname.replace(".", "/") if modname else ""
            if actual_path.name == "__init__.py":
                rel_import_path += "/__init__.py"
            elif actual_path.suffix == ".py":
                rel_import_path += ".py"
            return rel_import_path

    def process_import_node(
        self, node: ast.Import | ast.ImportFrom, file_path: Path, main_file: Path
    ):
        """Process an import AST node and recursively resolve dependencies."""
        modnames = []
        if isinstance(node, ast.Import):
            modnames = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            modnames = [node.module]

        is_relative = isinstance(node, ast.ImportFrom) and node.level and node.level > 0

        for modname in modnames:
            if not is_relative and is_stdlib_module_by_spec(modname):
                continue

            elif is_relative:
                path = self.resolve_relative_import(file_path, node, modname)
                if path:
                    actual_path = self.resolve_package_init(path)
                    rel_import_path = self.calculate_import_path(
                        actual_path, main_file, modname, is_relative=True
                    )
                    self.import_path_map[actual_path] = rel_import_path
                    self.find_imports(actual_path, main_file)

            else:
                path = resolve_module_path(modname)
                if path is not None and not is_stdlib_path(path) and not is_site_package_path(path):
                    actual_path = self.resolve_package_init(path)
                    rel_import_path = self.calculate_import_path(
                        actual_path, main_file, modname, is_relative=False
                    )
                    self.import_path_map[actual_path] = rel_import_path
                    self.find_imports(actual_path, main_file)

    def process_ast_statements(self, node: ast.AST, file_path: Path, main_file: Path):
        """Walk AST and process all import statements."""
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            self.process_import_node(node, file_path, main_file)
        for child in ast.iter_child_nodes(node):
            self.process_ast_statements(child, file_path, main_file)

    def find_imports(self, file_path: Path | str, main_file: Path | None = None):
        """Recursively find all local imports from a file."""
        file_path = Path(file_path).resolve()
        if file_path in self.visited:
            return

        if file_path.is_dir():
            init_file = file_path / "__init__.py"
            if init_file.exists():
                self.find_imports(init_file, main_file)
            return

        if not file_path.exists():
            return

        self.visited.add(file_path)

        file_classification = self.classify_file(file_path)
        if file_classification == "virtual_env":
            return
        elif file_classification == "local":
            self.local_imports.add(file_path)
        elif file_classification == "library":
            return

        node = parse_file_ast(file_path)
        if node is None:
            return

        if main_file is None:
            main_file = file_path
        self.process_ast_statements(node, file_path, main_file)
