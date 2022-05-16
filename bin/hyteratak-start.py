#!/usr/bin/env python3
import asyncio
import importlib.util
import logging.config
import os
import socket
import sys
from asyncio import AbstractEventLoop, Queue
from signal import SIGINT, SIGTERM
from typing import Optional


class HyteraTakBridge:
    def __init__(self, filepath: str = None, filedata: str = None):
        self.loop: Optional[AbstractEventLoop] = None
        self.settings: BridgeSettings = BridgeSettings(filepath=filepath, filedata=filedata)
        self.hytera_to_tak_queue: Queue = Queue()
        self.hytera_ports = []
        self.hytera_ports.append(HyteraHSTRProtocol(
            name='gps1', port=self.settings.gps1_port, hytera_to_tak_queue = self.hytera_to_tak_queue, settings=self.settings
        ))
        self.hytera_ports.append(HyteraHSTRProtocol(
            name='gps2', port=self.settings.gps2_port, hytera_to_tak_queue = self.hytera_to_tak_queue, settings=self.settings
        ))
        self.hytera_translator: HyteraTakTranslator = HyteraTakTranslator(
            hytera_to_tak_queue=self.hytera_to_tak_queue, settings=self.settings
        )

    async def go(self) -> None:
        self.loop = asyncio.get_running_loop()
        self.settings.print_settings()

        await self.hytera_hstr_connect()
        await self.hytera_translator.run()

    async def hytera_hstr_connect(self) -> None:
        for p in self.hytera_ports:
            await self.loop.create_datagram_endpoint(
                lambda: p,
                local_addr=(self.settings.ip, p.port),
            )

    def stop_running(self) -> None:
        for p in self.hytera_ports:
            p.disconnect()

        self.loop.stop()
        for task in asyncio.all_tasks():
            task.cancel()
            task.done()


if __name__ == "__main__":
    loggerConfigured: bool = False
    if len(sys.argv) > 2:
        if os.path.isfile(sys.argv[2]):
            logging.config.fileConfig(sys.argv[2])
            loggerConfigured = True
    if not loggerConfigured:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(levelname)s - %(asctime)s - %(name)s - %(message)s",
        )

    mainlog = logging.getLogger("hyteratak-start.py")

    mainlog.info("Hytera Tak Bridge")
    mainlog.info("This project is experimental, use at your own risk\n")

    settings_ini_path = None
    settings_ini_data = None
    if len(sys.argv) < 2:
        mainlog.info(
            'Using simple default settings\nUse as hyteratak-start <path to settings.ini> <optionally path to logger.ini>\nIf you do not have the settings.ini file, you can obtain one here:\ncurl "https://raw.githubusercontent.com/kortel-systems/hyteratak/master/settings.ini.example" -o settings.ini'
        )
        settings_ini_data = "[hyteratak]"
    else:
        settings_ini_path = sys.argv[1]

    self_name: str = "hyteratak"
    self_spec = importlib.util.find_spec(self_name)
    if self_spec is None:
        mainlog.debug(f"Package {self_name} is not installed, trying locally\n")
        parent_folder: str = os.path.dirname(
            os.path.dirname(os.path.realpath(__file__))
        )
        expected_folder: str = f"{parent_folder}{os.path.sep}"
        if os.path.isdir(expected_folder):
            sys.path.append(expected_folder)

    from hyteratak.lib.settings import BridgeSettings
    from hyteratak.lib.hytera_protocols import HyteraHSTRProtocol
    from hyteratak.lib.hytera_tak_translator import HyteraTakTranslator

    uvloop_spec = importlib.util.find_spec("uvloop")
    if uvloop_spec:
        import uvloop
        uvloop.install()

    loop = asyncio.get_event_loop()
    bridge: HyteraTakBridge = HyteraTakBridge(filepath = settings_ini_path, filedata = settings_ini_data)
    if os.name != "nt":
        for signal in [SIGINT, SIGTERM]:
            loop.add_signal_handler(signal, bridge.stop_running)

    try:
        loop.run_until_complete(bridge.go())
        loop.run_forever()
    except BaseException as e:
        mainlog.exception(e)
    finally:
        mainlog.info("Hytera Tak Bridge Ended")

__author__ = "Kortel <info@kortel.systems>"
__copyright__ = "Copyright 2022 Kortel"
__license__ = "Apache License, Version 2.0"
