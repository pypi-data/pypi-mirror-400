""" Maps Git Status data into FileChange data.
"""
from itertools import groupby
from typing import Callable, Iterable, Generator

from changelist_data import file_change
from changelist_data.file_change import FileChange

from changelist_init.git.status_reader import GitFileStatus


def map_file_status_to_changes(
    git_files: Iterable[GitFileStatus],
) -> Generator[FileChange, None, None]:
    """ Categorize by Status Code, and Map to FileChange data objects.

**Parameters:**
 - git_files (Iterable[GitFileStatus]): An iterable or Generator providing GitFileStatus objects.

**Yields:**
 FileChange - Generated File Changes.
    """
    for code, group in groupby(git_files, lambda w: w.code):
        if (mapping_function := get_status_code_change_map(code)) is None:
            print(f"Unrecognized Git Status Code:({code})")
            continue
        for file_status in group:
            yield mapping_function(
                _map_status_path_to_change(file_status.file_path)
            )


def get_status_code_change_map(
    code: str,
) -> Callable[[str, ], FileChange] | None:
    """ Get a FileChange mapping callable for a specific code.
 - (C)opied and (R)enamed are disabled in git status --no-renames.

**Parameters:**
 - code (str): The status code, determining what kind of FileChange (create, modify, delete)

**Returns:**
 Callable[str, FileChange]? - A function that maps a FileChange path into the FileChange object. None if the code is unrecognized.
    """
    if '?' in code or 'A' in code or '!' in code:
        return file_change.create_fc
    if 'D' in code:
        return file_change.delete_fc
    if 'M' in code or 'U' in code or 'T' in code:
        return file_change.update_fc
    return None


def _map_status_path_to_change(
    status_path: str,
) -> str:
    """ Convert Status File path to FileChange path.
 - Adds a leading slash character if not present.
    """
    return '/' + status_path if not status_path.startswith('/') else status_path
