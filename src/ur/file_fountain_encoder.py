#
# Copyright © 2020 Foundation Devices, Inc. and Contributors
# Licensed under the "BSD-2-Clause Plus Patent License"
#

import os
from .fountain_encoder import FountainEncoder
from .utils import xor_into
from .constants import MAX_UINT32
from .crc32 import crc32


class FileFountainEncoder(FountainEncoder):
    def __init__(
        self,
        file_path,
        max_fragment_len,
        first_seq_num=0,
        min_fragment_len=10,
    ):
        self.file_path = file_path

        stat = os.stat(file_path)
        self.message_len = stat.st_size
        assert self.message_len <= MAX_UINT32

        self.checksum = self._compute_checksum()

        self.fragment_len = self.find_nominal_fragment_length(
            self.message_len,
            min_fragment_len,
            max_fragment_len,
        )

        self.seq_num = first_seq_num

    def _read_range(self, offset, length):
        with open(self.file_path, "rb") as f:
            f.seek(offset)
            return f.read(length)

    def _compute_checksum(self):
        checksum = 0
        remaining = self.message_len

        with open(self.file_path, "rb") as f:
            while remaining > 0:
                chunk = f.read(min(256, remaining))
                if not chunk:
                    break
                checksum = crc32(chunk, checksum)
                remaining -= len(chunk)

        return checksum

    #  overrides ------

    def mix(self, indexes):
        """
        XOR selected fragments directly from disk.
        """
        result = bytearray(self.fragment_len)
        frag_len = self.fragment_len
        msg_len = self.message_len

        for index in indexes:
            start = index * frag_len
            if start >= msg_len:
                continue

            size = min(frag_len, msg_len - start)
            chunk = self._read_range(start, size)
            xor_into(result, chunk)

        return result
