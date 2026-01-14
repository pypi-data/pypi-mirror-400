"""Definition of unit tests for PasswordProvider class."""

import os
import base64
import json

from python_encrypt_code.password_provider import PasswordProvider


def test_password_provider_generates_password() -> None:
    """Test that PasswordProvider generates a password correctly."""

    # Generate password
    password = PasswordProvider.generate_password()

    # Verify password is a non-empty string
    assert isinstance(password, str), "Generated password should be a string."
    assert len(password) > 0, "Generated password should not be empty."

    # Verify password is URL-safe base64
    try:
        decoded_bytes = base64.urlsafe_b64decode(
            password.encode(PasswordProvider._encoding)
        )
        print(decoded_bytes)
        assert len(decoded_bytes) == 32, "Decoded password should be 32 bytes long."
    except Exception as e:
        assert False, f"Generated password is not valid URL-safe base64: {e}"


def test_password_provider_get_decryption_keys() -> None:
    """Test that PasswordProvider.get_decryption_keys retrieves the keys correctly."""

    # Set environment variable for get_decryption_keys test
    expected_password = PasswordProvider.generate_password()
    expected_aad = PasswordProvider._collect_metadata()
    os.environ["PEC_PASSWORD"] = expected_password
    os.environ["PEC_AAD"] = json.dumps(expected_aad)

    # Retrieve keys
    password, aad = PasswordProvider.get_decryption_keys()

    # Verify retrieved password
    assert isinstance(password, str), "Password should be a string."
    assert len(password) > 0, "Password should not be empty."
    assert password == expected_password, (
        "get_decryption_keys should return the password from environment variable."
    )

    # Verify retrieved AAD
    assert isinstance(aad, dict), "AAD should be a dictionary."
    assert aad == expected_aad, (
        "get_decryption_keys should return the AAD from environment variable."
    )
