#
# utils.py
#
# Copyright © 2020 Foundation Devices, Inc.
# Licensed under the "BSD-2-Clause Plus Patent License"
#


# def data_to_hex(buf):
#     return "".join("{:02x}".format(x) for x in buf)


# STAY
def int_to_bytes(n):
    # return n.to_bytes((n.bit_length() + 7) // 8, 'big')
    return n.to_bytes(4, "big")


# def bytes_to_int(buf):
#     return int.from_bytes(buf, "big")


# def string_to_bytes(s):
#     return bytes(s, "utf8")


# STAY
def is_ur_type(_type):
    for o in _type:
        if isinstance(o, str):
            o = ord(o)
        # if upper 'A'–'Z', get lower
        if 65 <= o <= 90:
            o += 32
        return (97 <= o <= 122) or (48 <= o <= 57) or (o == 45)  # a–z  # 0–9  # '-'


# Split the given sequence into two parts returned in a tuple
# The first entry in the tuple has the first `count` values.
# The second entry in the tuple has the remaining values.
# def split(buf, count):
#     mv = memoryview(buf)
#     return mv[:count], mv[count:]


# STAY
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


# STAY
def xor_into(target, source):
    for i, b in enumerate(source):
        target[i] ^= b


# STAY
def take_first(s, count):
    return s[:count]


# def drop_first(s, count):
#     return s[count:]
