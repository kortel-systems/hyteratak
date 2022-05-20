#!/usr/bin/env python3
import asyncio
from asyncio import transports, Queue
from binascii import hexlify
from typing import Optional, Tuple, Coroutine

from kaitaistruct import ValidationNotEqualError

from hyteratak.lib.custom_bridge_datagram_protocol import CustomBridgeDatagramProtocol
from hyteratak.lib.settings import BridgeSettings
from hyteratak.kaitai.hytera_simple_transport_reliability_protocol import HyteraSimpleTransportReliabilityProtocol

class HyteraHSTRProtocol(CustomBridgeDatagramProtocol):
    HSTRP_PREFIX: bytes = bytes([0x32, 0x42])

    def __init__(self, name: str, port: int, hytera_to_tak_queue: Queue, settings: BridgeSettings):
        super().__init__(settings=settings, name=name, port=port)
        self.hytera_to_tak_queue = hytera_to_tak_queue
        self.transport: Optional[transports.DatagramTransport] = None

    @staticmethod
    def packet_is_hstrp(data: bytes) -> bool:
        return data[:2] == HyteraHSTRProtocol.HSTRP_PREFIX

    def datagram_received(self, data: bytes, address: Tuple[str, int]) -> None:
        super().datagram_received(data=data, address=address)
        try:
            packet = HyteraSimpleTransportReliabilityProtocol.from_bytes(data)
            if packet.is_ack:
                return
            elif packet.is_connect:
                self.handle_connect(data, address)
            elif packet.is_heartbeat:
                self.handle_heartbeat(data, address)
            elif packet.is_close:
                self.log_warning(f"request close {data.hex()}")
            elif packet.is_reject:
                self.log_warning(f"request reject {data.hex()}")
            else:
                try:
                    self.hytera_to_tak_queue.put_nowait(packet.data[0])
                except AttributeError:
                    pass
            self.handle_ack(data, address)
            return
        except EOFError as e:
            self.log_error(f"Cannot parse HSTR packet {hexlify(data)} from {address}")
            self.log_exception(e)
        except ValidationNotEqualError as e:
            self.log_error(f"Cannot parse HSTR packet {hexlify(data)} from {address}")
            self.log_error("Parser for Hytera data failed to match the packet data")
            self.log_exception(e)
        except BaseException as e:
            self.log_error(f"[datagram_received] unhandled exception {hexlify(data)} from {address}")
            self.log_exception(e)
        self.last_chance_handle(data, address)

    def last_chance_handle(self, data: bytes, address: Tuple[str, int]) -> None:
        try:
            if self.packet_is_hstrp(data):
                self.handle_ack(data, address)
        except BaseException as e:
            self.log_error(f"[last_chance_handle] unhandled exception {hexlify(data)} from {address}")
            self.log_exception(e)

    def handle_ack(self, data: bytes, address: Tuple[str, int]) -> None:
        data = bytearray(data)
        data[3] |= 0x01
        self.transport.sendto(data, address)

    def handle_heartbeat(self, data: bytes, address: Tuple[str, int]) -> None:
        pass

    def handle_connect(self, data: bytes, address: Tuple[str, int]) -> None:
        self.log_info("connected")

__author__ = "Kortel <hytera@kortel.systems>"
__copyright__ = "Copyright 2022 Kortel"
__license__ = "Apache License, Version 2.0"
