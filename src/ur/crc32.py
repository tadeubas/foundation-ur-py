#
# crc32.py
#
# Copyright © 2020 Foundation Devices, Inc.
# Licensed under the "BSD-2-Clause Plus Patent License"
#
import binascii
from .constants import MAX_UINT32


# STAY
def crc32(buf):
    return binascii.crc32(buf) & MAX_UINT32
