"""Test fake files."""
import pytest

from ehr_utils_utils import fake_files


def test_fake_files_tsv() -> None:
    """Test that fake files constructs the correct tsv."""
    table = [["a", "b"], ["1", "2"]]
    with fake_files(table) as filenames:
        with open(filenames[0]) as f:
            data = f.read()
    assert [row.split("\t") for row in data.strip().split("\n")] == table


def test_fake_files_deletes() -> None:
    """Test fake files deletes the constructed files."""
    with fake_files([]) as filenames:
        pass
    with pytest.raises(FileNotFoundError):
        open(filenames[0])
