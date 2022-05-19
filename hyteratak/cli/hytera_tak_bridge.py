import asyncio
from asyncio import AbstractEventLoop, Queue
from typing import Optional

from hyteratak.lib.settings import BridgeSettings
from hyteratak.lib.hytera_protocols import HyteraHSTRProtocol
from hyteratak.lib.hytera_tak_translator import HyteraTakTranslator

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

__author__ = "Kortel <hytera@kortel.systems>"
__copyright__ = "Copyright 2022 Kortel"
__license__ = "Apache License, Version 2.0"
