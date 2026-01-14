"""Definition of ModuleImporterInterface."""

from io import BytesIO
from abc import ABC, abstractmethod
from pathlib import Path


class ModuleImporterInterface(ABC):
    """Interface for module importer implementations."""

    @classmethod
    @abstractmethod
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

    @classmethod
    @abstractmethod
    def import_module_from_disk(
        cls,
        module_path: Path,
        main_module: str | None = None,
    ) -> None:
        """Imports a Python module from a file on disk.

        Args:
            module_path (Path): The file path of the module on disk.
            main_module (str | None): The name of the main module to execute, if any.
        """
