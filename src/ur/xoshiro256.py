#
# xoshiro256.py
#
# Copyright © 2020 Foundation Devices, Inc.
# Licensed under the "BSD-2-Clause Plus Patent License"
#

try:
    import uhashlib as hashlib
except:
    import hashlib

from ur.constants import MAX_UINT64

# Original Info:
# Written in 2018 by David Blackman and Sebastiano Vigna (vigna@acm.org)

# To the extent possible under law, the author has dedicated all copyright
# and related and neighboring rights to this software to the public domain
# worldwide. This software is distributed without any warranty.

# See <http://creativecommons.org/publicdomain/zero/1.0/>.

# This is xoshiro256** 1.0, one of our all-purpose, rock-solid
# generators. It has excellent (sub-ns) speed, a state (256 bits) that is
# large enough for any parallel application, and it passes all tests we
# are aware of.

# For generating just floating-point numbers, xoshiro256+ is even faster.

# The state must be seeded so that it is not everywhere zero. If you have
# a 64-bit seed, we suggest to seed a splitmix64 generator and use its
# output to fill s.


def rotl(x, k):
    return ((x << k) | (x >> (64 - k))) & MAX_UINT64


class Xoshiro256:

    _INV_M = 1.0 / (float(MAX_UINT64) + 1.0)

    def __init__(self, arr=None):
        self.s = [0] * 4
        if arr is not None:
            self.s[0] = arr[0]
            self.s[1] = arr[1]
            self.s[2] = arr[2]
            self.s[3] = arr[3]

    def _hash_then_set_s(self, buf):
        m = hashlib.sha256()
        m.update(buf)
        d = m.digest()

        s = self.s
        for i in range(4):
            o = i << 3  # * 8
            s[i] = (
                (d[o] << 56)
                | (d[o + 1] << 48)
                | (d[o + 2] << 40)
                | (d[o + 3] << 32)
                | (d[o + 4] << 24)
                | (d[o + 5] << 16)
                | (d[o + 6] << 8)
                | d[o + 7]
            )

    @classmethod
    def from_bytes(cls, buf):
        x = cls()
        x._hash_then_set_s(buf)
        return x

    def next(self):
        result = (rotl((self.s[1] * 5) & MAX_UINT64, 7) * 9) & MAX_UINT64
        t = (self.s[1] << 17) & MAX_UINT64

        self.s[2] ^= self.s[0]
        self.s[3] ^= self.s[1]
        self.s[1] ^= self.s[2]
        self.s[0] ^= self.s[3]

        self.s[2] ^= t

        self.s[3] = rotl(self.s[3], 45) & MAX_UINT64

        return result

    def next_double(self):
        return self.next() * Xoshiro256._INV_M

    def next_int(self, low, high):
        return int(self.next_double() * (high - low + 1) + low) & MAX_UINT64
