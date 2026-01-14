"""Command-line interface for python-encrypt-code package."""

import argparse
import sys
import tempfile
from pathlib import Path

from python_encrypt_code import ModuleImporter
from python_encrypt_code.utils import (
    generate_password,
    encrypt_folder,
    decrypt_to_disk,
)


def main() -> None:
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Encrypt and run folders securely", prog="python-encrypt-code"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate password command
    _ = subparsers.add_parser(
        name="generate-password",
        help="Generate a secure password",
    )

    # Encrypt command
    encrypt_parser = subparsers.add_parser(
        name="encrypt",
        help="Encrypt a folder",
    )
    encrypt_parser.add_argument(
        "folder",
        type=Path,
        help="Path to the folder to encrypt",
    )
    encrypt_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="Path where the encrypted file will be saved",
    )
    encrypt_parser.add_argument(
        "-p",
        "--password",
        type=str,
        help="Password to use for encryption",
    )
    encrypt_parser.add_argument(
        "-aad",
        "--additional-authenticated-data",
        type=str,
        default=None,
        help="JSON-string with optional metadata for encrypted file",
    )

    # Decrypt command
    decrypt_parser = subparsers.add_parser(
        "decrypt",
        help="Decrypt a file to disk",
    )
    decrypt_parser.add_argument(
        "file",
        type=Path,
        help="Path to the encrypted file",
    )
    decrypt_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="Path where the decrypted folder will be saved",
    )

    # Run insecure command
    decrypt_run_parser = subparsers.add_parser(
        "run-insecure",
        help="Decrypt to temporary folder and run a script from an encrypted file",
    )
    decrypt_run_parser.add_argument(
        "file",
        type=Path,
        help="Path to the encrypted file",
    )
    decrypt_run_parser.add_argument(
        "-s",
        "--script",
        type=str,
        default="main.py",
        help="Name of the script to run (default: main.py)",
    )

    # Run command
    run_parser = subparsers.add_parser(
        "run", help="Decrypt to memory and run a script from an encrypted file"
    )
    run_parser.add_argument("file", type=Path, help="Path to the encrypted file")
    run_parser.add_argument(
        "-s",
        "--script",
        type=str,
        default="main.py",
        help="Name of the script to run (default: main.py)",
    )

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == "generate-password":
            generate_password()

        elif args.command == "encrypt":
            encrypt_folder(
                folder_path=args.folder,
                output_path=args.output,
                password=args.password,
                aad=args.additional_authenticated_data,
            )

        elif args.command == "decrypt":
            decrypt_to_disk(
                encrypted_file_path=args.file,
                output_path=args.output,
            )

        elif args.command == "run-insecure":
            # Create temporary directory for decrypted files
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                decrypt_to_disk(
                    encrypted_file_path=args.file,
                    output_path=temp_path,
                )

                # Import and run the specified module
                ModuleImporter.import_module_from_disk(
                    module_path=temp_path,
                    main_module=args.script,
                )

        elif args.command == "run":
            raise NotImplementedError("The 'run' command is not implemented yet.")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
