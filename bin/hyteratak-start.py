#!/usr/bin/env python3
if __name__ == "__main__":
    import re
    import os
    import sys
    import importlib.util

    self_name: str = "hyteratak"
    self_spec = importlib.util.find_spec(self_name)
    if self_spec is None:
        print(f"Package {self_name} is not installed, trying locally\n")
        parent_folder: str = os.path.dirname(
            os.path.dirname(os.path.realpath(__file__))
        )
        expected_folder: str = f"{parent_folder}{os.path.sep}"
        if os.path.isdir(expected_folder):
            sys.path.insert(0, expected_folder)

    from hyteratak.cli.hyteratak_start import cli
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(cli())

__author__ = "Kortel <hytera@kortel.systems>"
__copyright__ = "Copyright 2022 Kortel"
__license__ = "Apache License, Version 2.0"
