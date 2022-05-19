#!/usr/bin/env python3
import asyncio
import importlib.util
import logging.config
import os
import sys
from signal import SIGINT, SIGTERM

def cli() -> None:
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

    mainlog = logging.getLogger("hyteratak_start.py")

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
        parent_folder: str = os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.realpath(__file__))
        ))
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

    from hyteratak.cli.hytera_tak_bridge import HyteraTakBridge

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

if __name__ == "__main__":
    cli()

__author__ = "Kortel <hytera@kortel.systems>"
__copyright__ = "Copyright 2022 Kortel"
__license__ = "Apache License, Version 2.0"
