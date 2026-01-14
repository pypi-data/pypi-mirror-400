"""Fake files for testing ehr_utils."""
from contextlib import contextmanager
import pathlib
import tempfile
import typing
from uuid import uuid4


def write_file(table: list[list[str]], dirname: str) -> str:
    """Write table to tsv file."""
    with open(pathlib.Path(dirname) / str(uuid4()), "w") as f:
        f.write("\n".join("\t".join(row) for row in table))
        f.seek(0)
    return f.name


@contextmanager
def fake_files(
    *tables: list[list[str]],
) -> typing.Generator[tuple[str, ...], None, None]:
    """Generate fake files from data arrays."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tuple(write_file(table, tmpdirname) for table in tables)
