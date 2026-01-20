#
# ur.py
#
# Copyright © 2020 Foundation Devices, Inc.
# Licensed under the "BSD-2-Clause Plus Patent License"
#

# VERSION 2.0.0

from .utils import is_ur_type


# STAY
class UR:
    def __init__(self, _type, cbor):
        _type = _type.upper()
        if not is_ur_type(_type):
            raise ValueError("Invalid UR type")
        self.type = _type
        self.cbor = cbor

    # def __eq__(self, obj):
    #     if obj is None:
    #         return False
    #     return self.type == obj.type and self.cbor == obj.cbor
