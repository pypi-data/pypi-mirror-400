"""Definition of integration test fixtures."""

import pytest
import json
from pathlib import Path
import tempfile
from collections.abc import Iterator


@pytest.fixture
def password() -> str:
    """Fixture that provides a test password.

    Returns:
        str: A test password.
    """
    return "sZoOOTSY32x-4nzb_6XXtmfY2tA3R6KFcHLGS1hGA30="  # Base64-encoded 32-byte key


@pytest.fixture
def wrong_password() -> str:
    """Fixture that provides a wrong test password.

    Returns:
        str: A wrong test password.
    """
    return "5mtlZEFgdvVyrcpF-__xoBNFuDaUjpqLOb-Y05AOdKY="  # Base64-encoded 32-byte key


@pytest.fixture
def aad() -> str:
    """Fixture that provides additional authenticated data (AAD) for tests.

    Returns:
        str: AAD JSON string.
    """
    return json.dumps(
        {
            "TEST_KEY": "TEST_VALUE",
            "MODULE_VERSION": "1.0.0",
        },
    )


@pytest.fixture
def wrong_aad() -> str:
    """Fixture that provides wrong additional authenticated data (AAD) for tests.

    Returns:
        str: Wrong AAD JSON string.
    """
    return json.dumps(
        {
            "TEST_KEY": "TEST_VALUE",
            "MODULE_VERSION": "1.1.0",
        },
    )


@pytest.fixture(scope="function")
def tmp_dir() -> Iterator[Path]:
    """Fixture that provides a temporary directory for tests.

    Yields:
        Path: A temporary directory path.
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


@pytest.fixture
def simple_python_module() -> Path:
    """Path to a simple hello world Python module."""
    return Path(__file__).parent.parent / "test_data" / "simple_python_module"


@pytest.fixture
def nested_python_module() -> Path:
    """Path to a complex Python module with internal dependencies."""
    return Path(__file__).parent.parent / "test_data" / "nested_python_module"
