#
# Copyright © 2020 Foundation Devices, Inc. and Contributors
# Licensed under the "BSD-2-Clause Plus Patent License"
#

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

    @classmethod
    def _ensure_word_array(cls):
        """Lazily initialize the fast lookup table.
        Since the first and last letters of each Byteword are unique,
        we can use them as indexes into a two-dimensional lookup table"""

        if cls._WORD_ARRAY is not None:
            return

        array = [-1] * (cls._DIM * cls._DIM)

        for i in range(256):
            offset = i * 4
            x = BYTEWORDS[offset] - 97  # ord("a") == 97
            y = BYTEWORDS[offset + 3] - 97
            array[y * cls._DIM + x] = i

        cls._WORD_ARRAY = array

    @classmethod
    def _decode_word(cls, word, word_len):
        word_b = word.encode()
        if len(word_b) != word_len:
            raise ValueError("Invalid Bytewords length")

        cls._ensure_word_array()

        x = (word_b[0] | 0x20) - 97
        y_idx = 3 if word_len == 4 else 1
        y = (word_b[y_idx] | 0x20) - 97

        if not (0 <= x < cls._DIM and 0 <= y < cls._DIM):
            raise ValueError("Invalid Bytewords characters")

        value = cls._WORD_ARRAY[y * cls._DIM + x]

        if value == -1:
            raise ValueError("Unknown Bytewords word")

        if word_len == 4:
            expected_offset = value * 4
            if (word_b[1] | 0x20) != BYTEWORDS[expected_offset + 1] or (
                word_b[2] | 0x20
            ) != BYTEWORDS[expected_offset + 2]:
                raise ValueError("Bytewords word mismatch")

        return value

    @classmethod
    def decode(cls, _style, text):
        """
        Decode Bytewords string according to selected style
        """
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
            buf.append(cls._decode_word(text[i : i + 2], word_len))
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
