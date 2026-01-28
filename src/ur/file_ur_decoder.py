#
# Copyright © 2020 Foundation Devices, Inc. and Contributors
# Licensed under the "BSD-2-Clause Plus Patent License"
#

from .ur_decoder import URDecoder
from .file_fountain_decoder import FileFountainDecoder


class FileURDecoder(URDecoder):
    """
    UR decoder that uses a FileFountainDecoder to minimize RAM usage.
    """

    def __init__(self, workdir):
        super().__init__()
        self.fountain_decoder = FileFountainDecoder(workdir)
