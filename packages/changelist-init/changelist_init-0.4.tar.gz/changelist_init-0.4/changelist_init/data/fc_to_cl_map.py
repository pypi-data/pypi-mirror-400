""" Methods for Mapping FileChanges into Changelist Data structures.
"""
from typing import Iterable, Generator

from changelist_data import Changelist
from changelist_data.file_change import FileChange


def create_fc_to_cl_dict(
    changelists: Iterable[Changelist],
) -> dict[str, Changelist]:
    """ Initialize the Map of Existing FileChanges.
 - Clears each Changelist contents as they are inserted into the map.

**Parameters:
 - changelists (Iterable[Changelist]): The changelists to be inserted into the map.

**Returns:**
 dict[str, Changelist] - A map from file path to the Changelist object that contains it.
    """
    cl_map: dict[str, Changelist] = {}
    for cl in changelists:
        for fc in cl.changes:
            cl_map[_get_first_path(fc)] = cl
        cl.changes.clear()
    return cl_map


def offer_fc_to_cl_dict(
    fc_map: dict[str, Changelist],
    file: FileChange
) -> bool:
    """ Map a FileChange into an existing Changelist.
 - Searches the Dict for both FileChange paths, starting with the before_path.
 - Appends FC to CL changes and returns true if found.

**Parameters:**
 - fc_map (dict[str, Changelist]): The FileChange-to-Changelist Map.
 - file (FileChange): The FC to search the dict for, and add to the Changelist if found.

**Returns:**
 bool - True if the FC was added to a CL. False if the file was not found.
    """
    if (cl := fc_map.get(_get_first_path(file))) is not None:  # Match!
        cl.changes.append(file)
        return True
    return False # FC not in map


def _get_first_path(file: FileChange) -> str:
    if file.before_path:
        return file.before_path
    if file.after_path:
        return file.after_path
    exit("A Git Reader Error may have occurred.")


def merge_fc_generator(
    changelists: Iterable[Changelist],
    file_changes: Iterable[FileChange],
) -> Generator[FileChange, None, None]:
    """ Merge FC into existing CL, applying the fc_to_cl_map module.

**Parameters:**
 - existing_lists (Iterable[Changelist]): The list of existing Changelists.
 - files (Iterable[FileChange]): The iterable FileChange objects produced during initialization.

**Yields:**
 FileChange - The FileChange objects that are new, not present in existing Changelists.
    """
    cl_map = create_fc_to_cl_dict(changelists)
    # Search for matches using map
    for fc in file_changes:
        if not offer_fc_to_cl_dict(cl_map, fc):
            yield fc
