"""Provides device class representing a science mode device"""

from enum import IntEnum
from typing import Type

from .layer import Layer
from .protocol.types import StimStatus
from .protocol.packet_factory import PacketFactory
from .protocol.packet_number_generator import PacketNumberGenerator
from .general.general_layer import LayerGeneral
from .low_level.low_level_layer import LayerLowLevel
from .mid_level.mid_level_layer import LayerMidLevel
from .dyscom.dyscom_layer import LayerDyscom
from .dyscom.dyscom_types import DyscomGetOperationModeType
from .utils.connection import Connection
from .utils.packet_buffer import PacketBuffer


class DeviceCapability(IntEnum):
    """Represent device capabilities"""
    GENERAL = 0
    LOW_LEVEL = 1
    MID_LEVEL = 2
    DYSCOM = 3


class Device():
    """Base class for a science mode devices"""


    def __init__(self, conn: Connection, capabilities: set[DeviceCapability]):
        self._connection  = conn
        self._packet_factory = PacketFactory()
        self._packet_buffer = PacketBuffer(self._connection, self._packet_factory)
        self._packet_number_generator = PacketNumberGenerator()
        self._capabilities = capabilities
        self._layer: dict[DeviceCapability, Layer] = {}

        self._add_layer(DeviceCapability.GENERAL, capabilities, LayerGeneral)
        self._add_layer(DeviceCapability.LOW_LEVEL, capabilities, LayerLowLevel)
        self._add_layer(DeviceCapability.MID_LEVEL, capabilities, LayerMidLevel)
        self._add_layer(DeviceCapability.DYSCOM, capabilities, LayerDyscom)


    @property
    def connection(self) -> Connection:
        """Getter for connection"""
        return self._connection


    @property
    def packet_factory(self) -> PacketFactory:
        """Getter for packet factory"""
        return self._packet_factory


    @property
    def packet_buffer(self) -> PacketBuffer:
        """Getter for packet buffer"""
        return self._packet_buffer


    @property
    def packet_number_generator(self) -> PacketNumberGenerator:
        """Getter for packet number generator"""
        return self._capabilities


    @property
    def capabilities(self) -> set[DeviceCapability]:
        """Getter for capabilities"""
        return self._capabilities


    async def initialize(self):
        """Initialize device to get basic information (serial, versions) and stop any active stimulation/measurement"""
        if {DeviceCapability.LOW_LEVEL, DeviceCapability.MID_LEVEL}.issubset(self._capabilities):
            # get stim status to see if low/mid level is initialized or running
            stim_status = await self.get_layer_general().get_stim_status()
            if stim_status.stim_status == StimStatus.LOW_LEVEL_INITIALIZED:
                await self.get_layer_low_level().stop()
            elif stim_status.stim_status in [StimStatus.MID_LEVEL_INITIALIZED, StimStatus.MID_LEVEL_RUNNING]:
                await self.get_layer_mid_level().stop()
        if DeviceCapability.DYSCOM in self._capabilities:
            # get operation mode to see if dyscom measurement is running
            operation_mode = await self.get_layer_dyscom().get_operation_mode()
            if operation_mode in [DyscomGetOperationModeType.UNDEFINED,
                                  DyscomGetOperationModeType.LIVE_MEASURING_PRE,
                                  DyscomGetOperationModeType.LIVE_MEASURING,
                                  DyscomGetOperationModeType.RECORD_PRE,
                                  DyscomGetOperationModeType.RECORD,
                                  DyscomGetOperationModeType.DATATRANSFER_PRE,
                                  DyscomGetOperationModeType.DATATRANSFER]:
                await self.get_layer_dyscom().stop()

        await self.get_layer_general().initialize()


    def get_layer_general(self) -> LayerGeneral:
        """Helper function to access general layer"""
        return self._layer[DeviceCapability.GENERAL]


    def get_layer_mid_level(self) -> LayerMidLevel:
        """Helper function to access mid level layer"""
        return self._layer[DeviceCapability.MID_LEVEL]


    def get_layer_low_level(self) -> LayerLowLevel:
        """Helper function to access low level layer"""
        return self._layer[DeviceCapability.LOW_LEVEL]


    def get_layer_dyscom(self) -> LayerDyscom:
        """Helper function to access dyscom layer"""
        return self._layer[DeviceCapability.DYSCOM]


    def add_layer(self, capability: DeviceCapability, layer: Layer):
        """Add layer"""
        self._layer[capability] = layer


    def _add_layer(self, capability: DeviceCapability, used_capabilities: set[DeviceCapability], layer_class: Type[Layer]):
        """Helper method that checks if capability is in used_capabilities and if yes add a layer_class instance"""
        if capability in used_capabilities:
            self.add_layer(capability, layer_class(self._packet_buffer, self._packet_factory, self._packet_number_generator))
