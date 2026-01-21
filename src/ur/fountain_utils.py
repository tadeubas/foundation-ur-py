#
# fountain_utils.py
#
# Copyright © 2020 Foundation Devices, Inc.
# Licensed under the "BSD-2-Clause Plus Patent License"
#

from array import array
from .utils import int_to_bytes
from .xoshiro256 import Xoshiro256


class _DegreeSamplerCache:
    """Cache for choose_fragments -> choose_degree depended on seq_len"""

    class RandomSampler:
        def __init__(self, probs, aliases):
            self.probs = probs
            self.aliases = aliases

        def next(self, rng_func):
            r1 = rng_func()
            r2 = rng_func()
            i = int(r1 * len(self.probs))
            return i if r2 < self.probs[i] else self.aliases[i]

    def __init__(self):
        self.seq_len = None
        self.sampler = None

    def get(self, seq_len):
        if self.seq_len != seq_len:
            self.seq_len = seq_len
            self.sampler = self._build(seq_len)
        return self.sampler

    def _build(self, seq_len):
        # Pre-calculate total for harmonic distribution
        total = 0.0
        for i in range(1, seq_len + 1):
            total += 1.0 / i

        # Calculate probabilities directly into array
        P = array("f")
        inv_total = seq_len / total
        for i in range(seq_len):
            P.append((1.0 / (i + 1)) * inv_total)

        # Use bytearray for small temp storage
        S = []  # Small indices
        L = []  # Large indices
        for i in range(seq_len - 1, -1, -1):
            if P[i] < 1.0:
                S.append(i)
            else:
                L.append(i)

        if seq_len < 256:
            aliases = array("B", [0] * seq_len)
        else:
            aliases = array("H", [0] * seq_len)

        while S and L:
            a = S.pop()
            g = L.pop()
            aliases[a] = g
            P[g] += P[a] - 1.0
            if P[g] < 1.0:
                S.append(g)
            else:
                L.append(g)

        while L:
            P[L.pop()] = 1.0
        while S:
            P[S.pop()] = 1.0

        sampler = _DegreeSamplerCache.RandomSampler(P, aliases)
        return sampler


_degree_cache = _DegreeSamplerCache()


def choose_degree(seq_len, rng):
    sampler = _degree_cache.get(seq_len)
    return sampler.next(rng.next_double) + 1


def reset_degree_cache():
    sampler = _degree_cache.sampler
    if sampler:
        sampler.probs = None
        sampler.aliases = None
    _degree_cache.seq_len = None
    _degree_cache.sampler = None


def choose_fragments(seq_num, seq_len, checksum):
    if seq_num <= seq_len:
        return frozenset([seq_num - 1])

    seed = int_to_bytes(seq_num) + int_to_bytes(checksum)
    rng = Xoshiro256.from_bytes(seed)
    degree = choose_degree(seq_len, rng)

    # Choose smallest array type based on seq_len
    if seq_len < 256:
        remaining = array("B", range(seq_len))
    elif seq_len < 65536:
        remaining = array("H", range(seq_len))
    else:
        remaining = array("I", range(seq_len))
    result = set()

    for _ in range(degree):
        j = rng.next_int(0, len(remaining) - 1)

        v = remaining[j]
        result.add(v)

        # emulate array.pop(j)
        for k in range(j, len(remaining) - 1):
            remaining[k] = remaining[k + 1]

        remaining = remaining[:-1]

    return frozenset(result)
