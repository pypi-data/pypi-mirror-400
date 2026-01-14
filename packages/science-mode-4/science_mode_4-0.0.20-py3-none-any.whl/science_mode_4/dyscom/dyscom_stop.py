"""Provides packet classes for dyscom stop"""

from science_mode_4.protocol.commands import Commands
from science_mode_4.protocol.types import ResultAndError
from science_mode_4.protocol.packet import Packet, PacketAck


class PacketDyscomStop(Packet):
    """Packet for dyscom stop"""


    def __init__(self):
        super().__init__()
        self._command = Commands.DL_STOP


class PacketDyscomStopAck(PacketAck):
    """Packet for dyscom stop acknowledge"""


    def __init__(self, data: bytes):
        super().__init__(data)
        self._command = Commands.DL_STOP_ACK
        self._result_error = ResultAndError.NO_ERROR

        if not data is None:
            self._result_error = ResultAndError(data[0])


    @property
    def result_error(self) -> ResultAndError:
        """Getter for ResultError"""
        return self._result_error
