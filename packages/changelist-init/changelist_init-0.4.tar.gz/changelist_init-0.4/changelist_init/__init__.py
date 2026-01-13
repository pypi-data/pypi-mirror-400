""" CL-INIT Main Package Methods.
 Author: DK96-OS 2024 - 2025
"""
from changelist_data.storage.changelist_data_storage import ChangelistDataStorage
from changelist_data.storage.storage_type import StorageType

from changelist_init.data import merge_file_changes
from changelist_init.git import generate_file_changes
from changelist_init.input.input_data import InputData


def process_cl_init(input_data: InputData):
    """ The Changelist Init Process.

**Parameters:**
 - input_data (InputData): The Changelist Init input data.
    """
    init_storage(
        storage=input_data.storage,
        include_untracked=input_data.include_untracked,
    )
    _write_storage(input_data.storage)


def init_storage(
    storage: ChangelistDataStorage,
    include_untracked: bool,
):
    """ Get New FileChange Information, Merge into Changelists Data Storage.

**Parameters:*
 - storage (ChangelistDataStorage): The Storage object to obtain existing CL from, and send updates to.
 - include_untracked (bool): Whether to tell git to include untracked files.
    """
    merge_file_changes(
        storage,
        generate_file_changes(include_untracked)
    )


def _write_storage(storage: ChangelistDataStorage) -> bool:
    if not storage.write_to_storage(): # Write Changelist Data file
        if storage.storage_type == StorageType.CHANGELISTS:
            exit("Failed to write Changelist data file!")
        elif storage.storage_type == StorageType.WORKSPACE:
            exit("Failed to write Workspace data file!")
    return True
