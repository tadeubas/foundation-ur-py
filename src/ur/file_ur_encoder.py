#
# Copyright © 2020 Foundation Devices, Inc. and Contributors
# Licensed under the "BSD-2-Clause Plus Patent License"
#

from .ur_encoder import UREncoder
from .file_fountain_encoder import FileFountainEncoder

class FileUREncoder(UREncoder):
    """
    UR decoder that uses a FileFountainEncoder to minimize RAM usage.
    """

    def __init__(self, ur, max_fragment_len, first_seq_num=0, min_fragment_len=10):
        self.ur = ur
        self.fountain_encoder = FileFountainEncoder(ur.cbor, max_fragment_len, first_seq_num, min_fragment_len)

    def next_part(self):
        part = self.fountain_encoder.next_part()
        if self.is_single_part():
            with open(self.fountain_encoder.file_path, "rb") as f:
                self.ur.cbor = f.read()
            return UREncoder.encode(self.ur)

        return UREncoder.encode_part(self.ur.type, part)