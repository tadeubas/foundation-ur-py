#
# ur_decoder.py
#
# Copyright © 2020 Foundation Devices, Inc.
# Licensed under the "BSD-2-Clause Plus Patent License"
#

from .ur import UR
from .fountain_encoder import Part as FountainEncoderPart
from .fountain_decoder import FountainDecoder
from .bytewords.bytewords_decode import BytewordsDecoder
from .basic_decoder import BasicDecoder

SLASH = ord("/")
HYPHEN = ord("-")


class URDecoder(BasicDecoder):
    # Start decoding a (possibly) multi-part UR
    def __init__(self):
        super().__init__()
        self.fountain_decoder = FountainDecoder()
        self.expected_type = None

    # Decode a single-part UR
    @staticmethod
    def decode(data):
        _type, body, is_multi = URDecoder.parse(data)
        if is_multi:
            raise ValueError("Multi-part UR")
        cbor = BytewordsDecoder.decode(body)
        return UR(bytes(_type).decode(), cbor)

    @staticmethod
    def _find_byte(mv, byte):
        for i, b in enumerate(mv):
            if b == byte:
                return i
        return -1

    @staticmethod
    def parse(data):
        if isinstance(data, str):
            data = data.encode()

        data = memoryview(data)
        path = data[3:]

        # Find first slash (type separator)
        p0 = URDecoder._find_byte(path, SLASH)
        if p0 < 0:
            raise ValueError("Invalid UR")

        _type = path[:p0]
        rest = path[p0 + 1 :]

        # Single / multi
        p1 = URDecoder._find_byte(rest, SLASH)
        if p1 < 0:
            # single-part
            return _type, rest, False

        # multi-part
        seq = rest[:p1]
        frag = rest[p1 + 1 :]
        return _type, (seq, frag), True

    @staticmethod
    def parse_sequence_component(s):
        i = URDecoder._find_byte(s, HYPHEN)
        if i < 0:
            raise ValueError("Invalid sequence component")
        a = int(bytes(s[:i]))
        b = int(bytes(s[i + 1 :]))
        if a < 1 or b < 1:
            raise ValueError("Invalid sequence component")
        return a, b

    def validate_part(self, _type):
        if self.expected_type is None:
            # remove unnecessary check
            # if not is_ur_type(_type):
            #     return False
            self.expected_type = _type
            return True
        return _type == self.expected_type

    def receive_part(self, part):
        if self.result is not None:
            return False

        _type, payload, is_multi = URDecoder.parse(part)
        if not self.validate_part(_type):
            return False

        if not is_multi:
            body = payload
            cbor = BytewordsDecoder.decode(body)
            self.result = UR(bytes(_type).decode(), cbor)
            return True

        seq, fragment = payload
        seq_num, seq_len = URDecoder.parse_sequence_component(seq)

        cbor = BytewordsDecoder.decode(fragment)
        part = FountainEncoderPart.from_cbor(cbor)

        if seq_num != part.seq_num or seq_len != part.seq_len:
            return False

        if not self.fountain_decoder.receive_part(part):
            return False

        if self.fountain_decoder.is_success():
            self.result = UR(bytes(_type).decode(), self.fountain_decoder.result)
        else:
            self.result = self.fountain_decoder.result

        return True

    def expected_part_count(self):
        return self.fountain_decoder.expected_part_count()

    def received_part_indexes(self):
        return self.fountain_decoder.received_part_indexes

    def processed_parts_count(self):
        return self.fountain_decoder.processed_parts_count

    def estimated_percent_complete(self):
        return self.fountain_decoder.estimated_percent_complete()
