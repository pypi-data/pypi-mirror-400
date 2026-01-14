# Utilities for developing EHR utilities

Even utilities need utilities!

## Functions

* `fake_files` - provides test doubles for tsv files

## Installation

```bash
pip install git+https://github.com/biostat821/ehr-utils-utils.git@main
```

## Usage

The `fake_files` context manager takes tables (`list[list[str]]`), produces temporary tsv files from them, and yields the filenames. The temporary files will be deleted when the context is exited. 

Example usage:
```python
from ehr_utils_utils import fake_files

def test_my_parse_fcn():
    table = [["a", "b"], ["1", "2"]]
    with fake_files(table) as filenames:
        my_parse_fcn(filenames[0])
        ...
```

## Development

We welcome contributions! Before opening a pull request, please confirm that existing regression tests pass:

```python
python -m pytest tests/
```
