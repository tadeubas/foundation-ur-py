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
from .utils import is_ur_type
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
    def decode(_str):
        (_type, components) = URDecoder.parse(_str)
        if len(components) == 0:
            raise ValueError("Invalid path length")

        body = components[0]
        return URDecoder.decode_by_type(_type, body)

    # STAY
    @staticmethod
    def decode_by_type(_type, body):
        cbor = BytewordsDecoder.decode(STYLE_MINIMAL, body)
        return UR(_type, cbor)

    # STAY
    @staticmethod
    def parse(data):
        # pylint: disable=consider-using-enumerate

        data = data.encode() if isinstance(data, str) else data

        # Validate URI scheme
        if data[:3].lower() != b"ur:":
            raise ValueError("Invalid UR")

        path = memoryview(data)[3:]
        path_len = len(path)

        # Split the remainder into path components
        components = []
        start = 0
        # Single pass scan
        for i in range(path_len):
            if path[i] == 47:  # ord('/')
                if i > start:
                    components.append(bytes(path[start:i]))
                start = i + 1

        # Last component
        if start < path_len:
            components.append(bytes(path[start:]))

        # Need at least: ur:<type>/<data>
        if len(components) < 2:
            raise ValueError("Invalid UR")

        _type = components[0]
        _type = _type.decode()
        if not is_ur_type(_type):
            raise ValueError("Invalid UR")

        return _type, components[1:]

    # STAY
    @staticmethod
    def parse_sequence_component(_str):
        comps = _str.split("-")
        if len(comps) != 2:
            raise ValueError(" Invalid sequence component")
        seq_num = int(comps[0])
        seq_len = int(comps[1])
        if seq_num < 1 or seq_len < 1:
            raise ValueError(" Invalid sequence component")
        return (seq_num, seq_len)

    # STAY
    def validate_part(self, _type):
        if self.expected_type is None:
            if not is_ur_type(_type):
                return False
            self.expected_type = _type
            return True
        return _type == self.expected_type

    # STAY
    def receive_part(self, part):
        try:
            # Don't process the part if we're already done
            if self.result is not None:
                return False

            # Don't continue if this part doesn't validate
            (_type, components) = URDecoder.parse(part)
            # print("receive_part")
            # print(_type, components)
            if not self.validate_part(_type):
                return False

            # If this is a single-part UR then we're done
            if len(components) == 1:
                # print("single-part")
                body = components[0]
                body = body if isinstance(body, str) else body.decode()
                self.result = self.decode_by_type(_type, body)
                return True

            # Multi-part URs must have two path components: seq/fragment
            if len(components) != 2:
                raise ValueError("Invalid path length")
            seq = components[0]
            # print("multi")
            # print(seq)
            seq = seq if isinstance(seq, str) else seq.decode()
            fragment = components[1]
            # print(type(fragment))
            # print(seq, fragment)
            fragment = fragment if isinstance(fragment, str) else fragment.decode()

            # Parse the sequence component and the fragment, and make sure they agree.
            (seq_num, seq_len) = URDecoder.parse_sequence_component(seq)
            cbor = BytewordsDecoder.decode(STYLE_MINIMAL, fragment)
            part = FountainEncoderPart.from_cbor(cbor)
            if seq_num != part.seq_num or seq_len != part.seq_len:
                return False

            # Process the part
            if not self.fountain_decoder.receive_part(part):
                return False

            if self.fountain_decoder.is_success():
                self.result = UR(_type, self.fountain_decoder.result)
            else:
                self.result = self.fountain_decoder.result

            return True
        except:
            import traceback
            traceback.print_exc()
            print("exception on receive_part")
            raise ValueError("ERROR receive_part")
            return False

    # def expected_type(self):
    #     return self.expected_type

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
