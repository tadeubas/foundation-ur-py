#
# fountain_encoder.py
#
# Copyright © 2020 Foundation Devices, Inc.
# Licensed under the "BSD-2-Clause Plus Patent License"
#

from .cbor_lite import CBORDecoder, CBOREncoder
from .fountain_utils import choose_fragments, reset_degree_cache
from .utils import xor_into
from .constants import MAX_UINT32
from .crc32 import crc32


class Part:
    # Optimized attr storage to avoid dict (valuable if many parts)
    __slots__ = ("seq_num", "seq_len", "message_len", "checksum", "data")

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
            raise ValueError("Invalid header")

        seq_num, _ = decoder.decodeUnsigned()
        seq_len, _ = decoder.decodeUnsigned()
        message_len, _ = decoder.decodeUnsigned()
        checksum, _ = decoder.decodeUnsigned()
        data, _ = decoder.decodeBytes()

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


class FountainEncoder:
    def __init__(self, message, max_fragment_len, first_seq_num=0, min_fragment_len=10):
        assert isinstance(message, bytearray)
        assert len(message) <= MAX_UINT32

        self.message = message
        self.message_len = len(message)
        self.checksum = crc32(message)
        self.fragment_len = self.find_nominal_fragment_length(
            self.message_len, min_fragment_len, max_fragment_len
        )
        self.seq_num = first_seq_num

    @staticmethod
    def find_nominal_fragment_length(message_len, min_fragment_len, max_fragment_len):
        max_fragment_count = message_len // min_fragment_len
        for fragment_count in range(1, max_fragment_count + 1):
            frag_len = (message_len + fragment_count - 1) // fragment_count
            if frag_len <= max_fragment_len:
                return frag_len
        return max_fragment_len

    def seq_len(self):
        return (self.message_len + self.fragment_len - 1) // self.fragment_len

    # This becomes `true` when the minimum number of parts
    # to relay the complete message have been generated
    def is_complete(self):
        if self.seq_num >= self.seq_len():
            # Decode / Encoder operations don't usually happen in parallel, otherwise reset_degree_cache() will need to be removed from here
            reset_degree_cache()  # reset the cache for next_part -> choose_fragments -> choose_degree
            return True
        return False

    # True if only a single part will be generated.
    def is_single_part(self):
        return self.seq_len() == 1

    def next_part(self):
        self.seq_num = (self.seq_num + 1) % MAX_UINT32

        indexes = choose_fragments(self.seq_num, self.seq_len(), self.checksum)
        mixed = self.mix(indexes)

        return Part(
            self.seq_num,
            self.seq_len(),
            self.message_len,
            self.checksum,
            mixed,
        )

    def mix(self, indexes):
        result = bytearray(self.fragment_len)
        msg = self.message
        frag_len = self.fragment_len
        msg_len = self.message_len

        for index in indexes:
            start = index * frag_len
            if start >= msg_len:
                continue
            end = min(start + frag_len, msg_len)
            xor_into(result, msg[start:end])

        return result
