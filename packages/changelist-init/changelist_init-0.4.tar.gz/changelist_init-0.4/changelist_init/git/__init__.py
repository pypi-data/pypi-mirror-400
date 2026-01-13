""" Git Management Package.
"""
from typing import Generator

from changelist_data.file_change import FileChange

from changelist_init.git import status_runner, status_reader, status_change_mapping


def generate_file_changes(
    include_untracked: bool,
) -> Generator[FileChange, None, None]:
    """ Initialize FileChanges with a Generator.

**Parameters:**
 - include_untracked (bool): Whether to include untracked files in the git status output.

**Yields:**
 FileChange - Those precious File Changes, created from Git Status output.
    """
    yield from status_change_mapping.map_file_status_to_changes(
        status_reader.generate_file_status(
            status_runner.run_git_status(include_untracked)
        )
    )
