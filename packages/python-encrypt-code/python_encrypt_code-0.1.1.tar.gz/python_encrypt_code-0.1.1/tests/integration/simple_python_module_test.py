"""Test the encryption of a simple python module and its execution."""

import os
import sys
import subprocess
from pathlib import Path


def test_encrypt_and_run_simple_module(
    simple_python_module: Path,
    tmp_dir: Path,
    password: str,
    aad: str,
) -> None:
    """Test encrypting a simple hello world module.

    Args:
        simple_python_module (Path): Path to the simple python module.
        tmp_dir (Path): Temporary directory for test files.
        password (str): The test password.
        aad (str): Additional authenticated data.
    """

    encrypted_file = tmp_dir / "encrypted.pec"

    # Encrypt the simple python module
    encrypt_args = [
        sys.executable,
        "-m",
        "python_encrypt_code",
        "encrypt",
        str(simple_python_module),
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

    # Store password and AAD in environment variables
    # for the PasswordProviderExample used by the subprocesses
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
        "hello_world.py",
    ]
    result = subprocess.run(
        args=run_args,
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )

    # Verify output
    assert "Hello, World!" in result.stdout


def test_run_with_wrong_password(
    simple_python_module: Path,
    tmp_dir: Path,
    password: str,
    aad: str,
    wrong_password: str,
) -> None:
    """Test encrypting a simple hello world module and attempting to run it with a wrong password.

    Args:
        simple_python_module (Path): Path to the simple python module.
        tmp_dir (Path): Temporary directory for test files.
    """

    encrypted_file = tmp_dir / "encrypted_wrong_password.pec"
    assert password != wrong_password, "Test setup error: passwords should differ."

    # Encrypt the folder containing the hello world module
    encrypt_args = [
        sys.executable,
        "-m",
        "python_encrypt_code",
        "encrypt",
        str(simple_python_module),
        "-o",
        str(encrypted_file),
        "-p",
        password,
        "-aad",
        aad,
    ]
    subprocess.run(encrypt_args, check=True)

    # Verify that the encrypted file was created
    assert encrypted_file.exists()

    # Store wrong password and AAD in environment variables for the subprocesses
    env = {**os.environ}
    env["PEC_PASSWORD"] = wrong_password
    env["PEC_AAD"] = aad

    # Run the encrypted module with the wrong password
    run_args = [
        sys.executable,
        "-m",
        "python_encrypt_code",
        "run-insecure",
        str(encrypted_file),
        "--script",
        "hello_world.py",
    ]
    result = subprocess.run(
        args=run_args,
        check=False,
        capture_output=True,
        text=True,
    )

    # Verify that an error message is in the output
    assert "Error" in result.stderr


def test_run_with_wrong_aad(
    simple_python_module: Path,
    tmp_dir: Path,
    password: str,
    aad: str,
    wrong_aad: str,
) -> None:
    """Test encrypting a simple hello world module and attempting to run it with wrong AAD.

    Args:
        simple_python_module (Path): Path to the simple python module.
        tmp_dir (Path): Temporary directory for test files.
    """

    encrypted_file = tmp_dir / "encrypted_wrong_aad.pec"
    assert aad != wrong_aad, "Test setup error: AADs should differ."

    # Encrypt the folder containing the hello world module
    encrypt_args = [
        sys.executable,
        "-m",
        "python_encrypt_code",
        "encrypt",
        str(simple_python_module),
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

    # Store wrong password and AAD in environment variables for the subprocesses
    env = {**os.environ}
    env["PEC_PASSWORD"] = password
    env["PEC_AAD"] = wrong_aad

    # Run the encrypted module with the wrong AAD
    run_args = [
        sys.executable,
        "-m",
        "python_encrypt_code",
        "run-insecure",
        str(encrypted_file),
        "--script",
        "hello_world.py",
    ]
    result = subprocess.run(
        args=run_args,
        check=False,
        capture_output=True,
        text=True,
    )

    # Verify that an error message is in the output
    assert "Error" in result.stderr
