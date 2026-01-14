"""Unit tests for file_encrypter module."""

from pathlib import Path
from io import BytesIO
import pytest

from python_encrypt_code.file_encrypter import FileEncrypter


def test_encrypt_file_checks_inputs(
    sample_file: Path,
    password: str,
) -> None:
    """Test that FileEncrypter raises errors for invalid inputs."""

    temp_dir = sample_file.parent
    output_file = temp_dir / "encrypted.bin"

    # Test that TypeError is raised for non-Path input_file_path
    with pytest.raises(TypeError):
        FileEncrypter.encrypt_file(
            input_file_path="not_a_path",  # type: ignore
            output_file_path=output_file,
            password=password,
        )

    # Test that FileNotFoundError is raised for non-existent input_file_path
    with pytest.raises(FileNotFoundError):
        FileEncrypter.encrypt_file(
            input_file_path=temp_dir / "non_existent_file.txt",
            output_file_path=output_file,
            password=password,
        )

    # Test that ValueError is raised for non-file input_file_path (directory)
    with pytest.raises(ValueError):
        FileEncrypter.encrypt_file(
            input_file_path=temp_dir,
            output_file_path=output_file,
            password=password,
        )

    # Test that TypeError is raised for non-Path output_file_path
    with pytest.raises(TypeError):
        FileEncrypter.encrypt_file(
            input_file_path=sample_file,
            output_file_path="not_a_path",  # type: ignore
            password=password,
        )

    # Test that TypeError is raised for non-string password
    with pytest.raises(TypeError):
        FileEncrypter.encrypt_file(
            input_file_path=sample_file,
            output_file_path=output_file,
            password=123,  # type: ignore
        )

    # Test that ValueError is raised for empty password
    with pytest.raises(ValueError):
        FileEncrypter.encrypt_file(
            input_file_path=sample_file,
            output_file_path=output_file,
            password="",
        )

    # Test that ValueError is raised for password that does not decode to 32 bytes
    with pytest.raises(ValueError):
        FileEncrypter.encrypt_file(
            input_file_path=sample_file,
            output_file_path=output_file,
            password="short_password",
        )

    # Test that TypeError is raised for non-dict additional_data
    with pytest.raises(TypeError):
        FileEncrypter.encrypt_file(
            input_file_path=sample_file,
            output_file_path=output_file,
            password=password,
            additional_data="not_a_dict",  # type: ignore
        )


def test_encrypt_file_creates_encrypted_file(
    tmp_path: Path,
    password: str,
) -> None:
    """Test that FileEncrypter can encrypt a file correctly."""

    # Create a sample file for testing
    sample_file = tmp_path / "test_file.txt"
    original_content = "This is a test file with some content to encrypt."
    sample_file.write_text(original_content)

    # Define output encrypted file path
    encrypted_file = tmp_path / "encrypted.bin"

    # Encrypt the file
    FileEncrypter.encrypt_file(
        input_file_path=sample_file,
        output_file_path=encrypted_file,
        password=password,
        additional_data=None,
    )

    # Verify that the encrypted file was created
    assert encrypted_file.exists(), "Encrypted file should be created."

    # Verify that the encrypted file is different from the original
    encrypted_content = encrypted_file.read_bytes()
    original_content_bytes = original_content.encode("utf-8")

    assert encrypted_content != original_content_bytes, (
        "Encrypted content should be different from original."
    )
    assert len(encrypted_content) > len(original_content_bytes), (
        "Encrypted file should be larger (includes salt and encryption overhead)."
    )

    # Verify that the file starts with a 16-byte salt
    assert len(encrypted_content) >= 16, (
        "Encrypted file should contain at least 16 bytes for salt."
    )


def test_encrypt_file_with_different_passwords_produces_different_results(
    tmp_path: Path,
    password: str,
    sample_file: Path,
    wrong_password: str,
) -> None:
    """Test that encrypting the same file with different passwords produces different results."""

    encrypted_file_1 = tmp_path / "encrypted1.pec"
    encrypted_file_2 = tmp_path / "encrypted2.pec"

    # Encrypt with first password
    FileEncrypter.encrypt_file(
        input_file_path=sample_file,
        output_file_path=encrypted_file_1,
        password=password,
    )

    # Encrypt with second password
    encrypted_file_2 = tmp_path / "encrypted2.bin"
    FileEncrypter.encrypt_file(
        input_file_path=sample_file,
        output_file_path=encrypted_file_2,
        password=wrong_password,
    )

    # Verify that the encrypted files are different
    encrypted_content_1 = encrypted_file_1.read_bytes()
    encrypted_content_2 = encrypted_file_2.read_bytes()

    assert encrypted_content_1 != encrypted_content_2, (
        "Different passwords should produce different encrypted content."
    )


