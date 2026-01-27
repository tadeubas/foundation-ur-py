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
        self.mixed_part_indexes = set()
        self.workdir = workdir

    def _fragment_path(self, index):
        return self.workdir + "/" + "frag_%s.tmp" % index

    def _fragment_path_mixed(self, indexes):
        return self._fragment_path("-".join(map(str, indexes)))

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

    def _store_mixed_fragment(self, indexes, part):
        with open(self._fragment_path_mixed(indexes), "wb") as f:
            f.write(part.data)

    def _finalize_message(self):
        out_path = self.workdir + "/" + "data.txt"

        checksum = self.join_fragments_from_files(out_path)

        if checksum == self.expected_checksum:
            self.result = out_path  # or open file handle if you prefer
        else:
            self.result = InvalidChecksum()

    def reduce_mixed_by(self, p):
        new_mixed_indexes = set()

        for indexes in self.mixed_part_indexes:
            with open(self._fragment_path_mixed(indexes), "rb") as mixed_frag:
                value = mixed_frag.read()
            reduced = self.reduced_part_by_part(FountainDecoder.Part(indexes, value), p)
            if reduced.is_simple():
                self.queued_parts.append(reduced)
            else:
                self._store_mixed_fragment(reduced.indexes, reduced)
                new_mixed_indexes.add(reduced.indexes)

        self.mixed_part_indexes.clear()
        self.mixed_part_indexes.update(new_mixed_indexes)

    def process_mixed_part(self, p):
        if p.indexes in self.mixed_part_indexes:
            return

        # Reduce this part by all the others
        reduced = p

        for index in self.received_part_indexes:
            with open(self._fragment_path(index), "rb") as frag:
                value = frag.read()
                r = FountainDecoder.Part(frozenset([index]), value)
            reduced = self.reduced_part_by_part(reduced, r)
            if reduced.is_simple():
                break

        if not reduced.is_simple():
            for indexes in self.mixed_part_indexes:
                with open(self._fragment_path_mixed(indexes), "rb") as mix_frag:
                    value = mix_frag.read()
                    r = FountainDecoder.Part(indexes, value)
                reduced = self.reduced_part_by_part(reduced, r)
                if reduced.is_simple():
                    break

        # If the part is now simple
        if reduced.is_simple():
            # Add it to the queue
            self.queued_parts.append(reduced)
        else:
            # Reduce all the mixed parts by this one
            self.reduce_mixed_by(reduced)
            # Record this new mixed part
            self._store_mixed_fragment(reduced.indexes, reduced)
            self.mixed_part_indexes.add(reduced.indexes)
