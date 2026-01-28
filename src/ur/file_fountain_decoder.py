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
        self.mixed_part_indexes.clear()
        self._clear_files()

    def join_fragments_from_files(self, out_path):
        remaining = self.expected_message_len
        checksum = 0

        buf = bytearray(self.expected_fragment_len)
        mv = memoryview(buf)

        with open(out_path, "wb") as out:
            for i in range(self.expected_part_count()):
                if remaining <= 0:
                    break

                with open(self._fragment_path(i), "rb") as frag:
                    while remaining > 0:
                        n = frag.readinto(buf)
                        if n == 0:
                            break

                        # pylint: disable=consider-using-min-builtin
                        if n > remaining:
                            n = remaining

                        chunk = mv[:n]
                        checksum = crc32(chunk, checksum)
                        out.write(chunk)
                        remaining -= n

        return checksum

    def _store_fragment(self, index, part):
        filename = (
            self._fragment_path(index)
            if isinstance(index, int)
            else self._fragment_path_mixed(index)
        )
        with open(filename, "wb") as f:
            f.write(part.data)

    def _finalize_message(self):
        out_path = self.workdir + "/" + "data.txt"

        checksum = self.join_fragments_from_files(out_path)

        if checksum == self.expected_checksum:
            self.result = out_path  # or open file handle if you prefer
        else:
            self.result = InvalidChecksum()

    def _retrieve_part_data(self, p):
        if isinstance(p.data, str):
            with open(p.data, "rb") as frag:
                p.data = frag.read()

    def reduce_mixed_by(self, p):
        new_mixed_indexes = set()

        for indexes in self.mixed_part_indexes:
            value_bytearray = bytearray(self.expected_fragment_len)
            with open(self._fragment_path_mixed(indexes), "rb") as mixed_frag:
                mixed_frag.readinto(value_bytearray)
            reduced = self.reduced_part_by_part(
                FountainDecoder.Part(indexes, value_bytearray), p
            )
            if reduced.is_simple():
                self.queued_parts.append(reduced)
            else:
                self._store_fragment(reduced.indexes, reduced)
                new_mixed_indexes.add(reduced.indexes)

        self.mixed_part_indexes.clear()
        self.mixed_part_indexes.update(new_mixed_indexes)

    def process_mixed_part(self, p):
        # Don't process duplicate parts
        if p.indexes in self.mixed_part_indexes:
            return

        # Reduce this part by all the others
        reduced = p

        for index in self.received_part_indexes:
            r = FountainDecoder.Part(frozenset([index]), self._fragment_path(index))
            reduced = self.reduced_part_by_part(reduced, r)
            if reduced.is_simple():
                break

        if not reduced.is_simple():
            for indexes in self.mixed_part_indexes:
                r = FountainDecoder.Part(indexes, self._fragment_path_mixed(indexes))
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
            self._store_fragment(reduced.indexes, reduced)
            self.mixed_part_indexes.add(reduced.indexes)
