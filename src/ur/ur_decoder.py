#
# ur_decoder.py
#
# Copyright © 2020 Foundation Devices, Inc.
# Licensed under the "BSD-2-Clause Plus Patent License"
#

from .ur import UR
from .fountain_encoder import Part as FountainEncoderPart
from .fountain_decoder import FountainDecoder
from .bytewords import STYLE_MINIMAL
from .bytewords.bytewords_decode import BytewordsDecoder

# from .utils import is_ur_type
from .basic_decoder import BasicDecoder


# STAY
class URDecoder(BasicDecoder):
    # Start decoding a (possibly) multi-part UR
    def __init__(self):
        super().__init__()
        self.fountain_decoder = FountainDecoder()
        self.expected_type = None

    # STAY
    # Decode a single-part UR
    @staticmethod
    def decode(data):
        _type, body, is_multi = URDecoder.parse(data)
        if is_multi:
            raise ValueError("Multi-part UR")
        cbor = BytewordsDecoder.decode(STYLE_MINIMAL, body)
        return UR(_type.decode(), cbor)

    # STAY
    @staticmethod
    def parse(data):
        if isinstance(data, str):
            data = data.encode()

        # Don't need to validade as caller always check for startswith 'ur:'
        # Validate scheme
        # if data[:3].lower() != b"ur:":
        #     raise ValueError("Invalid UR")

        path = data[3:]

        # Find first slash (type separator)
        p0 = path.find(b"/")
        if p0 < 0:
            raise ValueError("Invalid UR")

        _type = path[:p0]
        # remove unnecessary check
        # if not is_ur_type(_type.decode()):
        #     raise ValueError("Invalid UR")

        rest = path[p0 + 1 :]

        # Single / multi
        p1 = rest.find(b"/")
        if p1 < 0:
            # single-part
            return _type, rest, False

        # multi-part
        seq = rest[:p1]
        frag = rest[p1 + 1 :]
        return _type, (seq, frag), True

    # STAY
    @staticmethod
    def parse_sequence_component(s):
        i = s.find(b"-")
        if i < 0:
            raise ValueError("Invalid sequence component")
        a = int(s[:i])
        b = int(s[i + 1 :])
        if a < 1 or b < 1:
            raise ValueError("Invalid sequence component")
        return a, b

    # STAY
    def validate_part(self, _type):
        if self.expected_type is None:
            # remove unnecessary check
            # if not is_ur_type(_type):
            #     return False
            self.expected_type = _type
            return True
        return _type == self.expected_type

    # STAY
    def receive_part(self, part):
        if self.result is not None:
            return False

        _type, payload, is_multi = URDecoder.parse(part)
        if not self.validate_part(_type):
            return False

        if not is_multi:
            body = payload
            cbor = BytewordsDecoder.decode(STYLE_MINIMAL, body)
            self.result = UR(_type.decode(), cbor)
            return True

        seq, fragment = payload
        seq_num, seq_len = URDecoder.parse_sequence_component(seq)

        cbor = BytewordsDecoder.decode(STYLE_MINIMAL, fragment)
        part = FountainEncoderPart.from_cbor(cbor)

        if seq_num != part.seq_num or seq_len != part.seq_len:
            return False

        if not self.fountain_decoder.receive_part(part):
            return False

        if self.fountain_decoder.is_success():
            self.result = UR(_type.decode(), self.fountain_decoder.result)
        else:
            self.result = self.fountain_decoder.result

        return True

    # STAY
    def expected_part_count(self):
        return self.fountain_decoder.expected_part_count()

    # STAY
    def received_part_indexes(self):
        return self.fountain_decoder.received_part_indexes

    # def last_part_indexes(self):
    #     return self.fountain_decoder.last_part_indexes

    # STAY
    def processed_parts_count(self):
        return self.fountain_decoder.processed_parts_count

    # STAY
    def estimated_percent_complete(self):
        return self.fountain_decoder.estimated_percent_complete()
