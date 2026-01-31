#
# utils.py
#
# Copyright © 2020 Foundation Devices, Inc.
# Licensed under the "BSD-2-Clause Plus Patent License"
#


def xor_into(target, source):
    source = memoryview(source)
    for i, b in enumerate(source):
        target[i] ^= b
