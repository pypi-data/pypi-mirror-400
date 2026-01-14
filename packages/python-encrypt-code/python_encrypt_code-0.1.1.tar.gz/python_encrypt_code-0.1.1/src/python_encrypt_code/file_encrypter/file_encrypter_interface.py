"""Definition of FileEncrypterInterface."""

from io import BytesIO
from abc import ABC, abstractmethod
from pathlib import Path


class FileEncrypterInterface(ABC):
    """Interface for file encrypters."""

    @classmethod
    @abstractmethod
    def encrypt_file(
        cls,
        input_file_path: Path,
        output_file_path: Path,
        password: str,
        additional_data: dict[str, str] | None = None,
    ) -> None:
        """Encrypt a file using the provided password.

        Args:
            input_file_path (str): The path to the input file to be encrypted.
            output_file_path (str): The path where the encrypted file will be saved.
            password (str): The password used for encryption.
            additional_data (dict[str, str] | None): Optional additional authenticated data (AAD).
        """

    @classmethod
    @abstractmethod
    def decrypt_file(
        cls,
        input_file_path: Path,
        password: str,
        additional_data: dict[str, str] | None = None,
    ) -> BytesIO:
        """Decrypt a file using the provided password.

        Args:
            input_file_path (str): The path to the input file to be decrypted.
            password (str): The password used for decryption.
            additional_data (dict[str, str] | None): Optional additional authenticated data (AAD).

        Returns:
            BytesIO: The decrypted file data in memory.
        """

    @classmethod
    @abstractmethod
    def decrypt_to_disk(
        cls,
        input_file_path: Path,
        output_file_path: Path,
        password: str,
        additional_data: dict[str, str] | None = None,
    ) -> None:
        """Decrypt a file and save it to disk.

        Args:
            input_file_path (str): The path to the input file to be decrypted.
            output_file_path (str): The path where the decrypted file will be saved.
            password (str): The password used for decryption.
            additional_data (dict[str, str] | None): Optional additional authenticated data (AAD).
        """
