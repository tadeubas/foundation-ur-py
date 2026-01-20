#
# cbor_lite.py
#
# Copyright © 2020 Foundation Devices, Inc.
# Licensed under the "BSD-2-Clause Plus Patent License"
#

# From: https://bitbucket.org/isode/cbor-lite/raw/6c770624a97e3229e3f200be092c1b9c70a60ef1/include/cbor-lite/codec.h

# This file is part of CBOR-lite which is copyright Isode Limited
# and others and released under a MIT license. For details, see the
# COPYRIGHT.md file in the top-level folder of the CBOR-lite software
# distribution.


Flag_None = 0
Flag_Require_Minimal_Encoding = 1

Tag_Major_unsignedInteger = 0
Tag_Major_negativeInteger = 1 << 5
Tag_Major_byteString = 2 << 5
# Tag_Major_textString = 3 << 5
Tag_Major_array = 4 << 5
# Tag_Major_map = 5 << 5
# Tag_Major_semantic = 6 << 5
# Tag_Major_floatingPoint = 7 << 5
# Tag_Major_simple = 7 << 5
Tag_Major_mask = 0xE0

Tag_Minor_length1 = 24
Tag_Minor_length2 = 25
Tag_Minor_length4 = 26
Tag_Minor_length8 = 27

# Tag_Minor_false = 20
# Tag_Minor_true = 21
# Tag_Minor_null = 22
# Tag_Minor_undefined = 23
# Tag_Minor_half_float = 25
# Tag_Minor_singleFloat = 26
# Tag_Minor_doubleFloat = 27

# Tag_Minor_dateTime = 0
# Tag_Minor_epochDateTime = 1
# Tag_Minor_positiveBignum = 2
# Tag_Minor_negativeBignum = 3
# Tag_Minor_decimalFraction = 4
# Tag_Minor_bigFloat = 5
# Tag_Minor_convertBase64Url = 21
# Tag_Minor_convertBase64 = 22
# Tag_Minor_convertBase16 = 23
# Tag_Minor_cborEncodedData = 24
# Tag_Minor_uri = 32
# Tag_Minor_base64Url = 33
# Tag_Minor_base64 = 34
# Tag_Minor_regex = 35
# Tag_Minor_mimeMessage = 36
# Tag_Minor_selfDescribeCbor = 55799
Tag_Minor_mask = 0x1F
# Tag_Undefined = Tag_Major_semantic + Tag_Minor_undefined

_SHIFTS_8 = (56, 48, 40, 32, 24, 16, 8, 0)
_SHIFTS_4 = (24, 16, 8, 0)
_SHIFTS_2 = (8, 0)

BYTE_MASK = 0xFF


# STAY
def get_byte_length(value):
    if value < 24:
        return 0
    if value <= 0xFF:
        return 1
    if value <= 0xFFFF:
        return 2
    if value <= 0xFFFFFFFF:
        return 4
    return 8


