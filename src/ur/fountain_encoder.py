#
# fountain_encoder.py
#
# Copyright © 2020 Foundation Devices, Inc.
# Licensed under the "BSD-2-Clause Plus Patent License"
#

import math
from .cbor_lite import CBORDecoder, CBOREncoder
from .fountain_utils import choose_fragments
from .utils import xor_into
from .constants import MAX_UINT32, MAX_UINT64
from .crc32 import crc32


class InvalidHeader(Exception):
    pass


class Part:

    def __init__(self, seq_num, seq_len, message_len, checksum, data):
        self.seq_num = seq_num
        self.seq_len = seq_len
        self.message_len = message_len
        self.checksum = checksum
        self.data = data

    @staticmethod
    def from_cbor(cbor_buf):
        decoder = CBORDecoder(cbor_buf)
        (array_size, _) = decoder.decodeArraySize()
        if array_size != 5:
            raise InvalidHeader()

        (seq_num, _) = decoder.decodeUnsigned()
        if seq_num > MAX_UINT64:
            raise InvalidHeader()

        (seq_len, _) = decoder.decodeUnsigned()
        if seq_len > MAX_UINT64:
            raise InvalidHeader()

        (message_len, _) = decoder.decodeUnsigned()
        if message_len > MAX_UINT64:
            raise InvalidHeader()

        (checksum, _) = decoder.decodeUnsigned()
        if checksum > MAX_UINT64:
            raise InvalidHeader()

        (data, _) = decoder.decodeBytes()

        return Part(seq_num, seq_len, message_len, checksum, data)

    def cbor(self):
        encoder = CBOREncoder()
        encoder.encodeArraySize(5)
        encoder.encodeInteger(self.seq_num)
        encoder.encodeInteger(self.seq_len)
        encoder.encodeInteger(self.message_len)
        encoder.encodeInteger(self.checksum)
        encoder.encodeBytes(self.data)
        return encoder.get_bytes()

    # def description(self):
    #     return "seqNum:{}, seqLen:{}, messageLen:{}, checksum:{}, data:{}".format(
    #         self.seq_num,
    #         self.seq_len,
    #         self.message_len,
    #         self.checksum,
    #         data_to_hex(self.data),
    #     )


# STAY
class FountainEncoder:
    def __init__(self, message, max_fragment_len, first_seq_num=0, min_fragment_len=10):
        assert isinstance(message, bytearray)
        assert len(message) <= MAX_UINT32
        self.message_len = len(message)
        self.checksum = crc32(message)
        self.fragment_len = FountainEncoder.find_nominal_fragment_length(
            self.message_len, min_fragment_len, max_fragment_len
        )
        self.fragments = FountainEncoder.partition_message(message, self.fragment_len)
        self.seq_num = first_seq_num

    @staticmethod
    def find_nominal_fragment_length(message_len, min_fragment_len, max_fragment_len):
        assert message_len > 0
        assert min_fragment_len > 0
        assert max_fragment_len >= min_fragment_len
        max_fragment_count = message_len // min_fragment_len
        fragment_len = None

        for fragment_count in range(1, max_fragment_count + 1):
            fragment_len = math.ceil(message_len / fragment_count)
            if fragment_len <= max_fragment_len:
                break

        assert fragment_len is not None
        return fragment_len

    @staticmethod
    def partition_message(message, fragment_len):
        remaining = memoryview(message)
        fragments = []

        while len(remaining):
            frag_view = remaining[:fragment_len]
            remaining = remaining[fragment_len:]

            # Create owned fragment buffer
            fragment = bytearray(fragment_len)
            fragment[: len(frag_view)] = frag_view

            fragments.append(fragment)

        return fragments

    def last_part_indexes(self):
        return self.last_part_indexes

    def seq_len(self):
        return len(self.fragments)

    # This becomes `true` when the minimum number of parts
    # to relay the complete message have been generated
    def is_complete(self):
        return self.seq_num >= self.seq_len()

    # True if only a single part will be generated.
    def is_single_part(self):
        return self.seq_len() == 1

    # STAY
    def next_part(self):
        self.seq_num += 1
        self.seq_num = self.seq_num % MAX_UINT32  # wrap at period 2^32
        indexes = choose_fragments(self.seq_num, self.seq_len(), self.checksum)
        mixed = self.mix(indexes)
        data = bytes(mixed)
        return Part(self.seq_num, self.seq_len(), self.message_len, self.checksum, data)

    def mix(self, indexes):
        result = [0] * self.fragment_len
        for index in indexes:
            xor_into(result, self.fragments[index])
        return result
