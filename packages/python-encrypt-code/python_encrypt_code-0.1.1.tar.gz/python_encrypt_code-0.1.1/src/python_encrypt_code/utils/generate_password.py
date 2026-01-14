"""Definition of generate_password function."""

from python_encrypt_code import PasswordProvider


def generate_password() -> None:
    """Generate and print a secure password."""

    # Generate and print a secure password
    password = PasswordProvider.generate_password()
    print(password)