class CBOREncoder:
    def __init__(self):
        self.buf = bytearray()

    # STAY
    def get_bytes(self):
        return self.buf

    # STAY
    def encodeTagAndAdditional(self, tag, additional):
        self.buf.append(tag + additional)
        return 1

    # STAY
    def encodeTagAndValue(self, tag, value):
        length = get_byte_length(value)

        # 5-8 bytes required, use 8 bytes
        if 5 <= length <= 8:
            self.encodeTagAndAdditional(tag, Tag_Minor_length8)
            self.buf.append((value >> 56) & BYTE_MASK)
            self.buf.append((value >> 48) & BYTE_MASK)
            self.buf.append((value >> 40) & BYTE_MASK)
            self.buf.append((value >> 32) & BYTE_MASK)
            self.buf.append((value >> 24) & BYTE_MASK)
            self.buf.append((value >> 16) & BYTE_MASK)
            self.buf.append((value >> 8) & BYTE_MASK)
            self.buf.append(value & BYTE_MASK)

        # 3-4 bytes required, use 4 bytes
        elif length in (3, 4):
            self.encodeTagAndAdditional(tag, Tag_Minor_length4)
            self.buf.append((value >> 24) & BYTE_MASK)
            self.buf.append((value >> 16) & BYTE_MASK)
            self.buf.append((value >> 8) & BYTE_MASK)
            self.buf.append(value & BYTE_MASK)

        elif length == 2:
            self.encodeTagAndAdditional(tag, Tag_Minor_length2)
            self.buf.append((value >> 8) & BYTE_MASK)
            self.buf.append(value & BYTE_MASK)

        elif length == 1:
            self.encodeTagAndAdditional(tag, Tag_Minor_length1)
            self.buf.append(value & BYTE_MASK)

        elif length == 0:
            self.encodeTagAndAdditional(tag, value)

        else:
            raise ValueError("Unsupported byte length for value in encodeTagAndValue")

        encoded_size = 1 + length
        return encoded_size

    # STAY
    def encodeUnsigned(self, value):
        return self.encodeTagAndValue(Tag_Major_unsignedInteger, value)

    # STAY
    def encodeNegative(self, value):
        return self.encodeTagAndValue(Tag_Major_negativeInteger, value)

    # STAY
    def encodeInteger(self, value):
        if value >= 0:
            return self.encodeUnsigned(value)
        return self.encodeNegative(value)

    # def encodeBool(self, value):
    #     return self.encodeTagAndValue(
    #         Tag_Major_simple, Tag_Minor_true if value else Tag_Minor_false
    #     )

    # STAY
    def encodeBytes(self, value):
        length = self.encodeTagAndValue(Tag_Major_byteString, len(value))
        self.buf += value
        return length + len(value)

    # def encodeEncodedBytes(self, value):
    #     length = self.encodeTagAndValue(Tag_Major_semantic, Tag_Minor_cborEncodedData)
    #     return length + self.encodeBytes(value)

    # def encodeEncodedBytes(self, value):
    #     length = self.encodeTagAndValue(Tag_Major_semantic, Tag_Minor_cborEncodedData)
    #     return length + self.encodeBytes(value)

    # def encodeText(self, value):
    #     str_len = len(value)
    #     length = self.encodeTagAndValue(Tag_Major_textString, str_len)
    #     self.buf.append(bytes(value, "utf8"))
    #     return length + str_len

    # STAY
    def encodeArraySize(self, value):
        return self.encodeTagAndValue(Tag_Major_array, value)

    # def encodeMapSize(self, value):
    #     return self.encodeTagAndValue(Tag_Major_map, value)


