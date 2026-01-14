"""Definition of ModuleImporter class."""

from io import BytesIO
import importlib.util
from pathlib import Path
import sys

from .module_importer_interface import ModuleImporterInterface


class ModuleImporter(ModuleImporterInterface):
    """Class to handle importing Python modules from various sources."""

    @classmethod
    def import_module(
        cls,
        module_data: dict[str, BytesIO],
        main_module: str | None = None,
    ) -> None:
        """Imports a Python module from in-memory data.

        Args:
            module_data (dict[str, BytesIO]): A dictionary mapping module names to their bytecode streams.
            main_module (str | None): The name of the main module to execute, if any.
        """
        raise NotImplementedError("import_module is not implemented yet.")

    @classmethod
    def import_module_from_disk(
        cls,
        module_path: Path,
        main_module: str | None = None,
    ) -> None:
        """Imports a Python module or package from a directory on disk.

        Args:
            module_path (Path): The directory path containing Python modules to import.
            main_module (str | None): The filename (e.g., 'main.py') to treat as the main module.
                                     If specified, this module will have __name__ set to '__main__'.
        """

        # Check inputs
        if not isinstance(module_path, Path):
            raise TypeError("module_path must be a Path object")
        if not module_path.exists():
            raise FileNotFoundError(f"module_path {module_path} does not exist")
        if not module_path.is_dir():
            raise ValueError("module_path must be a directory")

        # Find all Python files in the directory and subdirectories
        python_files = list(module_path.rglob("*.py"))
        if not python_files:
            raise ValueError(f"No Python files found in {module_path}")

        # Add the module directory to sys.path so imports work
        module_path_str = str(module_path)
        path_added = False
        if module_path_str not in sys.path:
            sys.path.insert(0, module_path_str)
            path_added = True

        try:
            # Import all Python files as modules (dependencies first, main module last)
            main_module_file = None
            init_files = []

            # First pass: Load all non-main, non-__init__ modules (dependencies)
            for py_file in python_files:
                relative_path = py_file.relative_to(module_path)

                # Check if this file is the main module
                is_main_module = main_module and relative_path.name == main_module
                # Check if this is an __init__.py file
                is_init_file = relative_path.name == "__init__.py"

                if is_main_module:
                    # Store the main module file for later execution
                    main_module_file = py_file
                    continue
                elif is_init_file:
                    # Store __init__.py files for later execution
                    init_files.append(py_file)
                    continue

                # Load regular dependency modules first
                cls._load_module(py_file, module_path, is_main=False)

            # Second pass: Load __init__.py files (after their contents are available)
            for init_file in init_files:
                cls._load_module(init_file, module_path, is_main=False)

            # Third pass: Load and execute the main module last (if specified)
            if main_module_file:
                cls._load_module(main_module_file, module_path, is_main=True)

        finally:
            # Clean up sys.path
            if path_added and module_path_str in sys.path:
                sys.path.remove(module_path_str)

    @staticmethod
    def _load_module(py_file: Path, module_path: Path, is_main: bool = False) -> None:
        """Load a single Python module.

        Args:
            py_file (Path): Path to the Python file to load
            module_path (Path): Base path for the module directory
            is_main (bool): Whether this is the main module
        """
        relative_path = py_file.relative_to(module_path)

        # Create module name from relative path
        if len(relative_path.parts) > 1:
            # Nested module: subdir/module.py -> subdir.module
            parts = list(relative_path.parts[:-1]) + [relative_path.stem]
            module_name = ".".join(parts)
        else:
            # Top-level module
            module_name = relative_path.stem

        # Use "__main__" as the spec name for main modules
        spec_name = "__main__" if is_main else module_name

        # Import the module from the file
        spec = importlib.util.spec_from_file_location(spec_name, py_file)
        if spec is None:
            raise ImportError(f"Could not create spec for module {module_name}")
        module = importlib.util.module_from_spec(spec)

        # Set module attributes
        module.__file__ = str(py_file)
        module.__package__ = (
            ".".join(relative_path.parts[:-1]) if len(relative_path.parts) > 1 else None
        )

        # Execute the module
        if spec.loader is None:
            raise ImportError(f"No loader found for module {module_name}")
        spec.loader.exec_module(module)

        # Add to sys.modules
        if is_main:
            sys.modules["__main__"] = module
        sys.modules[module_name] = module  # Also keep regular name for imports
