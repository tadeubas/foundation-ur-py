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
from ..utils import crc32_bytes, partition


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
            x = ord(BYTEWORDS[offset]) - ord("a")
            y = ord(BYTEWORDS[offset + 3]) - ord("a")
            array[y * cls._DIM + x] = i

        cls._WORD_ARRAY = array

    @classmethod
    def _decode_word(cls, word: str, word_len: int):
        if len(word) != word_len:
            raise ValueError("Invalid Bytewords length")

        cls._ensure_word_array()

        x = ord(word[0].lower()) - ord("a")
        y_idx = 3 if word_len == 4 else 1
        y = ord(word[y_idx].lower()) - ord("a")

        if not (0 <= x < cls._DIM and 0 <= y < cls._DIM):
            raise ValueError("Invalid Bytewords characters")

        offset = y * cls._DIM + x
        value = cls._WORD_ARRAY[offset]

        if value == -1:
            raise ValueError("Unknown Bytewords word")

        # Full word validation (middle characters)
        if word_len == 4:
            expected_offset = value * 4
            if (
                word[1].lower() != BYTEWORDS[expected_offset + 1]
                or word[2].lower() != BYTEWORDS[expected_offset + 2]
            ):
                raise ValueError("Bytewords word mismatch")

        return value

    @classmethod
    def decode(cls, style: int, text: str):
        """
        Decode Bytewords string according to selected style
        """
        word_len = 4
        if style == STYLE_STANDARD:
            words = text.split(" ")
        elif style == STYLE_URI:
            words = text.split("-")
        elif style == STYLE_MINIMAL:
            words = partition(text, 2)
            word_len = 2
        else:
            raise ValueError("Unknown Bytewords style: " + style)

        buf = bytearray()

        for word in words:
            buf.append(cls._decode_word(word, word_len))

        if len(buf) < 5:
            raise ValueError("Bytewords too short")

        # Checksum validation
        body = buf[:-4]
        checksum_bytes = buf[-4:]
        computed = crc32_bytes(body)

        if computed != checksum_bytes:
            raise ValueError("Bytewords checksum mismatch")

        return body
