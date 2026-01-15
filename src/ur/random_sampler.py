#
# random_sampler.py
#
# Copyright © 2020 Foundation Devices, Inc.
# Licensed under the "BSD-2-Clause Plus Patent License"
#

# STAY
from array import array


class RandomSampler:
    __slots__ = ("probs", "aliases")

    def __init__(self, probs):
        n = len(probs)
        total = sum(probs)

        P = array("f", [0]) * n
        for i, p in enumerate(probs):
            P[i] = (p * n) / total

        S = []
        L = []

        i = n - 1
        while i >= 0:
            if P[i] < 1:
                S.append(i)
            else:
                L.append(i)
            i -= 1

        if n < 256:
            aliases = array('B', [0]) * n
        else:
            aliases = array('H', [0]) * n

        while S and L:
            a = S.pop()
            g = L.pop()
            aliases[a] = g
            P[g] += P[a] - 1
            if P[g] < 1:
                S.append(g)
            else:
                L.append(g)

        while L:
            P[L.pop()] = 1

        while S:
            P[S.pop()] = 1

        self.probs = P
        self.aliases = aliases

    def next(self, rng_func):
        r1 = rng_func()
        r2 = rng_func()
        i = int(r1 * len(self.probs))
        return i if r2 < self.probs[i] else self.aliases[i]