def test_encrypt_same_file_twice_produces_different_results(
    tmp_path: Path,
    sample_file: Path,
    password: str,
) -> None:
    """Test that encrypting the same file twice with the same password produces different results (due to nonce)."""

    encrypted_file_1 = tmp_path / "encrypted1.pec"
    encrypted_file_2 = tmp_path / "encrypted2.pec"

    # Encrypt the file first time
    FileEncrypter.encrypt_file(
        input_file_path=sample_file,
        output_file_path=encrypted_file_1,
        password=password,
    )

    # Encrypt the file second time with same password
    FileEncrypter.encrypt_file(
        input_file_path=sample_file,
        output_file_path=encrypted_file_2,
        password=password,
    )

    # Verify that the encrypted files are different (due to different salts)
    encrypted_content_1 = encrypted_file_1.read_bytes()
    encrypted_content_2 = encrypted_file_2.read_bytes()

    assert encrypted_content_1 != encrypted_content_2, (
        "Same file encrypted twice should produce different results due to salt randomization."
    )

    # But the nonces (first 12 bytes) should be different
    nonce_1 = encrypted_content_1[:12]
    nonce_2 = encrypted_content_2[:12]

    assert nonce_1 != nonce_2, "Different encryptions should use different nonces."


def test_decrypt_file_checks_inputs(
    sample_file: Path,
    password: str,
) -> None:
    """Test that FileEncrypter raises errors for invalid inputs during decryption."""

    temp_dir = sample_file.parent

    # Test that TypeError is raised for non-Path input_file_path
    with pytest.raises(TypeError):
        FileEncrypter.decrypt_file(
            input_file_path="not_a_path",  # type: ignore
            password=password,
        )

    # Test that FileNotFoundError is raised for non-existent input_file_path
    with pytest.raises(FileNotFoundError):
        FileEncrypter.decrypt_file(
            input_file_path=temp_dir / "non_existent_file.txt",
            password=password,
        )

    # Test that ValueError is raised for non-file input_file_path (directory)
    with pytest.raises(ValueError):
        FileEncrypter.decrypt_file(
            input_file_path=temp_dir,
            password=password,
        )

    # Test that TypeError is raised for non-string password
    with pytest.raises(TypeError):
        FileEncrypter.decrypt_file(
            input_file_path=sample_file,
            password=123,  # type: ignore
        )

    # Test that ValueError is raised for empty password
    with pytest.raises(ValueError):
        FileEncrypter.decrypt_file(
            input_file_path=sample_file,
            password="",
        )

    # Test that ValueError is raised for password that does not decode to 32 bytes
    with pytest.raises(ValueError):
        FileEncrypter.decrypt_file(
            input_file_path=sample_file,
            password="short_password",
        )

    # Test that TypeError is raised for non-dict additional_data
    with pytest.raises(TypeError):
        FileEncrypter.decrypt_file(
            input_file_path=sample_file,
            password=password,
            additional_data="not_a_dict",  # type: ignore
        )


def test_decrypt_file_returns_decrypted_content(
    sample_file: Path,
    password: str,
) -> None:
    """Test that FileEncrypter can decrypt an encrypted file correctly."""

    encrypted_file = sample_file.parent / "encrypted.pec"

    # Encrypt the file
    FileEncrypter.encrypt_file(
        input_file_path=sample_file,
        output_file_path=encrypted_file,
        password=password,
    )

    # Decrypt the file
    decrypted_content: BytesIO = FileEncrypter.decrypt_file(
        input_file_path=encrypted_file,
        password=password,
    )

    # Read original content
    original_content = sample_file.read_text()

    # Verify that the decrypted content matches the original content
    assert decrypted_content.getvalue().decode("utf-8") == original_content, (
        "Decrypted content should match the original content."
    )


def test_decrypt_to_disk_writes_decrypted_file(
    sample_file: Path,
    password: str,
) -> None:
    """Test that FileEncrypter can decrypt an encrypted file and write to disk."""

    encrypted_file = sample_file.parent / "encrypted.pec"
    decrypted_file = sample_file.parent / "decrypted.txt"

    # Encrypt the file
    FileEncrypter.encrypt_file(
        input_file_path=sample_file,
        output_file_path=encrypted_file,
        password=password,
    )

    # Decrypt the file to disk
    FileEncrypter.decrypt_to_disk(
        input_file_path=encrypted_file,
        output_file_path=decrypted_file,
        password=password,
    )

    # Read original content
    original_content = sample_file.read_text()

    # Verify that the decrypted file matches the original content
    assert decrypted_file.read_text() == original_content, (
        "Decrypted file content should match the original content."
    )
