#
# ur_encoder.py
#
# Copyright © 2020 Foundation Devices, Inc.
# Licensed under the "BSD-2-Clause Plus Patent License"
#

from .fountain_encoder import FountainEncoder
from .bytewords import STYLE_MINIMAL
from .bytewords.bytewords_encode import BytewordsEncoder


# STAY
class UREncoder:
    # Start encoding a (possibly) multi-part UR
    def __init__(self, ur, max_fragment_len, first_seq_num=0, min_fragment_len=10):
        self.ur = ur
        self.fountain_encoder = FountainEncoder(
            ur.cbor, max_fragment_len, first_seq_num, min_fragment_len
        )

    # STAY
    # Encode a single-part UR
    @staticmethod
    def encode(ur):
        body = BytewordsEncoder.encode(STYLE_MINIMAL, ur.cbor)
        return UREncoder.encode_ur(ur.type, body)

    # def last_part_indexes(self):
    #     return self.fountain_encoder.last_part_indexes()

    # `True` if the minimal number of parts to transmit the message have been
    # generated. Parts generated when this is `true` will be fountain codes
    # containing various mixes of the part data.
    # def is_complete(self):
    #     return self.fountain_encoder.is_complete()

    # STAY
    # `True` if this UR can be contained in a single part. If `True`, repeated
    # calls to `next_part()` will all return the same single-part UR.
    def is_single_part(self):
        return self.fountain_encoder.is_single_part()

    # STAY
    def next_part(self):
        part = self.fountain_encoder.next_part()
        if self.is_single_part():
            return UREncoder.encode(self.ur)
        return UREncoder.encode_part(self.ur.type, part)

    # STAY
    @staticmethod
    def encode_part(_type, part):
        seq = "{}-{}".format(part.seq_num, part.seq_len)
        body = BytewordsEncoder.encode(STYLE_MINIMAL, part.cbor())
        result = UREncoder.encode_ur(_type, seq, body)
        return result

    # STAY
    @staticmethod
    def encode_uri(scheme, path_components):
        path = "/".join(path_components)
        return scheme + ":" + path

    # STAY
    @staticmethod
    def encode_ur(*path_components):
        return UREncoder.encode_uri("ur", path_components)
