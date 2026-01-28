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
    def encode(cls, data):
        """
        Encode bytes into Bytewords string using the specified style
        """

        # Add checksum to data
        crc = crc32(data)
        out = bytearray((len(data) + 4) * 2)

        pos = 0
        bw = BYTEWORDS

        for b in data:
            o = b << 2
            out[pos] = bw[o]
            out[pos + 1] = bw[o + 3]
            pos += 2

        for b in crc.to_bytes(4, "big"):
            o = b << 2
            out[pos] = bw[o]
            out[pos + 1] = bw[o + 3]
            pos += 2

        return out.decode()
