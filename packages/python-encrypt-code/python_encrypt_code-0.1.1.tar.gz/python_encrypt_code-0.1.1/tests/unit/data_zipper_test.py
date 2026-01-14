"""Unit tests for data_zipper module."""

import zipfile
from pathlib import Path
from io import BytesIO

from python_encrypt_code.data_zipper.data_zipper import DataZipper


def test_data_zipper_zip_data_checks_inputs(
    tmp_path: Path,
) -> None:
    """Test that DataZipper raises errors for invalid inputs."""

    # Test that TypeError is raised for non-Path input_path
    try:
        DataZipper.zip_data(
            input_path="not_a_path",  # type: ignore
            output_path=tmp_path / "output.zip",
        )
    except TypeError as e:
        assert str(e) == "input_path must be a Path object"

    # Test that FileNotFoundError is raised for non-existent input_path
    try:
        DataZipper.zip_data(
            input_path=tmp_path / "non_existent_directory",
            output_path=tmp_path / "output.zip",
        )
    except FileNotFoundError as e:
        assert (
            str(e) == f"input_path {tmp_path / 'non_existent_directory'} does not exist"
        )

    # Test that ValueError is raised for non-directory input_path
    tmp_not_dir = tmp_path / "not_a_directory"
    tmp_not_dir.write_text("This is a file, not a directory.")
    try:
        DataZipper.zip_data(
            input_path=tmp_not_dir,
            output_path=tmp_path / "output.zip",
        )
    except ValueError as e:
        assert str(e) == "input_path must be a directory"

    # Test that TypeError is raised for non-Path output_path
    try:
        DataZipper.zip_data(
            input_path=tmp_path,
            output_path="not_a_path",  # type: ignore
        )
    except TypeError as e:
        assert str(e) == "output_path must be a Path object"


def test_data_zipper_zips_folder(
    tmp_path: Path,
    sample_folder: Path,
) -> None:
    """Test that DataZipper can zip a folder correctly."""

    # Define output zip file path
    output_zip = tmp_path / "output.zip"

    # Zip the sample folder
    DataZipper.zip_data(
        input_path=sample_folder,
        output_path=output_zip,
    )

    # Verify that the zip file was created
    assert output_zip.exists(), "Zip file should be created."

    # Verify the contents of the zip file
    with zipfile.ZipFile(output_zip, "r") as zipf:
        zip_contents = zipf.namelist()
        expected_files = [
            "file1.txt",
            "file2.txt",
            "subdir/file3.txt",
        ]
        for expected_file in expected_files:
            assert expected_file in zip_contents, (
                f"{expected_file} not found in zip file."
            )


def test_data_zipper_unzip_data_checks_inputs() -> None:
    """Test that DataZipper raises errors for invalid inputs during unzip."""

    # Test that TypeError is raised for non-BytesIO input_data
    try:
        DataZipper.unzip_data(
            input_data="not_a_path",  # type: ignore
        )
    except TypeError as e:
        assert str(e) == "input_data must be a BytesIO object"

    # Test that ValueError is raised for empty BytesIO input_data
    empty_bytesio = BytesIO()
    try:
        DataZipper.unzip_data(
            input_data=empty_bytesio,
        )
    except ValueError as e:
        assert str(e) == "input_data must not be empty"


def test_data_zipper_unzips_file(
    tmp_path: Path,
    sample_folder: Path,
) -> None:
    """Test that DataZipper can unzip a file correctly."""

    # First, create a zip file from the sample folder
    output_zip = tmp_path / "output.zip"
    DataZipper.zip_data(
        input_path=sample_folder,
        output_path=output_zip,
    )

    # Read the zip file into a BytesIO object
    with open(output_zip, "rb") as f:
        zip_data = BytesIO(f.read())

    # Now, unzip the created zip file
    extracted_files = DataZipper.unzip_data(
        input_data=zip_data,
    )

    # Verify that the correct files were extracted
    expected_files = [
        "file1.txt",
        "file2.txt",
        "subdir/file3.txt",
    ]
    for expected_file in expected_files:
        assert expected_file in extracted_files, (
            f"{expected_file} not found in extracted files."
        )
        # Optionally, verify the content of the extracted files
        if expected_file == "file1.txt":
            assert extracted_files[expected_file].getvalue() == b"This is file 1."
        elif expected_file == "file2.txt":
            assert extracted_files[expected_file].getvalue() == b"This is file 2."
        elif expected_file == "subdir/file3.txt":
            assert (
                extracted_files[expected_file].getvalue()
                == b"This is file 3 in subdir."
            )


def test_data_zipper_unzips_file_to_disk(
    tmp_path: Path,
    sample_folder: Path,
) -> None:
    """Test that DataZipper can unzip a file to disk correctly."""

    # First, create a zip file from the sample folder
    output_zip = tmp_path / "output.zip"
    DataZipper.zip_data(
        input_path=sample_folder,
        output_path=output_zip,
    )

    # Read the zip file into a BytesIO object
    with open(output_zip, "rb") as f:
        zip_data = BytesIO(f.read())

    # Define output directory for unzipping
    unzip_output_dir = tmp_path / "unzipped"
    unzip_output_dir.mkdir()

    # Unzip the created zip file to disk
    DataZipper.unzip_data_to_disk(
        input_data=zip_data,
        output_path=unzip_output_dir,
    )

    # Verify that the correct files were extracted to disk
    expected_files = [
        unzip_output_dir / "file1.txt",
        unzip_output_dir / "file2.txt",
        unzip_output_dir / "subdir" / "file3.txt",
    ]
    for expected_file in expected_files:
        assert expected_file.exists(), f"{expected_file} should exist on disk."


def test_data_zipper_unzip_to_disk_checks_inputs(
    tmp_path: Path,
) -> None:
    """Test that DataZipper raises errors for invalid inputs during unzip to disk."""

    # Test that TypeError is raised for non-BytesIO input_data
    try:
        DataZipper.unzip_data_to_disk(
            input_data="not_a_path",  # type: ignore
            output_path=tmp_path / "output_dir",
        )
    except TypeError as e:
        assert str(e) == "input_data must be a BytesIO object"

    # Test that TypeError is raised for non-Path output_path
    try:
        DataZipper.unzip_data_to_disk(
            input_data=BytesIO(b"some data"),
            output_path="not_a_path",  # type: ignore
        )
    except TypeError as e:
        assert str(e) == "output_path must be a Path object"

    # Test that ValueError is raised for empty BytesIO input_data
    empty_bytesio = BytesIO()
    try:
        DataZipper.unzip_data_to_disk(
            input_data=empty_bytesio,
            output_path=tmp_path / "output_dir",
        )
    except ValueError as e:
        assert str(e) == "input_data must not be empty"
