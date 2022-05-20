#!/usr/bin/env python3
from asyncio import protocols, transports
from typing import Optional, Tuple

from hyteratak.lib.logging_trait import LoggingTrait
from hyteratak.lib.settings import BridgeSettings

class CustomBridgeDatagramProtocol(protocols.DatagramProtocol, LoggingTrait):
    def __init__(self, name: str, port: int, settings: BridgeSettings) -> None:
        super().__init__()
        self.settings = settings
        self.name = name
        self.port = port
        self.transport: Optional[transports.DatagramTransport] = None
        self.hosts = []
        for h in self.settings.forward_to_hosts:
            self.hosts.append((h,port))

    def datagram_received(self, data: bytes, address: Tuple[str, int]) -> None:
        try:
            for h in self.hosts:
                self.transport.sendto(data, h)
        except BaseException as e:
            pass

    def connection_lost(self, exc: Optional[Exception]) -> None:
        self.log_info("connection lost")
        if exc:
            self.log_exception(exc)

    def connection_made(self, transport: transports.BaseTransport) -> None:
        self.transport = transport
        self.log_debug("connection prepared")

    def disconnect(self):
        self.log_warning("Self Disconnect")

    def log_debug(self, msg: str):
        super().get_logger().debug(self.name + " " + msg)

    def log_info(self, msg: str):
        super().get_logger().info(self.name + " " + msg)

    def log_warning(self, msg: str):
        super().get_logger().warning(self.name + " " + msg)

    def log_error(self, msg: str):
        super().get_logger().error(self.name + " " + msg)

__author__ = "Kortel <hytera@kortel.systems>"
__copyright__ = "Copyright 2022 Kortel"
__license__ = "Apache License, Version 2.0"
