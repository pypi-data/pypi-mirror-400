"""Provides packet classes for low level init"""

from science_mode_4.protocol.commands import Commands
from science_mode_4.protocol.types import ResultAndError
from science_mode_4.protocol.packet import Packet, PacketAck
from science_mode_4.utils.byte_builder import ByteBuilder
from .low_level_types import LowLevelHighVoltageSource, LowLevelMode


class PacketLowLevelInit(Packet):
    """Packet for low level init"""


    def __init__(self):
        super().__init__()
        self._command = Commands.LOW_LEVEL_INIT
        self._mode = LowLevelMode.NO_MEASUREMENT
        self._high_voltage_source = LowLevelHighVoltageSource.STANDARD


    @property
    def mode(self) -> LowLevelMode:
        """Getter for mode"""
        return self._mode


    @mode.setter
    def mode(self, value: LowLevelMode):
        """Setter for mode"""
        self._mode = value


    @property
    def high_voltage_source(self) -> int:
        """Getter for high voltage source"""
        return self._high_voltage_source


    @high_voltage_source.setter
    def high_voltage_source(self, value: int):
        """Setter for high voltage source"""
        self._high_voltage_source = value


    def get_data(self) -> bytes:
        bb = ByteBuilder()
        bb.set_bit_to_position(0, 0, 1)
        bb.set_bit_to_position(self._high_voltage_source, 1, 3)
        bb.set_bit_to_position(self._mode, 4, 3)
        bb.set_bit_to_position(0, 7, 0)
        return bb.get_bytes()


class PacketLowLevelInitAck(PacketAck):
    """Packet for low level init acknowledge"""


    def __init__(self, data: bytes):
        super().__init__(data)
        self._command = Commands.LOW_LEVEL_INIT_ACK
        self._result_error = ResultAndError.NO_ERROR

        if not data is None:
            self._result_error = ResultAndError(data[0])


    @property
    def result_error(self) -> ResultAndError:
        """Getter for ResultError"""
        return self._result_error