class CBORDecoder:
    def __init__(self, buf):
        self.buf = buf
        self.pos = 0

    # STAY
    def decodeTagAndAdditional(self):
        pos = self.pos
        buf = self.buf
        if pos >= len(buf):
            raise Exception("Not enough input")
        octet = buf[pos]
        self.pos = pos + 1
        return octet & Tag_Major_mask, octet & Tag_Minor_mask, 1

    # STAY
    def _decode_with_tag(self, expected_tag, flags):
        tag, value, length = self.decodeTagAndValue(flags)
        if tag != expected_tag:
            raise ValueError("Expected " + expected_tag)
        return value, length

    # STAY
    def decodeTagAndValue(self, flags):
        buf = self.buf
        pos = self.pos
        end = len(buf)

        tag, additional, _ = self.decodeTagAndAdditional()
        start = self.pos

        if additional < 24:
            return tag, additional, 1

        value = 0

        if additional == Tag_Minor_length8:
            if end - pos < 8:
                raise Exception("Not enough input")
            for shift in _SHIFTS_8:
                value |= buf[self.pos] << shift
                self.pos += 1

        elif additional == Tag_Minor_length4:
            if end - pos < 4:
                raise Exception("Not enough input")
            for shift in _SHIFTS_4:
                value |= buf[self.pos] << shift
                self.pos += 1

        elif additional == Tag_Minor_length2:
            if end - pos < 2:
                raise Exception("Not enough input")
            for shift in _SHIFTS_2:
                value |= buf[self.pos] << shift
                self.pos += 1

        elif additional == Tag_Minor_length1:
            if end - pos < 1:
                raise Exception("Not enough input")
            value = buf[self.pos]
            self.pos += 1

        else:
            raise Exception("Bad additional value")

        if (flags & Flag_Require_Minimal_Encoding) and value == 0:
            raise Exception("Encoding not minimal")

        return tag, value, self.pos - start + 1

    # STAY
    def decodeUnsigned(self, flags=Flag_None):
        return self._decode_with_tag(Tag_Major_unsignedInteger, flags)

    # def decodeNegative(self, flags=Flag_None):
    #     (tag, value, length) = self.decodeTagAndValue(flags)
    #     if tag != Tag_Major_negativeInteger:
    #         raise Exception(
    #             "Expected Tag_Major_negativeInteger, but found {}".format(tag)
    #         )
    #     return (value, length)

    # def decodeInteger(self, flags=Flag_None):
    #     (tag, value, length) = self.decodeTagAndValue(flags)
    #     if tag == Tag_Major_unsignedInteger:
    #         return (value, length)
    #     elif tag == Tag_Major_negativeInteger:
    #         # CBOR major type 1: value is -1 - n (RFC 8949)
    #         return (-1 - value, length)

    # def decodeBool(self, flags=Flag_None):
    #     (tag, value, length) = self.decodeTagAndValue(flags)
    #     if tag == Tag_Major_simple:
    #         if value == Tag_Minor_true:
    #             return (True, length)
    #         if value == Tag_Minor_false:
    #             return (False, length)
    #         raise Exception("Not a Boolean")
    #     raise Exception("Not Simple/Boolean")

    # STAY
    def decodeBytes(self, flags=Flag_None):
        # First value is the length of the bytes that follow
        tag, byte_length, size_length = self.decodeTagAndValue(flags)
        if tag != Tag_Major_byteString:
            raise Exception("Not a byteString")

        end = len(self.buf)
        if end - self.pos < byte_length:
            raise Exception("Not enough input")

        mv = memoryview(self.buf)[self.pos : self.pos + byte_length]
        self.pos += byte_length
        return mv, size_length + byte_length

    # def decodeEncodedBytesPrefix(self, flags=Flag_None):
    #     (tag, value, length1) = self.decodeTagAndValue(flags)
    #     if tag != Tag_Major_semantic or value != Tag_Minor_cborEncodedData:
    #         raise Exception("Not CBOR Encoded Data")

    #     (tag, value, length2) = self.decodeTagAndValue(flags)
    #     if tag != Tag_Major_byteString:
    #         raise Exception("Not byteString")

    #     return (tag, value, length1 + length2)

    # def decodeEncodedBytes(self, flags=Flag_None):
    #     (tag, minor_tag, tag_length) = self.decodeTagAndValue(flags)
    #     if tag != Tag_Major_semantic or minor_tag != Tag_Minor_cborEncodedData:
    #         raise Exception("Not CBOR Encoded Data")

    #     (value, length) = self.decodeBytes(flags)
    #     return (value, tag_length + length)

    # def decodeText(self, flags=Flag_None):
    #     # First value is the length of the bytes that follow
    #     (tag, byte_length, size_length) = self.decodeTagAndValue(flags)
    #     if tag != Tag_Major_textString:
    #         raise Exception("Not a textString")

    #     end = len(self.buf)
    #     if end - self.pos < byte_length:
    #         raise Exception("Not enough input")

    #     value = bytes(self.buf[self.pos : self.pos + byte_length])
    #     self.pos += byte_length
    #     return (value, size_length + byte_length)

    # STAY
    def decodeArraySize(self, flags=Flag_None):
        return self._decode_with_tag(Tag_Major_array, flags)

    # def decodeMapSize(self, flags=Flag_None):
    #     (tag, value, length) = self.decodeTagAndValue(flags)
    #     if tag != Tag_Major_mask:
    #         raise Exception("Expected Tag_Major_map, but found {}".format(tag))
    #     return (value, length)
