"""Provides general types"""

from enum import IntEnum


class GeneralHashType(IntEnum):
    """Represent general hash type"""
    UNINITIALIZED = 0
    GIT = 1
    ELF_MD5 = 2
    ELF_SHA256 = 3
