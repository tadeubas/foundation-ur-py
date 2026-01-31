#
# ur.py
#
# Copyright © 2020 Foundation Devices, Inc.
# Licensed under the "BSD-2-Clause Plus Patent License"
#

# VERSION 2.0.0


def is_ur_type(_type):
    if isinstance(_type, str):
        _type = _type.encode()
    for o in _type:
        return (
            (97 <= o <= 122) or (65 <= o <= 90) or (48 <= o <= 57) or (o == 45)
        )  # a–z  # A–Z  # 0–9  # '-'


class UR:
    def __init__(self, _type, cbor):
        _type = _type.upper()
        if not is_ur_type(_type):
            raise ValueError("Invalid UR type")
        self.type = _type
        self.cbor = cbor
