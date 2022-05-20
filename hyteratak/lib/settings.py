#!/usr/bin/env python3

import configparser

from hyteratak.lib.logging_trait import LoggingTrait

_UNSET = object()


class BridgeSettings(LoggingTrait):
    SECTION_GENERAL = "general"
    SECTION_FTPC = "forward-to-pc"
    SECTION_HYTERATAK = "hyteratak"
    SECTION_LOGGING = "logging"

    MINIMAL_SETTINGS = """
    [forward-to-pc]
    ip = 0.0.0.0

    [hyteratak]
    url = broadcast:239.2.3.1
    """

    def __init__(self, filepath: str = None, filedata: str = None) -> None:

        if not filepath and not filedata:
            raise SystemError(
                "Cannot init BridgeSettings without filepath and filedata, at least one must be provided"
            )

        if filepath and filedata:
            raise SystemError(
                "Both filename and filedata provided, this is unsupported, choose one"
            )

        parser = configparser.ConfigParser()
        self.parser = parser
        parser.sections()
        if filepath:
            parser.read(filenames=filepath)
        else:
            parser.read_string(string=filedata)

        self.ip: str = parser.get(self.SECTION_FTPC, "ip", fallback="0.0.0.0")
        self.gps1_port: int = parser.getint(self.SECTION_FTPC, "gps1_port", fallback=30003)
        self.gps2_port: int = parser.getint(self.SECTION_FTPC, "gps2_port", fallback=30004)
        self.forward_to: int = parser.get(self.SECTION_FTPC, "forward_to", fallback=None)

        self.url: str = parser.get(self.SECTION_HYTERATAK, "url", fallback="broadcast:239.2.3.1")
        self.cot_type: str = parser.get(self.SECTION_HYTERATAK, "type", fallback="a-f-G-U-C")
        self.cot_stale: int  = parser.getint(self.SECTION_HYTERATAK, "stale", fallback=3600)
        self.groupname: str  = parser.get(self.SECTION_HYTERATAK, "group", fallback="Green")
        self.grouprole: str  = parser.get(self.SECTION_HYTERATAK, "role", fallback="Team Member")

        self.forward_to_hosts = []
        if self.forward_to is not None:
            names = self.forward_to.split(',')
            for n in names:
                self.forward_to_hosts.append(n.strip())


    @staticmethod
    def getint_safe(
        parser: configparser.ConfigParser, section: str, key: str, fallback=_UNSET
    ):
        try:
            return parser.getint(section, key, fallback=fallback)
        except ValueError:
            if fallback is _UNSET:
                raise
            return fallback

    def get_incorrect_configurations(self) -> list:
        rtn: list = list()

        generic_error_message: str = (
            "Value might have not been configured and was not obtained in Hytera repeater "
            "configuration process "
        )

        return rtn

    def print_settings(self) -> None:
        self.log_info(
            f"Hytera Repeater is expected to forward to ports"
            f" [{self.gps1_port},{self.gps2_port}] and forwarding packets to {self.forward_to_hosts}",
        )

__author__ = "Kortel <hytera@kortel.systems>"
__copyright__ = "Copyright 2022 Kortel"
__license__ = "Apache License, Version 2.0"
