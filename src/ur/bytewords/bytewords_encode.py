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
from ..utils import crc32_bytes


class BytewordsEncoder:
    @classmethod
    def _get_full_word(cls, index: int) -> str:
        """Get the 4-letter Byteword for a given byte value (0–255)"""
        offset = index * 4
        return BYTEWORDS[offset : offset + 4]

    @classmethod
    def _get_minimal_word(cls, index: int) -> str:
        """Get the 2-character minimal Byteword (first + last letter)"""
        offset = index * 4
        return BYTEWORDS[offset] + BYTEWORDS[offset + 3]

    @classmethod
    def _encode_words(cls, buf: bytes, separator: str) -> str:
        """Join full 4-letter words with the given separator"""
        words = [cls._get_full_word(byte) for byte in buf]
        return separator.join(words)

    @classmethod
    def _encode_minimal(cls, buf: bytes) -> str:
        """Concatenate 2-character minimal words without separator"""
        return "".join(cls._get_minimal_word(byte) for byte in buf)

    @classmethod
    def _add_checksum(cls, data: bytes) -> bytes:
        """Append 4-byte CRC32 checksum"""
        crc = crc32_bytes(data)
        return data + crc

    @classmethod
    def encode(cls, style: int, data: bytes):
        """
        Encode bytes into Bytewords string using the specified style
        """

        # Add checksum to data
        payload_with_crc = cls._add_checksum(data)

        if style == STYLE_STANDARD:
            return cls._encode_words(payload_with_crc, " ")
        if style == STYLE_URI:
            return cls._encode_words(payload_with_crc, "-")
        if style == STYLE_MINIMAL:
            return cls._encode_minimal(payload_with_crc)

        raise ValueError("Unknown Bytewords style: " + style)
