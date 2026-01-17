#
# Copyright © 2020 Foundation Devices, Inc. and Contributors
# Licensed under the "BSD-2-Clause Plus Patent License"
#

from array import array
from . import (
    # STYLE_STANDARD,
    # STYLE_URI,
    # STYLE_MINIMAL,
    BYTEWORDS,
)
from ..crc32 import crc32


class BytewordsDecoder:
    _WORD_ARRAY = None
    _DIM = 26

    # STAY
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
            x = BYTEWORDS[offset] - 97  # ord("a") == 97
            y = BYTEWORDS[offset + 3] - 97
            w_array[y * cls._DIM + x] = i

        cls._WORD_ARRAY = w_array

    # STAY
    @classmethod
    def _decode_word(cls, buf, pos, word_len):
        # if len(word_b) != word_len:
        #     raise ValueError("Invalid Bytewords length")

        cls._ensure_word_array()

        b0 = buf[pos] | 0x20
        x = b0 - 97
        y_idx = pos + (3 if word_len == 4 else 1)
        b1 = buf[y_idx] | 0x20
        y = b1 - 97

        if not (0 <= x < cls._DIM and 0 <= y < cls._DIM):
            raise ValueError("Invalid Bytewords characters")

        value = cls._WORD_ARRAY[y * cls._DIM + x]

        if value == -1:
            raise ValueError("Unknown Bytewords word")

        if word_len == 4:
            expected_offset = value << 2  # * 4
            if (buf[pos + 1] | 0x20) != BYTEWORDS[expected_offset + 1] or (
                buf[pos + 2] | 0x20
            ) != BYTEWORDS[expected_offset + 2]:
                raise ValueError("Bytewords word mismatch")

        return value

    # STAY
    @classmethod
    def decode(cls, _style, text):
        """
        Decode Bytewords string according to selected style
        """
        if isinstance(text, str):
            text = text.encode()
        word_len = 4
        buf = bytearray()
        # if _style in (STYLE_STANDARD, STYLE_URI):
        #     sep = " " if style == STYLE_STANDARD else "-"
        #     i = 0
        #     n = len(text)

        #     while i < n:
        #         j = text.find(sep, i)
        #         if j < 0:
        #             j = n

        #         buf.append(cls._decode_word(text[i:j], word_len))
        #         i = j + 1
        # elif _style == STYLE_MINIMAL:
        word_len = 2
        for i in range(0, len(text), word_len):
            buf.append(cls._decode_word(text, i, word_len))
        # else:
        #     raise ValueError("Unknown Bytewords style: " + style)

        if len(buf) < 5:
            raise ValueError("Bytewords too short")

        # Checksum validation
        body = buf[:-4]
        checksum_bytes = buf[-4:]
        computed = crc32(body).to_bytes(4, "big")

        if computed != checksum_bytes:
            raise ValueError("Bytewords checksum mismatch")

        return body
