#
# utils.py
#
# Copyright © 2020 Foundation Devices, Inc.
# Licensed under the "BSD-2-Clause Plus Patent License"
#


# def data_to_hex(buf):
#     return "".join("{:02x}".format(x) for x in buf)


def int_to_bytes(n):
    # return n.to_bytes((n.bit_length() + 7) // 8, 'big')
    return n.to_bytes(4, "big")


# def bytes_to_int(buf):
#     return int.from_bytes(buf, "big")


# def string_to_bytes(s):
#     return bytes(s, "utf8")


def is_ur_type(ch):
    ch = ch.decode() if isinstance(ch, bytes) else ch
    return ("a" <= ch <= "z") or ("0" <= ch <= "9") or (ch == "-")


# Split the given sequence into two parts returned in a tuple
# The first entry in the tuple has the first `count` values.
# The second entry in the tuple has the remaining values.
# def split(buf, count):
#     mv = memoryview(buf)
#     return mv[:count], mv[count:]


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
    count = len(target)
    assert count == len(source)
    for i in range(count):
        target[i] ^= source[i]


def xor_with(target, b):
    xor_into(target, b)
    return target


def take_first(s, count):
    return s[:count]


# def drop_first(s, count):
#     return s[count:]
