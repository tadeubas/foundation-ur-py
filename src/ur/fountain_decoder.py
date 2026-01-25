#
# fountain_decoder.py
#
# Copyright © 2020 Foundation Devices, Inc.
# Licensed under the "BSD-2-Clause Plus Patent License"
#

from .fountain_utils import (
    choose_fragments,
    reset_degree_cache,
)
from .utils import join_bytes, xor_into
from .crc32 import crc32
from .basic_decoder import BasicDecoder


class InvalidChecksum(Exception):
    pass


class FountainDecoder(BasicDecoder):
    class Part:
        __slots__ = ("indexes", "data", "_index")

        def __init__(self, indexes, data):
            self.indexes = indexes
            self.data = data
            # cache its index once if simple part
            self._index = next(iter(indexes)) if len(indexes) == 1 else None

        def is_simple(self):
            return self._index is not None

        def index(self):
            return self._index

        @classmethod
        def from_encoder_part(cls, p):
            return cls(choose_fragments(p.seq_num, p.seq_len, p.checksum), p.data)

    # FountainDecoder
    def __init__(self):
        super().__init__()
        self.received_part_indexes = set()
        # self.last_part_indexes = None
        self.processed_parts_count = 0
        self.expected_part_indexes = None
        self.expected_fragment_len = None
        self.expected_message_len = None
        self.expected_checksum = None
        self.simple_parts = {}
        self.mixed_parts = {}
        self.queued_parts = []

    def _clear_caches(self):
        self.simple_parts.clear()
        self.mixed_parts.clear()
        self.queued_parts.clear()
        self.received_part_indexes.clear()
        self.expected_part_indexes = None

    def is_complete(self):
        if self.result is not None:
            # Decode / Encoder operations don't usually happen in parallel, otherwise reset_degree_cache() will need to be removed from here
            reset_degree_cache()  # reset the cache for receive_part -> FountainDecoder.Part.from_encoder_part -> choose_fragments -> choose_degree
            return True
        return False

    def expected_part_count(self):
        if self.expected_part_indexes is not None:
            return len(self.expected_part_indexes)
        raise RuntimeError("Decoder not initialized yet")

    def estimated_percent_complete(self):
        if self.is_complete():
            return 1
        if self.expected_part_indexes is None:
            return 0
        estimated_input_parts = self.expected_part_count() * 1.75
        return min(0.99, self.processed_parts_count / estimated_input_parts)

    def receive_part(self, encoder_part):
        # Don't process the part if we're already done
        if self.is_complete():
            return False

        # Don't continue if this part doesn't validate
        if not self.validate_part(encoder_part):
            return False

        # Process this part as if it was from queue
        p = FountainDecoder.Part.from_encoder_part(encoder_part)
        # self.last_part_indexes = p.indexes
        self.process_queue_item(p)

        # Process the queue until we're done or the queue is empty
        while len(self.queued_parts) > 0 and not self.is_complete():
            self.process_queue_item(self.queued_parts.pop())

        # Keep track of how many parts we've processed
        self.processed_parts_count += 1

        # self.print_part_end()

        return True

    # Join all the fragments of a message together, throwing away any padding
    @staticmethod
    def join_fragments(fragments, message_len):
        message = join_bytes(fragments)
        return message[:message_len]

    def process_queue_item(self, part):

        if part.is_simple():
            self.process_simple_part(part)
        else:
            self.process_mixed_part(part)

    def reduce_mixed_by(self, p):
        new_mixed = {}
        for value in self.mixed_parts.values():
            reduced = self.reduced_part_by_part(value, p)
            if reduced.is_simple():
                self.queued_parts.append(reduced)
            else:
                new_mixed[reduced.indexes] = reduced
        self.mixed_parts.clear()
        self.mixed_parts.update(new_mixed)

    def reduced_part_by_part(self, a, b):
        # If the fragments mixed into `b` are a strict (proper) subset of those in `a`...
        if b.indexes != a.indexes and b.indexes.issubset(a.indexes):
            # The new fragments in the revised part are `a` - `b`
            new_indexes = a.indexes.difference(b.indexes)
            # The new data in the revised part are `a` XOR `b`
            new_data = bytearray(a.data)
            xor_into(new_data, b.data)

            return self.Part(new_indexes, new_data)

        # `a` is not reducable by `b`, so return a
        return a

    def _store_fragment(self, _index, part):
        # store whole part
        self.simple_parts[part.indexes] = part

    def _finalize_message(self):
        fragments = [None] * self.expected_part_count()
        for part in self.simple_parts.values():
            fragments[part.index()] = part.data

        message = self.join_fragments(fragments, self.expected_message_len)

        # Verify the message checksum and note success or failure
        checksum = crc32(message)
        if checksum == self.expected_checksum:
            self.result = message
        else:
            self.result = InvalidChecksum()

    def process_simple_part(self, p):
        # Don't process duplicate parts
        fragment_index = p.index()
        if fragment_index in self.received_part_indexes:
            return

        # Record this part
        self._store_fragment(fragment_index, p)
        self.received_part_indexes.add(fragment_index)

        # If we've received all the parts
        if self.received_part_indexes == self.expected_part_indexes:
            # Reassemble the message from its fragments
            self._finalize_message()
            self._clear_caches()
        else:
            # Reduce all the mixed parts by this part
            self.reduce_mixed_by(p)

    def process_mixed_part(self, p):
        # Don't process duplicate parts
        if p.indexes in self.mixed_parts:
            return

        # Reduce this part by all the others
        reduced = p
        for r in self.simple_parts.values():
            reduced = self.reduced_part_by_part(reduced, r)
            if reduced.is_simple():
                break

        if not reduced.is_simple():
            for r in self.mixed_parts.values():
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
            self.mixed_parts[reduced.indexes] = reduced

    def validate_part(self, p):
        # If this is the first part we've seen
        if self.expected_part_indexes is None:
            self.expected_part_indexes = set(range(p.seq_len))
            self.expected_message_len = p.message_len
            self.expected_checksum = p.checksum
            self.expected_fragment_len = len(p.data)
        else:
            if (
                self.expected_part_count() != p.seq_len
                or self.expected_message_len != p.message_len
                or self.expected_checksum != p.checksum
                or self.expected_fragment_len != len(p.data)
            ):
                return False

        return True
