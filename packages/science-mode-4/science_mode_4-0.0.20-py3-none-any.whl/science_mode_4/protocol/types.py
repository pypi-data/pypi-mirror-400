"""Provides common types"""

from enum import IntEnum


class Channel(IntEnum):
    """Represents a channel"""
    RED = 0
    BLUE = 1
    BLACK = 2
    WHITE = 3


class Connector(IntEnum):
    """Represents a cable connector"""
    YELLOW = 0
    GREEN = 1


class ResultAndError(IntEnum):
    """Represents science mode type ResultAndError"""
    NO_ERROR = 0
    TRANSFER_ERROR = 1
    PARAMETER_ERROR = 2
    PROTOCOL_ERROR = 3
    UC_STIM_TIMEOUT_ERROR = 4
    EMG_TIMEOUT_ERROR = 5
    EMG_REGISTER_ERROR = 6
    NOT_INITIALIZED = 7
    HV_ERROR = 8
    DEMUX_TIMEOUT_ERROR = 9
    ELECTRODE_ERROR = 10
    INVALID_CMD_ERROR = 11
    DEMUX_PARAMETER_ERROR = 12
    DEMUX_NOT_INITIALIZED_ERROR = 13
    DEMUX_TRANSFER_ERROR = 14
    DEMUX_UNKNOWN_ACK_ERROR = 15
    PULSE_TIMEOUT_ERROR = 16
    FUEL_GAUGE_ERROR = 17
    LIVE_SIGNAL_ERROR = 18
    FILE_TRANSMISSION_TIMEOUT = 19
    FILE_NOT_FOUND = 20
    BUSY = 21
    FILE_ERROR = 22
    FLASH_ERASE_ERROR = 23
    FLASH_WRITE_ERROR = 24
    UNKNOWN_CONTROLLER_ERROR = 25
    FIRMWARE_TOO_LARGE_ERROR = 26
    FUEL_GAUGE_NOT_PROGRAMMED = 27
    PULSE_LOW_CURRENT_ERROR = 28


class StimStatus(IntEnum):
    """Represents science mode type StimStatus"""
    NO_LEVEL_INITIALIZED = 0
    LOW_LEVEL_INITIALIZED = 1
    MID_LEVEL_INITIALIZED = 2
    MID_LEVEL_RUNNING = 3
