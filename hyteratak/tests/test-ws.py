#!/usr/bin/env python3

import importlib.util
import os
import sys

try:
    import hyteratak
except ImportError:
    sys.path.append(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    )

from hyteratak.tests.prettyprint import prettyprint
from hyteratak.lib.hytera_tak_translator import HyteraTakTranslator

if __name__ == "__main__":
    val = [(b'N', b'1234.56', 12.576),
        (b'S', b'1234.56', -12.576),
        (b'E', b'11234.56', 112.576),
        (b'W', b'11234.56', -112.576),
    ]
    for t in val:
        print(f"{t[0]} {t[1]} expected {t[2]} = {HyteraTakTranslator.ddmm2deg(t[0], t[1])}")

__author__ = "Kortel <hytera@kortel.systems>"
__copyright__ = "Copyright 2022 Kortel"
__license__ = "Apache License, Version 2.0"
