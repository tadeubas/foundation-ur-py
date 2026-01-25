#
# Copyright © 2020 Foundation Devices, Inc. and Contributors
# Licensed under the "BSD-2-Clause Plus Patent License"
#

from array import array
from . import (
    BYTEWORDS,
)
from ..crc32 import crc32

ORD_A = 65  # 'A'. Was 97 = 'a'
CASE_MASK = ~0x20  # 0xDF = uppercase_mask. Was | 0x20 = lowercase mask


class BytewordsDecoder:
    _WORD_ARRAY = None
    _DIM = 26

    @classmethod
    def _ensure_word_array(cls):
        """Lazily initialize the fast lookup table.
        Since the first and last letters of each Byteword are unique,
        we can use them as indexes into a two-dimensional lookup table"""

        if cls._WORD_ARRAY is not None:
            return

        w_array = array("h", [-1] * (cls._DIM * cls._DIM))

        for i in range(256):
            offset = i << 2  # * 4
            x = BYTEWORDS[offset] - ORD_A  # ord("a") == ORD_A
            y = BYTEWORDS[offset + 3] - ORD_A
            w_array[y * cls._DIM + x] = i

        cls._WORD_ARRAY = w_array

    @classmethod
    def _decode_word(cls, buf, pos, word_len):

        cls._ensure_word_array()

        b0 = buf[pos] & CASE_MASK  # = uppercase. Was | 0x20 = lowercase
        x = b0 - ORD_A
        y_idx = pos + (3 if word_len == 4 else 1)
        b1 = buf[y_idx] & CASE_MASK
        y = b1 - ORD_A

        if not (0 <= x < cls._DIM and 0 <= y < cls._DIM):
            raise ValueError("Invalid Bytewords characters")

        value = cls._WORD_ARRAY[y * cls._DIM + x]

        if value == -1:
            raise ValueError("Unknown Bytewords word")

        # minimal lib using only STYLE_MINIMAL (word_len == 2)
        # if word_len == 4:
        #     expected_offset = value << 2  # * 4
        #     if (buf[pos + 1] & CASE_MASK) != BYTEWORDS[expected_offset + 1] or (
        #         buf[pos + 2] & CASE_MASK
        #     ) != BYTEWORDS[expected_offset + 2]:
        #         raise ValueError("Bytewords word mismatch")

        return value

    @classmethod
    def decode(cls, text):
        """
        Decode Bytewords string according to selected style
        """
        if isinstance(text, str):
            text = text.encode()
        word_len = 4
        buf = bytearray()
        word_len = 2
        for i in range(0, len(text), word_len):
            buf.append(cls._decode_word(text, i, word_len))

        if len(buf) < 5:
            raise ValueError("Bytewords too short")

        # Checksum validation
        body = buf[:-4]
        checksum_bytes = buf[-4:]
        computed = crc32(body).to_bytes(4, "big")

        if computed != checksum_bytes:
            raise ValueError("Bytewords checksum mismatch")

        return body
