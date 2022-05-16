#!/usr/bin/env python3
from asyncio import protocols

from hyteratak.lib.logging_trait import LoggingTrait
from hyteratak.lib.settings import BridgeSettings

class CustomBridgeDatagramProtocol(protocols.DatagramProtocol, LoggingTrait):
    def __init__(self, settings: BridgeSettings) -> None:
        super().__init__()
        self.settings = settings

__author__ = "Kortel <info@kortel.systems>"
__copyright__ = "Copyright 2022 Kortel"
__license__ = "Apache License, Version 2.0"
