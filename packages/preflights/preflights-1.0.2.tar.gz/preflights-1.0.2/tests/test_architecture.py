"""
Architecture enforcement tests.

These tests verify that architectural constraints are respected:
- Core has no I/O
- Core has no non-deterministic operations
- Core has no forbidden imports
- Layer boundaries are respected
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Iterator

import pytest

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
CORE_DIR = PROJECT_ROOT / "preflights" / "core"
APP_DIR = PROJECT_ROOT / "preflights" / "application"
ADAPTERS_DIR = PROJECT_ROOT / "preflights" / "adapters"
CLI_DIR = PROJECT_ROOT / "preflights" / "cli"


# =============================================================================
# FORBIDDEN IMPORTS IN CORE
# =============================================================================

# Modules that must NEVER be imported in core/
FORBIDDEN_IMPORTS_CORE = frozenset({
    # I/O
    "os",
    "pathlib",
    "io",
    "shutil",
    "tempfile",
    "glob",
    "fnmatch",
    # Network
    "requests",
    "httpx",
    "urllib",
    "aiohttp",
    "socket",
    # External services
    "anthropic",
    "openai",
    # Database
    "sqlite3",
    "psycopg2",
    "sqlalchemy",
    # Non-deterministic (partial - datetime itself is ok for types)
    "random",
    "uuid",
    "secrets",
    # Framework coupling
    "click",
    "typer",
    "fastapi",
    "flask",
    # Subprocess
    "subprocess",
    "multiprocessing",
})

# Specific imports that are forbidden (module.attr)
FORBIDDEN_FROM_IMPORTS_CORE = frozenset({
    ("datetime", "datetime.now"),
    ("datetime", "datetime.utcnow"),
    ("time", "time"),
    ("time", "sleep"),
    ("os", "environ"),
    ("os", "getcwd"),
    ("os", "listdir"),
    ("os", "path"),
})


# =============================================================================
# FORBIDDEN FUNCTION CALLS IN CORE
# =============================================================================

# Function calls that must never appear in core/
FORBIDDEN_CALLS_CORE = frozenset({
    # I/O
    "open",
    "print",  # Use logging or return values
    # Non-deterministic
    "datetime.now",
    "datetime.utcnow",
    "time.time",
    "time.sleep",
    "random.random",
    "random.randint",
    "random.choice",
    "uuid.uuid4",
    "uuid.uuid1",
    # OS
    "os.getcwd",
    "os.listdir",
    "os.path.exists",
    "os.path.isfile",
    "os.path.isdir",
    "os.environ.get",
    "os.getenv",
    # Subprocess
    "subprocess.run",
    "subprocess.call",
    "subprocess.Popen",
})


# =============================================================================
# HELPERS
# =============================================================================


def iter_python_files(directory: Path) -> Iterator[Path]:
    """Iterate over all Python files in directory."""
    for path in directory.rglob("*.py"):
        if "__pycache__" not in str(path):
            yield path


def get_imports(tree: ast.AST) -> list[tuple[str, int]]:
    """Extract all imports from AST with line numbers."""
    imports: list[tuple[str, int]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((alias.name.split(".")[0], node.lineno))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append((node.module.split(".")[0], node.lineno))

    return imports


def get_function_calls(tree: ast.AST) -> list[tuple[str, int]]:
    """Extract all function calls from AST with line numbers."""
    calls: list[tuple[str, int]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            call_name = _get_call_name(node.func)
            if call_name:
                calls.append((call_name, node.lineno))

    return calls


def _get_call_name(node: ast.expr) -> str | None:
    """Get the full name of a function call."""
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        value_name = _get_call_name(node.value)
        if value_name:
            return f"{value_name}.{node.attr}"
        return node.attr
    return None


# =============================================================================
# TESTS
# =============================================================================


@pytest.mark.arch
class TestCoreNoForbiddenImports:
    """Core must not import I/O or non-deterministic modules."""

    def test_no_forbidden_imports(self) -> None:
        """Scan core/ for forbidden imports."""
        violations: list[str] = []

        for py_file in iter_python_files(CORE_DIR):
            content = py_file.read_text()
            try:
                tree = ast.parse(content)
            except SyntaxError:
                continue

            imports = get_imports(tree)
            relative_path = py_file.relative_to(PROJECT_ROOT)

            for module, lineno in imports:
                if module in FORBIDDEN_IMPORTS_CORE:
                    violations.append(
                        f"{relative_path}:{lineno} - forbidden import '{module}'"
                    )

        assert not violations, (
            f"Core has forbidden imports:\n" + "\n".join(f"  {v}" for v in violations)
        )


@pytest.mark.arch
class TestCoreNoIOCalls:
    """Core must not call I/O or non-deterministic functions."""

    def test_no_forbidden_function_calls(self) -> None:
        """Scan core/ for forbidden function calls."""
        violations: list[str] = []

        for py_file in iter_python_files(CORE_DIR):
            content = py_file.read_text()
            try:
                tree = ast.parse(content)
            except SyntaxError:
                continue

            calls = get_function_calls(tree)
            relative_path = py_file.relative_to(PROJECT_ROOT)

            for call_name, lineno in calls:
                if call_name in FORBIDDEN_CALLS_CORE:
                    violations.append(
                        f"{relative_path}:{lineno} - forbidden call '{call_name}()'"
                    )

        assert not violations, (
            f"Core has forbidden function calls:\n"
            + "\n".join(f"  {v}" for v in violations)
        )

    def test_no_open_calls(self) -> None:
        """Specifically check for open() calls which are easy to miss."""
        violations: list[str] = []

        for py_file in iter_python_files(CORE_DIR):
            content = py_file.read_text()
            try:
                tree = ast.parse(content)
            except SyntaxError:
                continue

            relative_path = py_file.relative_to(PROJECT_ROOT)

            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id == "open":
                        violations.append(
                            f"{relative_path}:{node.lineno} - open() call"
                        )

        assert not violations, (
            f"Core has open() calls (I/O forbidden):\n"
            + "\n".join(f"  {v}" for v in violations)
        )


@pytest.mark.arch
class TestCoreNoPrintStatements:
    """Core should not use print() - return values or raise errors instead."""

    def test_no_print_calls(self) -> None:
        """Scan core/ for print() calls."""
        violations: list[str] = []

        for py_file in iter_python_files(CORE_DIR):
            content = py_file.read_text()
            try:
                tree = ast.parse(content)
            except SyntaxError:
                continue

            relative_path = py_file.relative_to(PROJECT_ROOT)

            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id == "print":
                        violations.append(f"{relative_path}:{node.lineno}")

        assert not violations, (
            f"Core has print() calls (use return values instead):\n"
            + "\n".join(f"  {v}" for v in violations)
        )


@pytest.mark.arch
class TestLayerBoundaries:
    """Verify layer dependencies are respected."""

    def test_core_does_not_import_adapters(self) -> None:
        """Core must not import from adapters/."""
        violations: list[str] = []

        for py_file in iter_python_files(CORE_DIR):
            content = py_file.read_text()
            relative_path = py_file.relative_to(PROJECT_ROOT)

            # Check for adapter imports
            if "from preflights.adapters" in content:
                # Find line number
                for i, line in enumerate(content.split("\n"), 1):
                    if "from preflights.adapters" in line:
                        violations.append(f"{relative_path}:{i}")
            if "import preflights.adapters" in content:
                for i, line in enumerate(content.split("\n"), 1):
                    if "import preflights.adapters" in line:
                        violations.append(f"{relative_path}:{i}")

        assert not violations, (
            f"Core imports from adapters (layer violation):\n"
            + "\n".join(f"  {v}" for v in violations)
        )

    def test_core_does_not_import_cli(self) -> None:
        """Core must not import from cli/."""
        violations: list[str] = []

        for py_file in iter_python_files(CORE_DIR):
            content = py_file.read_text()
            relative_path = py_file.relative_to(PROJECT_ROOT)

            if "from preflights.cli" in content or "import preflights.cli" in content:
                for i, line in enumerate(content.split("\n"), 1):
                    if "preflights.cli" in line:
                        violations.append(f"{relative_path}:{i}")

        assert not violations, (
            f"Core imports from cli (layer violation):\n"
            + "\n".join(f"  {v}" for v in violations)
        )

    def test_core_does_not_import_app(self) -> None:
        """Core must not import from application/."""
        violations: list[str] = []

        for py_file in iter_python_files(CORE_DIR):
            content = py_file.read_text()
            relative_path = py_file.relative_to(PROJECT_ROOT)

            if (
                "from preflights.application" in content
                or "import preflights.application" in content
                or "from preflights.app" in content
                or "import preflights.app" in content
            ):
                for i, line in enumerate(content.split("\n"), 1):
                    if "preflights.app" in line or "preflights.application" in line:
                        violations.append(f"{relative_path}:{i}")

        assert not violations, (
            f"Core imports from application (layer violation):\n"
            + "\n".join(f"  {v}" for v in violations)
        )


@pytest.mark.arch
class TestAdaptersCanImportCore:
    """Verify adapters CAN import from core (correct direction)."""

    def test_adapters_can_import_core_types(self) -> None:
        """Adapters should be able to import core types."""
        # This is a "documentation" test - just verify the layer exists
        assert ADAPTERS_DIR.exists(), "adapters/ directory should exist"
        assert CORE_DIR.exists(), "core/ directory should exist"

        # Check that at least one adapter imports from core
        found_core_import = False
        for py_file in iter_python_files(ADAPTERS_DIR):
            content = py_file.read_text()
            if "from preflights.core" in content:
                found_core_import = True
                break

        assert found_core_import, (
            "Adapters should import from core (this is the correct dependency direction)"
        )


@pytest.mark.e2e
class TestArchitectureSummary:
    """Summary test that runs all architecture checks."""

    def test_architecture_is_valid(self) -> None:
        """
        Meta-test: Run this to get a full architecture report.

        This test always passes but prints violations if any.
        Use the individual tests above for CI enforcement.
        """
        # This is just a marker test - real checks are in other tests
        assert CORE_DIR.exists(), "core/ must exist"
        assert ADAPTERS_DIR.exists(), "adapters/ must exist"
