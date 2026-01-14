"""Definition of unit test fixtures."""

from pathlib import Path
import tempfile
from collections.abc import Iterator
import pytest


@pytest.fixture
def tmp_path() -> Iterator[Path]:
    """Fixture that provides a temporary directory for tests.

    Yields:
        Path: The path to the temporary directory.
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


@pytest.fixture
def sample_file() -> Iterator[Path]:
    """Fixture that creates a sample file for testing.

    Yields:
        Path: The path to the sample file.
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        sample_file = Path(tmpdirname) / "sample.txt"
        sample_file.write_text("This is a sample file for testing.")
        yield sample_file


@pytest.fixture(scope="session")
def sample_folder() -> Iterator[Path]:
    """Fixture that creates a sample folder with files for testing.

    Yields:
        Path: The path to the sample folder.
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        sample_dir = Path(tmpdirname)
        (sample_dir / "file1.txt").write_text("This is file 1.")
        (sample_dir / "file2.txt").write_text("This is file 2.")
        sub_dir = sample_dir / "subdir"
        sub_dir.mkdir()
        (sub_dir / "file3.txt").write_text("This is file 3 in subdir.")
        yield sample_dir


@pytest.fixture
def nested_python_module() -> Path:
    """Path to a complex Python module with internal dependencies."""
    return Path(__file__).parent.parent / "test_data" / "nested_python_module"


@pytest.fixture
def password() -> str:
    """Fixture that provides a sample password for encryption tests.

    Returns:
        str: A sample password.
    """
    return "sZoOOTSY32x-4nzb_6XXtmfY2tA3R6KFcHLGS1hGA30="  # Base64-encoded 32-byte key


@pytest.fixture
def wrong_password() -> str:
    """Fixture that provides a wrong test password.

    Returns:
        str: A wrong test password.
    """
    return "5mtlZEFgdvVyrcpF-__xoBNFuDaUjpqLOb-Y05AOdKY="  # Base64-encoded 32-byte key
