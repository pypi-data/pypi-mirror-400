"""Provides classes for general GetStimStatus"""

from typing import NamedTuple
from science_mode_4.protocol.commands import Commands
from science_mode_4.protocol.packet import Packet, PacketAck
from science_mode_4.protocol.types import StimStatus

class GetStimStatusResult(NamedTuple):
    """Helper class for stim result"""
    stim_status: StimStatus
    high_voltage_on: bool


class PacketGeneralGetStimStatus(Packet):
    """Packet for general GetStimStatus"""


    def __init__(self):
        super().__init__()
        self._command = Commands.GET_STIM_STATUS


class PacketGeneralGetStimStatusAck(PacketAck):
    """Packet for general GetStimStatus akcnowledge"""


    def __init__(self, data: bytes):
        super().__init__(data)
        self._command = Commands.GET_STIM_STATUS_ACK
        self._successful: bool = False
        self._stim_status = StimStatus.NO_LEVEL_INITIALIZED
        self._high_voltage_on: bool = False

        if not data is None:
            self._successful = data[0] == 0
            self._stim_status = StimStatus(data[1])
            self._high_voltage_on = data[2] == 6


    @property
    def successful(self) -> bool:
        """Getter for Successful"""
        return self._successful


    @property
    def stim_status(self) -> StimStatus:
        """Getter for StimStatus"""
        return self._stim_status


    @property
    def high_voltage_on(self) -> bool:
        """Getter for HighVoltageOn"""
        return self._high_voltage_on
