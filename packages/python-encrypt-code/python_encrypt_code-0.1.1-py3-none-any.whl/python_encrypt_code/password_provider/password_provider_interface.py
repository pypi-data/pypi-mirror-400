"""Definition of PasswordProviderInterface."""

from abc import ABC, abstractmethod


class PasswordProviderInterface(ABC):
    """Interface for password providers."""

    @classmethod
    @abstractmethod
    def generate_password(cls) -> str:
        """Generate a new password for encryption and decryption.

        Returns:
            str: The generated password.
        """

    @classmethod
    @abstractmethod
    def get_decryption_keys(cls) -> tuple[str, dict[str, str] | None]:
        """Get decryption keys for decryption.

        Returns:
            dict: The decryption keys.
        """
