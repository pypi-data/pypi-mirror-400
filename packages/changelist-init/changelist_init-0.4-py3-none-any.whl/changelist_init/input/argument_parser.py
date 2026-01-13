""" Defines and Validates Argument Syntax.
 - Encapsulates Argument Parser.
 - Returns Argument Data, after the argument syntax is validated.

**ArgumentData NamedTuple Fields:**
 - changelists_file (str?): The string path to the Changelists Data File.
 - workspace_file (str?): The string path to the Workspace File.
 - include_untracked (bool): Whether to include untracked files.
 - enable_workspace_overwrite (bool): Indicates that Workspace is the preferred storage option, if present.
"""
from argparse import ArgumentParser
from collections import namedtuple
from sys import exit

from changelist_data.validation.arguments import validate_string_argument


ArgumentData = namedtuple(
    'ArgumentData',
    (
        'changelists_file',
        'workspace_file',
        'include_untracked',
        'enable_workspace_overwrite',
    ),
    defaults=(None, None, False, False),
)


def parse_arguments(
    args: list[str] | None,
) -> ArgumentData:
    """ Parse command line arguments.

**Parameters:**
 - args: A list of argument strings.

**Returns:**
 ArgumentData : Container for Valid Argument Data.
    """
    if args is None or len(args) == 0:
        return ArgumentData()
    try: # Initialize the Parser and Parse Immediately
        parsed_args = _define_arguments().parse_args(args)
    except SystemExit:
        exit("Unable to Parse Arguments.")
    return _validate_arguments(parsed_args)


def _validate_arguments(
    parsed_args,
) -> ArgumentData:
    if (changelists_file := parsed_args.changelists_file) is not None:
        if not validate_string_argument(changelists_file):
            exit("The Changelists File name was invalid.")
    elif (workspace_file := parsed_args.workspace_file) is not None:
        if not validate_string_argument(workspace_file):
            exit("The Workspace File name was invalid.")
    return ArgumentData(
        changelists_file=parsed_args.changelists_file,
        workspace_file=parsed_args.workspace_file,
        include_untracked=parsed_args.include_untracked,
        enable_workspace_overwrite=parsed_args.enable_workspace_overwrite,
    )


def _define_arguments() -> ArgumentParser:
    """ Initializes and Defines Argument Parser.
 - Sets Required/Optional Arguments and Flags.

**Returns:**
 argparse.ArgumentParser - An instance with all supported Arguments.
    """
    parser = ArgumentParser(
        description='Initializes and updates the Changelist data storage file with git status information. Provides two options for data storage: one independent file option and one that integrates with the IDEA workspace file.',
    )
    # Introduced in Version 3.14: Color, SuggestOnError.
    parser.color = True
    parser.suggest_on_error = True
    # Optional Arguments
    parser.add_argument(
        '--changelists_file',
        type=str,
        default=None,
        help='The Path to the Changelists Data File. Searches default path (.changelists/data.xml) if none.',
    )
    parser.add_argument(
        '--workspace_file',
        type=str,
        default=None,
        help='The Path to the Workspace Data File. Useful if not in the default path (.idea/workspace.xml). Implies --enable_workspace_overwrite.',
    )
    parser.add_argument(
        '--include_untracked', '-u',
        action='store_true',
        default=False,
        help='The option to include untracked files in changelists.',
    )
    parser.add_argument(
        '--enable_workspace_overwrite', '-w',
        action='store_true',
        default=False,
        help='Enable overwriting Workspace file in the default location. Prefers Workspace over Changelist data file, but creates Changelist data file if neither exists.',
    )
    return parser
