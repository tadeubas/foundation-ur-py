#
# utils.py
#
# Copyright © 2020 Foundation Devices, Inc.
# Licensed under the "BSD-2-Clause Plus Patent License"
#


def int_to_bytes(n):
    # return n.to_bytes((n.bit_length() + 7) // 8, 'big')
    return n.to_bytes(4, "big")


def is_ur_type(_type):
    if isinstance(_type, str):
        _type = _type.encode()
    for o in _type:
        return (
            (97 <= o <= 122) or (65 <= o <= 90) or (48 <= o <= 57) or (o == 45)
        )  # a–z  # A–Z  # 0–9  # '-'


def join_bytes(chunks):
    total = 0
    for c in chunks:
        total += len(c)

    out = bytearray(total)
    pos = 0
    for c in chunks:
        l = len(c)
        out[pos : pos + l] = c
        pos += l

    return out


def xor_into(target, source):
    for i, b in enumerate(source):
        target[i] ^= b

