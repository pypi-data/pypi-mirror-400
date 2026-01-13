""" Reader for the Git Status Output String.
"""
from collections import namedtuple
from typing import Generator


GitFileStatus = namedtuple(
    'GitFileStatus',
    'code file_path',
)


def generate_file_status(
    status_string: str,
) -> Generator[GitFileStatus, None, None]:
    """ Generate GitFileStatus objects from the output of Git Status operation.

**Parameters:**
 - status_string (str): The output of the Git Status operation, as a string.

**Yields:**
 GitFileStatus - The file information including status code and file path.
    """
    if not isinstance(status_string, str):
        raise TypeError("Must be a String!")
    for f in status_string.splitlines():
        if (file_status := read_git_status_line(f)) is not None:
            yield file_status
        else:
            print(f"Skipped: ${f}")


def read_git_status_line(
    file_status_line: str
) -> GitFileStatus | None:
    """ Read a line of output from Git Status, into a GitFileStatus object.

**Parameters:**
 - file_status_line (str): The line of status output to process into a GitFileStatus object.

**Returns:**
 GitFileStatus? - The status code and file_path in a tuple, or None if the input string was not accepted.
    """
    if len(file_status_line.strip()) < 3:
        return None
    if file_status_line.endswith('/'):
        return None
    return GitFileStatus(
        code=file_status_line[:2],
        file_path=file_status_line[3:],
    )
