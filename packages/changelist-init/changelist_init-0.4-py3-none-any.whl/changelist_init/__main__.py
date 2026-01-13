#!/usr/bin/python


def main():
    from sys import argv
    # Validate Input Data
    from changelist_init.input import validate_input
    input_data = validate_input(argv[1:])
    # Run CL-INIT Process
    from changelist_init import process_cl_init
    process_cl_init(input_data)


if __name__ == "__main__":
    from pathlib import Path
    from sys import path
    # Get the directory of the current file (__file__ is the path to the script being executed)
    current_directory = Path(__file__).resolve().parent.parent
    path.append(str(current_directory)) # Add the directory to sys.path
    # Now imports have parent dir in path
    main()
