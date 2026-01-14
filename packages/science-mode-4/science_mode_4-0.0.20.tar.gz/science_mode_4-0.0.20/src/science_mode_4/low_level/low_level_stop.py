"""Provides packet classes for low level stop"""

from science_mode_4.protocol.commands import Commands
from science_mode_4.protocol.packet import Packet, PacketAck
from science_mode_4.protocol.types import ResultAndError


class PacketLowLevelStop(Packet):
    """Packet for low level stop"""


    def __init__(self):
        super().__init__()
        self._command = Commands.LOW_LEVEL_STOP


class PacketLowLevelStopAck(PacketAck):
    """Packet for low level stop acknowledge"""


    def __init__(self, data: bytes):
        super().__init__(data)
        self._command = Commands.LOW_LEVEL_STOP_ACK
        self._result_error = ResultAndError.NO_ERROR

        if not data is None:
            self._result_error = ResultAndError(data[0])


    @property
    def result_error(self) -> ResultAndError:
        """Getter for ResultError"""
        return self._result_error
