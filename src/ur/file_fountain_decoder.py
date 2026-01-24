#
# Copyright © 2020 Foundation Devices, Inc. and Contributors
# Licensed under the "BSD-2-Clause Plus Patent License"
#

import os
from .fountain_decoder import FountainDecoder, InvalidChecksum
from .crc32 import crc32


class FileFountainDecoder(FountainDecoder):
    """
    Fountain decoder that uses a files for fragments to minimize RAM usage.
    """

    def __init__(self, workdir):
        super().__init__()
        self.workdir = workdir

    def _fragment_path(self, index):
        return self.workdir + "/" + "frag_%05d.tmp" % index

    def _clear_files(self):
        for name in os.listdir(self.workdir):
            if name.startswith("frag_"):
                os.remove(self.workdir + "/" + name)

    #  overrides ------

    def _clear_caches(self):
        super()._clear_caches()
        self._clear_files()

    def join_fragments_from_files(self, out_path):
        remaining = self.expected_message_len
        checksum = 0

        with open(out_path, "wb") as out:
            for i in range(self.expected_part_count()):
                if remaining <= 0:
                    break

                with open(self._fragment_path(i), "rb") as frag:
                    chunk = frag.read()

                    if len(chunk) > remaining:
                        chunk = chunk[:remaining]

                    checksum = crc32(chunk, checksum)
                    out.write(chunk)
                    remaining -= len(chunk)

        return checksum

    def _store_fragment(self, index, part):
        with open(self._fragment_path(index), "wb") as f:
            f.write(part.data)

    def _finalize_message(self):
        out_path = self.workdir + "/" + "data.txt"

        checksum = self.join_fragments_from_files(out_path)

        if checksum == self.expected_checksum:
            self.result = out_path  # or open file handle if you prefer
        else:
            self.result = InvalidChecksum()
