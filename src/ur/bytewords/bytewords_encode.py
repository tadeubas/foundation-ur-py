#
# Copyright © 2020 Foundation Devices, Inc. and Contributors
# Licensed under the "BSD-2-Clause Plus Patent License"
#

from . import (
    STYLE_STANDARD,
    STYLE_URI,
    STYLE_MINIMAL,
    BYTEWORDS,
)
from ..crc32 import crc32


class BytewordsEncoder:
    @classmethod
    def _get_full_word(cls, index):
        """Get the 4-letter Byteword for a given byte value (0–255)"""
        offset = index * 4
        return BYTEWORDS[offset : offset + 4]

    @classmethod
    def _encode_words(cls, buf, b_separator):
        """Join full 4-letter words with the given b_separator"""
        sep_len = len(b_separator)
        out = bytearray(len(buf) * (4 + sep_len) - sep_len)
        pos = 0

        first = True
        for byte in buf:
            if not first:
                out[pos : pos + sep_len] = b_separator
                pos += sep_len
            first = False
            word = cls._get_full_word(byte)
            out[pos : pos + 4] = word
            pos += 4

        return out.decode()

    @classmethod
    def _encode_minimal(cls, buf):
        """Concatenate 2-character minimal words without separator"""
        out = bytearray(len(buf) * 2)
        pos = 0

        for byte in buf:
            offset = byte * 4
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
    def encode(cls, style, data):
        """
        Encode bytes into Bytewords string using the specified style
        """

        # Add checksum to data
        payload_with_crc = cls._add_checksum(data)

        if style == STYLE_STANDARD:
            return cls._encode_words(payload_with_crc, b" ")
        if style == STYLE_URI:
            return cls._encode_words(payload_with_crc, b"-")
        if style == STYLE_MINIMAL:
            return cls._encode_minimal(payload_with_crc)

        raise ValueError("Unknown Bytewords style: " + style)
