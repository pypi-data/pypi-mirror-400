""" The CL-Init Data Package.
"""
from typing import Iterable

from changelist_data.changelist import Changelist, get_default_cl
from changelist_data.file_change import FileChange
from changelist_data.storage.changelist_data_storage import ChangelistDataStorage

from changelist_init.data import fc_to_cl_map


_DEFAULT_CHANGELIST_ID = '4a74640f-90b3-86a1-ab28-af29299c84fd'
_DEFAULT_CHANGELIST_NAME = "Initial Changelist"


def merge_file_changes(
    storage: ChangelistDataStorage,
    files: Iterable[FileChange],
):
    """ Merge FileChange into Changelists.
 - Leaves existing files in their Changelists.
 - Inserts all new files into the default Changelist.
 - Creates DEFAULT_CHANGELIST if storage is empty.

**Parameters:**
 - storage (ChangelistDataStorage): The in-memory storage object from the changelist_data package.
 - files (Iterable[FileChange]): The FileChanges obtained from Git to merge into storage object.
    """
    initial_changelists = storage.get_changelists()
    if (default_cl := get_default_cl(initial_changelists)) is None:
        initial_changelists.append(
            Changelist(
                id=_DEFAULT_CHANGELIST_ID,
                name=_DEFAULT_CHANGELIST_NAME,
                changes=files if isinstance(files, list) else list(files),
                comment='',
                is_default=True,
            )
        )
    else:
        default_cl.changes.extend(
            fc_to_cl_map.merge_fc_generator(
                changelists=initial_changelists,
                file_changes=files,
            )
        )
    storage.update_changelists(initial_changelists)
