"""Definition of DataZipper class."""

from io import BytesIO
import os
import zipfile
from pathlib import Path

from .data_zipper_interface import DataZipperInterface


class DataZipper(DataZipperInterface):
    """Class to handle zipping of data folders."""

    @staticmethod
    def zip_data(
        input_path: Path,
        output_path: Path,
    ) -> None:
        """Zips the contents of a folder into a zip file.

        Args:
            folder_path (Path): The path to the folder to be zipped.
            output_path (Path): The path where the zip file will be saved.
        """

        # Check inputs
        if not isinstance(input_path, Path):
            raise TypeError("input_path must be a Path object")
        if not input_path.exists():
            raise FileNotFoundError(f"input_path {input_path} does not exist")
        if not input_path.is_dir():
            raise ValueError("input_path must be a directory")
        if not isinstance(output_path, Path):
            raise TypeError("output_path must be a Path object")

        # Zip the folder
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(input_path):
                for file in files:
                    file_path = Path(root) / file
                    zipf.write(file_path, arcname=file_path.relative_to(input_path))

    @staticmethod
    def unzip_data(
        input_data: BytesIO,
    ) -> dict[str, BytesIO]:
        """Unzips the data of a zip file into memory.

        Args:
            input_data (BytesIO): The data of the zip file to be unzipped.

        Returns:
            Dict[str, BytesIO]: Dictionary mapping file names to BytesIO objects.
        """

        # Check inputs
        if not isinstance(input_data, BytesIO):
            raise TypeError("input_data must be a BytesIO object")

        if input_data.getbuffer().nbytes == 0:
            raise ValueError("input_data must not be empty")

        # Unzip the file into memory
        extracted_files = {}
        with zipfile.ZipFile(input_data, "r") as zipf:
            for file_info in zipf.filelist:
                if not file_info.is_dir():  # Skip directories
                    file_content = zipf.read(file_info.filename)
                    extracted_files[file_info.filename] = BytesIO(file_content)

        return extracted_files

    @staticmethod
    def unzip_data_to_disk(
        input_data: BytesIO,
        output_path: Path,
    ) -> None:
        """Unzips the data of a zip file to disk.

        Args:
            input_data (BytesIO): The data of the zip file to be unzipped.
            output_path (Path): The path where the unzipped files will be saved.
        """

        # Check inputs
        if not isinstance(input_data, BytesIO):
            raise TypeError("input_data must be a BytesIO object")

        if not isinstance(output_path, Path):
            raise TypeError("output_path must be a Path object")

        if input_data.getbuffer().nbytes == 0:
            raise ValueError("input_data must not be empty")

        # Unzip the file to disk
        with zipfile.ZipFile(input_data, "r") as zipf:
            zipf.extractall(output_path)
