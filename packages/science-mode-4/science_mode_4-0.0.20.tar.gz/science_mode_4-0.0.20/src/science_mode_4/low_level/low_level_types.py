"""Provides low level types"""

from enum import IntEnum


class LowLevelMode(IntEnum):
    """Represent low level type for measurement"""
    NO_MEASUREMENT = 0
    STIM_CURRENT = 1
    STIM_VOLTAGE = 2
    HIGH_VOLTAGE_SOURCE = 3


class LowLevelHighVoltageSource(IntEnum):
    """Represent low level high voltage source"""
    STANDARD = 0
    OFF = 1
