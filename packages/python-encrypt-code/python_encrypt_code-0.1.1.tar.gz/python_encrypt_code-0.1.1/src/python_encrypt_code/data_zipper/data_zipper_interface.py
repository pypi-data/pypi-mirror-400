"""Definition of DataZipperInterface."""

from io import BytesIO
from abc import ABC, abstractmethod
from pathlib import Path


class DataZipperInterface(ABC):
    """Interface for data zipper implementations."""

    @staticmethod
    @abstractmethod
    def zip_data(
        input_path: Path,
        output_path: Path,
    ) -> None:
        """Zips data from the input path and saves it to the output path.

        Args:
            input_path (Path): The path to the data to be zipped.
            output_path (Path): The path where the zipped data will be saved.
        """

    @staticmethod
    @abstractmethod
    def unzip_data(
        input_data: BytesIO,
    ) -> dict[str, BytesIO]:
        """Unzips data from the input path and saves it in memory.

        Args:
            input_data (BytesIO): The data of the zipped file.
        Returns:
            Dict[str, BytesIO]: A dictionary mapping file names to BytesIO objects.
        """

    @staticmethod
    @abstractmethod
    def unzip_data_to_disk(
        input_data: BytesIO,
        output_path: Path,
    ) -> None:
        """Unzips data from the input path and saves it to the output path on disk.

        Args:
            input_data (BytesIO): The data of the zipped file.
            output_path (Path): The path where the unzipped data will be saved.
        """
