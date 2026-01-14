"""Provides packet classes for dyscom power module"""

from typing import NamedTuple
from science_mode_4.protocol.commands import Commands
from science_mode_4.protocol.types import ResultAndError
from science_mode_4.protocol.packet import Packet, PacketAck
from science_mode_4.utils.byte_builder import ByteBuilder
from .dyscom_types import DyscomPowerModuleType, DyscomPowerModulePowerType


class DyscomPowerModuleResult(NamedTuple):
    """Helper class for dyscom power module result"""
    module: DyscomPowerModuleType
    power: DyscomPowerModulePowerType


class PacketDyscomPowerModule(Packet):
    """Packet for dyscom power module"""


    def __init__(self, module: DyscomPowerModuleType = DyscomPowerModuleType.MEASUREMENT, power = DyscomPowerModulePowerType.SWITCH_OFF):
        super().__init__()
        self._command = Commands.DL_POWER_MODULE
        self._module = module
        self._power = power


    def get_data(self) -> bytes:
        bb = ByteBuilder()
        bb.append_byte(self._module)
        bb.append_byte(self._power)
        return bb.get_bytes()


class PacketDyscomPowerModuleAck(PacketAck):
    """Packet for dyscom power module"""


    def __init__(self, data: bytes):
        super().__init__(data)
        self._command = Commands.DL_POWER_MODULE_ACK
        self._result_error = ResultAndError.NO_ERROR
        self._module = DyscomPowerModuleType.MEASUREMENT
        self._power = DyscomPowerModulePowerType.SWITCH_OFF

        if not data is None:
            self._result_error = ResultAndError(data[0])
            self._module = DyscomPowerModuleType(data[1])
            self._power = DyscomPowerModulePowerType(data[2])


    @property
    def result_error(self) -> ResultAndError:
        """Getter for ResultError"""
        return self._result_error


    @property
    def module(self) -> DyscomPowerModuleType:
        """Getter for module"""
        return self._module


    @property
    def power(self) -> DyscomPowerModulePowerType:
        """Getter for power"""
        return self._power
