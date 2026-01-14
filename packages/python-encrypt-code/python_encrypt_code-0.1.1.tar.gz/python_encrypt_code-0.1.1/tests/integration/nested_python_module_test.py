"""Test the encryption of complex python modules with multiple files and imports."""

import os
import sys
import subprocess
from pathlib import Path


def test_encrypt_and_run_nested_module(
    nested_python_module: Path,
    tmp_dir: Path,
    password: str,
    aad: str,
) -> None:
    """Test encrypting and running a module with nested imports.

    Args:
        nested_python_module (Path): Path to the nested module directory.
        tmp_dir (Path): Temporary directory for test files.
        password (str): The test password.
        aad (str): Additional authenticated data.
    """

    encrypted_file = tmp_dir / "encrypted_nested.pec"

    # Encrypt the folder containing the complex module
    encrypt_args = [
        sys.executable,
        "-m",
        "python_encrypt_code",
        "encrypt",
        str(nested_python_module),
        "-o",
        str(encrypted_file),
        "-p",
        password,
        "-aad",
        aad,
    ]
    subprocess.run(
        args=encrypt_args,
        check=True,
    )

    # Verify that the encrypted file was created
    assert encrypted_file.exists()

    # Prepare environment for the PasswordProviderExample
    env = {**os.environ}
    env["PEC_PASSWORD"] = password
    env["PEC_AAD"] = aad

    # Run the encrypted module with environment set
    run_args = [
        sys.executable,
        "-m",
        "python_encrypt_code",
        "run-insecure",
        str(encrypted_file),
        "--script",
        "main.py",
    ]
    result = subprocess.run(
        args=run_args,
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )

    # Verify nested module functionality works
    assert "Nested Python Module executed successfully." in result.stderr
