"""Definiition of FileEncrypter class."""

from io import BytesIO
import os
import base64
import json
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .file_encrypter_interface import FileEncrypterInterface


class FileEncrypter(FileEncrypterInterface):
    """Class to handle file encryption and decryption."""

    _encoding: str = "utf-8"
    _salt_length: int = 16  # Length of the salt in bytes
    _nonce_length: int = 12  # Length of the nonce in bytes

    @classmethod
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

        # Check inputs
        if not isinstance(input_file_path, Path):
            raise TypeError("input_file_path must be a Path object")
        if not input_file_path.exists():
            raise FileNotFoundError(f"input_file_path {input_file_path} does not exist")
        if not input_file_path.is_file():
            raise ValueError("input_file_path must be a file")
        if not isinstance(output_file_path, Path):
            raise TypeError("output_file_path must be a Path object")
        if not isinstance(password, str):
            raise TypeError("password must be a string")
        if len(password) == 0:
            raise ValueError("password cannot be empty")
        password_bytes = base64.urlsafe_b64decode(password.encode(cls._encoding))
        if len(password_bytes) != 32:
            raise ValueError("Password must decode to 32 bytes for AES-256")
        if additional_data is not None and not isinstance(additional_data, dict):
            raise TypeError("additional_data must be a dict if provided")

        # Prepare additional authenticated data (AAD) if provided
        additional_data_bytes = None
        if additional_data is not None:
            additional_data_bytes = json.dumps(additional_data).encode(cls._encoding)

        # Generate a random Number Used Once (nonce)
        nonce = os.urandom(cls._nonce_length)

        # Initialize AESGCM with derived key
        aesgcm = AESGCM(password_bytes)

        # Read the input file
        with open(input_file_path, "rb") as file:
            original_data = file.read()

        # Encrypt the data
        encrypted_data = aesgcm.encrypt(nonce, original_data, additional_data_bytes)

        # Write the salt, nonce, and encrypted data to the output file
        with open(output_file_path, "wb") as file:
            file.write(nonce + encrypted_data)

    @classmethod
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

        # Check inputs
        if not isinstance(input_file_path, Path):
            raise TypeError("input_file_path must be a Path object")
        if not input_file_path.exists():
            raise FileNotFoundError(f"input_file_path {input_file_path} does not exist")
        if not input_file_path.is_file():
            raise ValueError("input_file_path must be a file")
        if not isinstance(password, str):
            raise TypeError("password must be a string")
        if len(password) == 0:
            raise ValueError("password cannot be empty")
        password_bytes = base64.urlsafe_b64decode(password.encode(cls._encoding))
        if len(password_bytes) != 32:
            raise ValueError("Password must decode to 32 bytes for AES-256")
        if additional_data is not None and not isinstance(additional_data, dict):
            raise TypeError("additional_data must be a dict if provided")

        # Prepare additional authenticated data (AAD) if provided
        additional_data_bytes = None
        if additional_data is not None:
            additional_data_bytes = json.dumps(additional_data).encode(cls._encoding)

        # Initialize AESGCM with derived key
        aesgcm = AESGCM(password_bytes)

        # Read the input file
        with open(input_file_path, "rb") as file:
            file_data = file.read()

        # Split the nonce and encrypted data
        nonce = file_data[: cls._nonce_length]
        encrypted_data = file_data[cls._nonce_length :]

        # Decrypt the data
        decrypted_data = aesgcm.decrypt(nonce, encrypted_data, additional_data_bytes)

        # # Extract the salt and encrypted data
        # salt = file_data[:16]
        # encrypted_data = file_data[16:]

        # # Derive the key from the password using PBKDF2
        # kdf = PBKDF2HMAC(
        #     algorithm=hashes.SHA256(),
        #     length=32,
        #     salt=salt,
        #     iterations=480000,  # OWASP recommended minimum for 2023+
        # )
        # key = base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))
        # fernet = Fernet(key)

        # # Decrypt the data
        # decrypted_data = fernet.decrypt(encrypted_data)

        return BytesIO(decrypted_data)

    @classmethod
    def decrypt_to_disk(
        cls,
        input_file_path: Path,
        output_file_path: Path,
        password: str,
        additional_data: dict[str, str] | None = None,
    ) -> None:
        """Decrypt a file using the provided password and save to disk.

        Args:
            input_file_path (str): The path to the input file to be decrypted.
            output_file_path (str): The path where the decrypted file will be saved.
            password (str): The password used for decryption.
            additional_data (dict[str, str] | None): Optional additional authenticated data (AAD).
        """

        decrypted_data_io = FileEncrypter.decrypt_file(
            input_file_path, password, additional_data
        )

        # Write the decrypted data to the output file
        with open(output_file_path, "wb") as file:
            file.write(decrypted_data_io.getbuffer())
