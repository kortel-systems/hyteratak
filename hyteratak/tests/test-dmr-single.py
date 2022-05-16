#!/usr/bin/env python3

import importlib.util
import os
import sys

if __name__ == "__main__":

    self_name: str = "hyteratak"
    self_spec = importlib.util.find_spec(self_name)
    if self_spec is None:
        parent_folder: str = os.path.dirname(
            os.path.dirname(os.path.realpath(__file__))
        )
        expected_folder: str = f"{parent_folder}{os.path.sep}"
        if os.path.isdir(expected_folder):
            sys.path.append(expected_folder)

from hyteratak.tests.prettyprint import prettyprint
from hyteratak.kaitai.hytera_simple_transport_reliability_protocol import HyteraSimpleTransportReliabilityProtocol
from hyteratak.kaitai.hytera_dmr_application_protocol import HyteraDmrApplicationProtocol

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("use as %s <hexstring>" % sys.argv[0])
        exit(0)

    packet = HyteraDmrApplicationProtocol.from_bytes(
        bytes.fromhex(sys.argv[1])
    )
    prettyprint(packet)
    print(packet.data.opcode)

__author__ = "Kortel <info@kortel.systems>"
__copyright__ = "Copyright 2022 Kortel"
__license__ = "Apache License, Version 2.0"
