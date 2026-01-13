""" Input Package Method.
"""
from pathlib import Path

from changelist_data import ChangelistDataStorage, validate_string_argument, load_storage, StorageType

from changelist_init.input.argument_parser import parse_arguments
from changelist_init.input.input_data import InputData


def validate_input(
    arguments: list[str],
) -> InputData:
    """ Parse and Validate the Arguments, and return Input Data.

**Parameters:**
 - arguments (list[str]): The arguments received by the program.

**Returns:**
 InputData - The InputData containing the program inputs. The other packages will process the data from here.
    """
    arg_data = parse_arguments(arguments)
    return InputData(
        storage=_validate_storage_arguments(
            arg_data.changelists_file,
            arg_data.workspace_file,
            arg_data.enable_workspace_overwrite,
        ),
        include_untracked=arg_data.include_untracked,
    )


def _validate_storage_arguments(
    changelists_file: str | None,
    workspace_file: str | None,
    enable_workspace_overwrite: bool,
) -> ChangelistDataStorage | None:
    # Validate given Path arguments if provided.
    if validate_string_argument(changelists_file):
        return load_storage(StorageType.CHANGELISTS, Path(changelists_file))
    if validate_string_argument(workspace_file):
        return load_storage(StorageType.WORKSPACE, Path(workspace_file))
    # Check Workspace Overwrite Status
    if enable_workspace_overwrite: # Prefer Workspace File
        if (workspace_storage := load_storage(StorageType.WORKSPACE)) is not None:
            return workspace_storage
    # Only Changelist Data File Enabled
    return load_storage(StorageType.CHANGELISTS)
