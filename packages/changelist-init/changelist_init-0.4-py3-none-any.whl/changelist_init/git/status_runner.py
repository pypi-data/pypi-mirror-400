""" Runner for Git Status Operation.
"""
import subprocess


def run_git_status(
    include_untracked: bool = False,
) -> str:
    """ Run a Git Status Process and Return the Output.

**Parameters:**
 - include_untracked (bool): Whether to include untracked files and directories in the output.

**Returns:**
 str - The output of the Git Status Operation.
    """
    args = ['git', '--no-optional-locks', 'status', '--porcelain', '--no-renames']
    if include_untracked:
        args.append('-uall')
    else:
        args.append('-uno')
    result = subprocess.run(
        args=args,
        capture_output=True,
        text=True,
        universal_newlines=True,
        shell=False,
        timeout=5,
    )
    if (error := result.stderr) is not None and not len(error) < 1:
        exit(f"Git Status Runner Error: {error}")
    return result.stdout
