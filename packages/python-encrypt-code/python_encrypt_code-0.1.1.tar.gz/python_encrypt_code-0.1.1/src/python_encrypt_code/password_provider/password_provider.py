"""Definition of PasswordProvider class."""

import os
import json
import base64
import secrets

from .password_provider_interface import PasswordProviderInterface


class PasswordProviderExample(PasswordProviderInterface):
    """Class to provide password for encryption.
    Please extend this class to implement your own password storage/retrieval logic.
    """

    _encoding: str = "utf-8"

    @classmethod
    def generate_password(cls) -> str:
        """Generate a new password AES-256-GCM compliant key (32 bytes, base64-url encoded).

        Returns:
            str: The generated password.
        """

        # AES-256 requires a 32-byte key
        key_bytes = secrets.token_bytes(32)
        url_safe_string = base64.urlsafe_b64encode(key_bytes).decode(cls._encoding)
        return url_safe_string

    @classmethod
    def get_decryption_keys(cls) -> tuple[str, dict[str, str] | None]:
        """Placeholder function to get decryption keys. Implement your own logic here.

        Returns:
            password: str: The password fetched from the authentication provider.
            aad: dict[str, str] | None: The additional authenticated data.
        """

        # Simulate using metadata to authenticate and get decryption keys
        password_str = cls._get_password()

        # Simulate using metadata to authenticate and get AAD
        aad_dict = cls._get_additional_authenticated_data()

        return password_str, aad_dict

    @classmethod
    def _collect_metadata(cls) -> dict[str, str]:
        """Placeholder function to collect metadata. Implement your own logic here.

        Returns:
            dict[str, str]: The metadata fetched from e.g. environment variables.
        """

        # Simulate fetching metadata from environment variables
        return {"DEPLOYED_MODULE_VERSION": "0.1.0"}

    @classmethod
    def _get_additional_authenticated_data(cls) -> dict[str, str] | None:
        """Placeholder function to get optional additional authenticated data (AAD). Implement your own logic here.

        Returns:
            dict[str, str] | None: The additional authenticated data.
        """

        # Simulate collecting metadata about self to authorize against external provider
        _ = cls._collect_metadata()

        # Simulate fetching AAD from an external provider
        aad_str = os.getenv("PEC_AAD", None)
        if aad_str is None:
            return None
        aad_dict = {str(k): str(v) for k, v in json.loads(aad_str).items()}

        return aad_dict

    @classmethod
    def _get_password(cls) -> str:
        """Placeholder function to get password. Implement your own logic here.

        Returns:
            str: The password fetched from the authentication provider.
        """

        # Simulate collecting metadata about self to authorize against external provider
        _ = cls._collect_metadata()

        # Simulate fetching password from an external authentication provider
        if password_str := os.getenv("PEC_PASSWORD"):
            return password_str

        raise ValueError(
            "PEC_PASSWORD environment variable not set. "
            "Please set it to use this PasswordProvider."
        )
