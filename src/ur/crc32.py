#
# crc32.py
#
# Copyright © 2020 Foundation Devices, Inc.
# Licensed under the "BSD-2-Clause Plus Patent License"
#
import binascii
from .constants import MAX_UINT32


def crc32(buf, prev=0):
    return binascii.crc32(buf, prev) & MAX_UINT32
