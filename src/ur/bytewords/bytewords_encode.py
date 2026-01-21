#
# Copyright © 2020 Foundation Devices, Inc. and Contributors
# Licensed under the "BSD-2-Clause Plus Patent License"
#

from . import (
    BYTEWORDS,
)
from ..crc32 import crc32


class BytewordsEncoder:
    @classmethod
    def _encode_minimal(cls, buf):
        """Concatenate 2-character minimal words without separator"""
        out = bytearray(len(buf) << 1)  # * 2
        pos = 0

        for byte in buf:
            offset = byte << 2  # * 4
            out[pos] = BYTEWORDS[offset]
            out[pos + 1] = BYTEWORDS[offset + 3]
            pos += 2

        return out.decode()

    @classmethod
    def _add_checksum(cls, data):
        """Append 4-byte CRC32 checksum"""
        out = bytearray(data)
        out.extend(crc32(out).to_bytes(4, "big"))
        return out

    @classmethod
    def encode(cls, data):
        """
        Encode bytes into Bytewords string using the specified style
        """

        # Add checksum to data
        payload_with_crc = cls._add_checksum(data)

        return cls._encode_minimal(payload_with_crc)
