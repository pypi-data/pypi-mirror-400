"""Definition of integration tests for the CLI functionality."""

import subprocess
import os
import sys
from pathlib import Path


def test_generate_password_command() -> None:
    """Test the generate-password CLI command."""
    generate_password_args = [
        sys.executable,
        "-m",
        "python_encrypt_code",
        "generate-password",
    ]
    output = subprocess.run(
        generate_password_args, check=True, capture_output=True, text=True
    )
    password = output.stdout.strip()
    assert len(password) > 0, "Generated password should not be empty"


def test_encrypt_command(
    password: str,
    aad: str,
    simple_python_module: Path,
    tmp_dir: Path,
) -> None:
    """Test the encrypt CLI command."""

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
    subprocess.run(encrypt_args, check=True)

    assert encrypted_file.exists(), "Encrypted file should be created"

    # Encrypt without optional AAD
    encrypted_file_no_aad = tmp_dir / "encrypted_no_aad.pec"
    encrypt_args_no_aad = [
        sys.executable,
        "-m",
        "python_encrypt_code",
        "encrypt",
        str(simple_python_module),
        "-o",
        str(encrypted_file_no_aad),
        "-p",
        password,
    ]
    subprocess.run(encrypt_args_no_aad, check=True)

    assert encrypted_file_no_aad.exists(), "Encrypted file should be created"


def test_decrypt_command(
    password: str,
    aad: str,
    simple_python_module: Path,
    tmp_dir: Path,
) -> None:
    """Test the decrypt CLI command."""

    encrypted_file = tmp_dir / "encrypted.pec"
    decrypted_output_dir = tmp_dir / "decrypted_output"

    # Prepare an encrypted file
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

    # The PasswordProviderExample reads from environment variables
    # to mock getting data from external secret management systems.
    env = {**os.environ}
    env["PEC_PASSWORD"] = password
    env["PEC_AAD"] = aad

    # Decrypt the file
    decrypt_args = [
        sys.executable,
        "-m",
        "python_encrypt_code",
        "decrypt",
        str(encrypted_file),
        "-o",
        str(decrypted_output_dir),
    ]
    subprocess.run(decrypt_args, check=True, env=env)

    assert decrypted_output_dir.exists(), "Decrypted output directory should be created"
    assert any(decrypted_output_dir.iterdir()), (
        "Decrypted output directory should not be empty"
    )


def test_run_insecure_command(
    password: str,
    aad: str,
    simple_python_module: Path,
    tmp_dir: Path,
) -> None:
    """Test the run-insecure CLI command."""

    encrypted_file = tmp_dir / "encrypted_run.pec"

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

    # Store password and AAD in environment variables for the subprocesses
    env = dict(**os.environ)
    env["PEC_PASSWORD"] = password
    env["PEC_AAD"] = aad

    # Step 2: Run the encrypted module
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
