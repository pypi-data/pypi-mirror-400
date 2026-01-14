"""Entry point for running the package as a module."""

import multiprocessing
import sys
import os


if __name__ == "__main__":
    # Fix for windowed PyInstaller builds - redirect stdout/stderr
    if sys.stdout is None:
        sys.stdout = open(os.devnull, 'w')
    if sys.stderr is None:
        sys.stderr = open(os.devnull, 'w')

    # https://stackoverflow.com/a/32677108
    multiprocessing.freeze_support()

    from molecular_dynamics_toy.app import main

    main()
