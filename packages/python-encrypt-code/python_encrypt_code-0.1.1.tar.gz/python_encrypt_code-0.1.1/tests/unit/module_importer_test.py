"""Unit tests for module importer functionality."""

import sys
from pathlib import Path
import pytest

from python_encrypt_code.module_importer import ModuleImporter


def test_module_importer_comprehensive_functionality(
    nested_python_module: Path,
) -> None:
    """Test comprehensive module importer functionality including packages, modules, imports, and main execution."""

    # Store original modules state
    original_modules = sys.modules.copy()

    try:
        # Test regular loading first
        ModuleImporter.import_module_from_disk(nested_python_module)

        # Verify packages were created
        assert "src" in sys.modules  # src package from __init__.py
        assert hasattr(sys.modules["src"], "__path__"), (
            "src should be a package with __path__"
        )

        # Verify individual modules were created
        assert "src.func_one" in sys.modules
        assert "src.func_two" in sys.modules
        assert "main" in sys.modules

        # Verify module attributes are set correctly
        func_one_module = sys.modules["src.func_one"]
        assert func_one_module.__file__ is not None
        assert func_one_module.__file__.endswith("func_one.py")
        assert func_one_module.__package__ == "src"

        main_module = sys.modules["main"]
        assert main_module.__file__ is not None
        assert main_module.__file__.endswith("main.py")
        assert main_module.__package__ is None

        # Test that functions are accessible (assuming func_one has a function)
        if hasattr(func_one_module, "func_one"):
            assert callable(func_one_module.func_one)

        # Clean up for next test
        modules_to_remove = [
            name for name in sys.modules.keys() if name not in original_modules
        ]
        for module_name in modules_to_remove:
            del sys.modules[module_name]

        # Test main module functionality
        ModuleImporter.import_module_from_disk(
            nested_python_module, main_module="main.py"
        )

        # Verify main module has correct __name__
        assert "__main__" in sys.modules
        assert sys.modules["__main__"].__name__ == "__main__"

        # Verify all expected modules are still loaded
        assert "src" in sys.modules
        assert "src.func_one" in sys.modules
        assert "src.func_two" in sys.modules
        assert "main" in sys.modules

        # Verify src is still a package
        src_module = sys.modules["src"]
        assert hasattr(src_module, "__path__")

    finally:
        # Clean up
        modules_to_remove = [
            name for name in sys.modules.keys() if name not in original_modules
        ]
        for module_name in modules_to_remove:
            del sys.modules[module_name]


def test_module_importer_handles_edge_cases(
    tmp_path: Path,
) -> None:
    """Test module importer handling of edge cases like empty files."""

    # Create actual files on disk
    module_dir = tmp_path / "test_module"
    module_dir.mkdir()

    pkg_dir = module_dir / "pkg"
    pkg_dir.mkdir()

    # Create empty files
    (module_dir / "empty_module.py").write_text("")
    (pkg_dir / "__init__.py").write_text("# Package init")

    # Also test cross-module imports
    src_dir = module_dir / "src"
    src_dir.mkdir()
    (src_dir / "math_utils.py").write_text("def square(x): return x * x")
    (src_dir / "geometry.py").write_text(
        "from src.math_utils import square\ndef area_square(side): return square(side)"
    )

    # Store original modules state
    original_modules = sys.modules.copy()

    try:
        ModuleImporter.import_module_from_disk(module_dir)

        # Verify empty modules were created successfully
        assert "empty_module" in sys.modules
        assert "pkg.__init__" in sys.modules

        # Verify cross-module functionality works
        geometry_module = sys.modules["src.geometry"]
        assert hasattr(geometry_module, "area_square")
        assert geometry_module.area_square(5) == 25

    finally:
        # Clean up
        modules_to_remove = [
            name for name in sys.modules.keys() if name not in original_modules
        ]
        for module_name in modules_to_remove:
            del sys.modules[module_name]


def test_module_importer_input_validation(
    tmp_path: Path,
) -> None:
    """Test input validation for import_module_from_disk."""

    # Test invalid module_path type
    with pytest.raises(TypeError, match="module_path must be a Path object"):
        ModuleImporter.import_module_from_disk("not_a_path")  # type: ignore

    # Test non-existent path
    non_existent = tmp_path / "does_not_exist"
    with pytest.raises(FileNotFoundError, match="does not exist"):
        ModuleImporter.import_module_from_disk(non_existent)

    # Test path that is not a directory
    file_path = tmp_path / "file.txt"
    file_path.write_text("not a directory")
    with pytest.raises(ValueError, match="module_path must be a directory"):
        ModuleImporter.import_module_from_disk(file_path)

    # Test directory with no Python files
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    with pytest.raises(ValueError, match="No Python files found"):
        ModuleImporter.import_module_from_disk(empty_dir)
