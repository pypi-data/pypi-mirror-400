"""Definition of encrypt_folder function."""

import tempfile
import json
from pathlib import Path

from python_encrypt_code import (
    DataZipper,
    FileEncrypter,
)


def encrypt_folder(
    folder_path: Path,
    output_path: Path,
    password: str,
    aad: str | None = None,
) -> None:
    """Encrypt a folder.

    Args:
        folder_path (Path): Path to the folder to encrypt
        output_path (Path): Path where the encrypted file will be saved
        password (str): Optional password to use. If None, generates a new one.
        aad (str | None): Optional JSON-formatted metadata that will be stored in with the encrypted file.
    """

    # Validate inputs
    if not isinstance(folder_path, Path):
        raise TypeError(f"folder_path must be a Path object: {folder_path}")
    if not folder_path.exists():
        raise FileNotFoundError(f"Folder not found: {folder_path}")
    if not folder_path.is_dir():
        raise ValueError(f"Path is not a directory: {folder_path}")
    if not isinstance(output_path, Path):
        raise TypeError(f"output_path must be a Path object: {output_path}")
    if not output_path.parent.exists():
        raise FileNotFoundError(
            f"Output directory does not exist: {output_path.parent}"
        )
    if not isinstance(password, str):
        raise TypeError("password must be a string")
    if len(password) == 0:
        raise ValueError("password cannot be an empty string")
    if aad is not None and not isinstance(aad, str):
        raise TypeError("aad must be a string or None")

    # Convert additional_data to if provided
    if isinstance(aad, str):
        additional_data = dict(json.loads(aad))
    else:
        additional_data = None

    # Create temporary zip file
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
        temp_zip_path = Path(temp_zip.name)

    try:
        # Step 1: Zip the folder
        print(f"Zipping folder: {folder_path}")
        DataZipper.zip_data(folder_path, temp_zip_path)

        # Step 2: Encrypt the zip file
        print(f"Encrypting to: {output_path}")
        FileEncrypter.encrypt_file(
            input_file_path=temp_zip_path,
            output_file_path=output_path,
            password=password,
            additional_data=additional_data,
        )

        print("✅ Folder encrypted successfully!")

    finally:
        # Clean up temporary zip file
        if temp_zip_path.exists():
            temp_zip_path.unlink()
