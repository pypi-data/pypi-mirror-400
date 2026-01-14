"""Definition of decrypt_file_to_disk function."""

import tempfile
from pathlib import Path

from python_encrypt_code import (
    DataZipper,
    FileEncrypter,
    PasswordProvider,
)


def decrypt_to_disk(
    encrypted_file_path: Path,
    output_path: Path,
) -> None:
    """Decrypt a file and save the contents to disk.

    Args:
        encrypted_file_path: Path to the encrypted file
        output_path: Path where the decrypted folder will be saved
    """

    # Validate inputs
    if not encrypted_file_path.exists():
        raise FileNotFoundError(f"Encrypted file not found: {encrypted_file_path}")

    if not encrypted_file_path.is_file():
        raise ValueError(f"Path is not a file: {encrypted_file_path}")

    # Get decryption keys
    password, additional_data = PasswordProvider.get_decryption_keys()

    # Create temporary zip file
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
        temp_zip_path = Path(temp_zip.name)

    try:
        # Step 1: Decrypt the file
        print(f"Decrypting: {encrypted_file_path}")
        decrypted_data = FileEncrypter.decrypt_file(
            input_file_path=encrypted_file_path,
            password=password,
            additional_data=additional_data,
        )

        # Step 2: Extract the zip file to disk
        print(f"Extracting to: {output_path}")
        DataZipper.unzip_data_to_disk(decrypted_data, output_path)

        print("✅ File decrypted and extracted successfully!")

    finally:
        # Clean up temporary zip file
        if temp_zip_path.exists():
            temp_zip_path.unlink()
