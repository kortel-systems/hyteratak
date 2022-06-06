#!/usr/bin/env python3
import asyncio
from asyncio import Queue
import datetime

from kaitaistruct import KaitaiStruct

from hyteratak.lib import settings as module_settings
from hyteratak.lib.logging_trait import LoggingTrait

from hyteratak.kaitai.hytera_simple_transport_reliability_protocol import HyteraSimpleTransportReliabilityProtocol
from hyteratak.kaitai.hytera_dmr_application_protocol import HyteraDmrApplicationProtocol
from hyteratak.kaitai.radio_registration_service import RadioRegistrationService
from hyteratak.kaitai.location_protocol import LocationProtocol

import pytak
import urllib
import xml.etree.ElementTree

class HyteraTakTranslator(pytak.MessageWorker, LoggingTrait):

    """HYTERA Cursor-on-Target Worker Class."""

    def __init__(self,
        hytera_to_tak_queue: asyncio.Queue,
        settings: module_settings.BridgeSettings,
    ) -> None:
        LoggingTrait.__init__(self)
        self.log_info("Starting Hytera->TAK bridge")

        self.hytera_to_tak_queue = hytera_to_tak_queue
        self.tak_in_queue: asyncio.Queue = asyncio.Queue()
        self.tak_out_queue: asyncio.Queue = asyncio.Queue()

        pytak.MessageWorker.__init__(self, self.tak_in_queue)
        self.settings = settings
        self.config = settings.parser

        self.cot_url: urllib.parse.ParseResult = urllib.parse.urlparse(
            self.settings.url)

        self.cot_type = self.settings.cot_type
        self.cot_stale = self.settings.cot_stale

        self.groupname = self.settings.groupname
        self.grouprole = self.settings.grouprole

    async def translate_from_hytera(self):
        loop = asyncio.get_running_loop()
        while loop.is_running():
            try:
                packet: KaitaiStruct = await self.hytera_to_tak_queue.get()
            except RuntimeError as e:
                self.log_error("HYTERA->TAK Could not get Hytera packet from queue")
                self.log_exception(e)
                continue
            except BaseException as e:
                self.log_error("HYTERA->TAK unhandled exception getting Hytera packet from queue")
                self.log_exception(e)
                continue

            try:
                cot_str = self.hytera_to_cot(packet)
                if not cot_str:
                    self.log_warning(f"Empty CoT Event for HYTERA Frame: '{packet}'", )
                    continue

                await self._put_event_queue(cot_str)
            except BaseException as e:
                self.log_error("HYTERA->TAK creating CoT unhandled exception")
                self.log_exception(e)
                continue

            self.hytera_to_tak_queue.task_done()

    async def run(self):
        self.log_info(f"Running Hytera->TAK bridge using TAK server: {self.settings.url}")

        reader = None
        writer = None

        if self.cot_url.scheme.lower() in ["broadcast"]:
            writer = await pytak.udp_client(self.cot_url)
        else:
            reader, writer = await pytak.protocol_factory(self.cot_url)

        write_worker = pytak.EventTransmitter(self.tak_in_queue, writer)
        read_worker = pytak.EventReceiver(self.tak_out_queue, reader)

        await self.tak_in_queue.put(pytak.hello_event("hyteratak"))

        done, _ = await asyncio.wait(
            {self.translate_from_hytera(), read_worker.run(), write_worker.run()},
            return_when=asyncio.FIRST_COMPLETED)

        for task in done:
            self.log_info(f"Task completed: {task}")

    @staticmethod
    def getb2s(package: dict, name: str):
        b = getattr(package, name, None)
        if not b:
            return None
        return b.decode(errors='ignore')

    @staticmethod
    def ddmm2deg(hemi, ddmm):
        brk = max(ddmm.find(b".") - 2, 0)
        degrees = ddmm[:brk]
        minutes = ddmm[brk:]
        latlong = int(degrees) + float(minutes) / 60
        if hemi in b"WS":
            latlong *= -1
        return latlong

    def hytera_to_cot_xml(self, packet) -> \
            [xml.etree.ElementTree, None]:  # NOQA pylint: disable=too-many-locals,too-many-statements
        """Converts an HYTERA Frame to a Cursor-on-Target Event."""

        data = None
        gpsdata = None
        if isinstance(packet, HyteraSimpleTransportReliabilityProtocol):
            packet = packet.data[0]

        if isinstance(packet, HyteraDmrApplicationProtocol):
            packet = packet.data

        if isinstance(packet, LocationProtocol):
            data = packet.data
            gpsdata = data.gpsdata

        if not data:
            return None

        if gpsdata:
            gps_status = gpsdata.gps_status
            if not gps_status or gps_status != b'A':
                gpsdata = None
            else:
                lat = HyteraTakTranslator.ddmm2deg(gpsdata.north_south, gpsdata.latitude)
                lon = HyteraTakTranslator.ddmm2deg(gpsdata.east_west, gpsdata.longitude)
                speed = HyteraTakTranslator.getb2s(gpsdata, "speed")
                direction = HyteraTakTranslator.getb2s(gpsdata, "direction")

        time = datetime.datetime.now(datetime.timezone.utc)
        radioid = str(data.radio_ip.radio_id)
        callsign = f"{radioid} (HYTERA)"
        name = callsign
        cot_type = self.cot_type
        _cot_stale = self.cot_stale
        groupname = self.groupname
        grouprole = self.grouprole

        eventuid = f"HYTERA.{radioid}".replace(" ", "")
        if radioid in self.config:
            cs_conf = self.config[radioid]
            cot_type = cs_conf.get("type", self.cot_type)
            _cot_stale = cs_conf.get("stale", self.cot_stale)
            eventuid = cs_conf.get("uid", eventuid)
            name = cs_conf.get("name", name)
            groupname = cs_conf.get("group", self.groupname)
            grouprole = cs_conf.get("role", self.grouprole)
            cot_icon = cs_conf.get("icon")

        cot_stale = (datetime.datetime.now(datetime.timezone.utc) +
                     datetime.timedelta(
                         seconds=int(_cot_stale))).strftime(pytak.ISO_8601_UTC)
        pointel = None
        how = "h-e"
        if gpsdata:
            how = "m-g"
            pointel = xml.etree.ElementTree.Element("point")
            pointel.set("lat", str(lat))
            pointel.set("lon", str(lon))

            pointel.set("ce", "9999999.0")
            pointel.set("le", "9999999.0")
            pointel.set("hae", "9999999.0")

            trackel = xml.etree.ElementTree.Element("track")
            trackel.set("course", direction)
            trackel.set("speed", speed)

            locel = xml.etree.ElementTree.Element("precisionlocation")
            locel.set("altsrc", "GPS")
            locel.set("geopointsrc", "GPS")
        else:
            how = "h-e"
            pointel = None

        uidel = xml.etree.ElementTree.Element("uid")
        uidel.set("Droid", name)

        contactel = xml.etree.ElementTree.Element("contact")
        contactel.set("callsign", name)
        contactel.set("endpoint", "*:-1:stcp")

        groupel = xml.etree.ElementTree.Element("__group")
        groupel.set("role", grouprole)
        groupel.set("name", groupname)

        detailel = xml.etree.ElementTree.Element("detail")
        detailel.append(contactel)
        detailel.append(uidel)
        if pointel is not None:
            detailel.append(locel)
            detailel.append(trackel)
        detailel.append(groupel)

        remarksel = xml.etree.ElementTree.Element("remarks")

        root = xml.etree.ElementTree.Element("event")
        root.set("version", "2.0")
        root.set("type", cot_type)
        root.set("uid", eventuid)
        root.set("how", how)
        root.set("time", time.strftime(pytak.ISO_8601_UTC))
        root.set("start", time.strftime(pytak.ISO_8601_UTC))
        root.set("stale", cot_stale)
        if pointel is not None:
            root.append(pointel)
        root.append(detailel)

        return root


    def hytera_to_cot(self, packet) -> str:
        """
        Converts an HYTERA Packet to a Cursor-on-Target Event, as a String.
        """
        cot_str: str = ""
        cot_xml: xml.etree.ElementTree = self.hytera_to_cot_xml(packet)
        if cot_xml:
            cot_str = xml.etree.ElementTree.tostring(cot_xml)
        return cot_str

__author__ = "Kortel <hytera@kortel.systems>"
__copyright__ = "Copyright 2022 Kortel"
__license__ = "Apache License, Version 2.0"
