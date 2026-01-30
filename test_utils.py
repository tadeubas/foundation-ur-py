#
# test_utils.py
#
# Copyright © 2020 Foundation Devices, Inc.
# Licensed under the "BSD-2-Clause Plus Patent License"
#

from ur.xoshiro256 import Xoshiro256
from ur.cbor_lite import CBOREncoder
from ur.constants import MAX_UINT64
from ur.ur import UR

def eq_for_tests(self, obj):
    if obj == None:
        return False
    return self.type == obj.type and self.cbor == obj.cbor

UR.__eq__ = eq_for_tests

def next_int(rng, low, high):
    return int(rng.next_double() * (high - low + 1) + low) & MAX_UINT64

def next_byte(rng):
    return next_int(rng, 0, 255)

def next_data(rng, count):
    result = bytearray(count)
    for i in range(count):
        result[i] = next_byte(rng)
    return result

def make_message(length, seed = b"Wolf"):
    rng = Xoshiro256.from_bytes(seed)
    return next_data(rng, length)

def make_message_ur(length, seed = b"Wolf"):
    message = make_message(length, seed)
    encoder = CBOREncoder()
    encoder.encodeBytes(message)
    
    return UR("bytes", encoder.get_bytes())
