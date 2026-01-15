#
# test.py
#
# Copyright © 2020 Foundation Devices, Inc.
# Licensed under the "BSD-2-Clause Plus Patent License"
#

try:
    import unittest
except:
    unittest = None

from test_utils import make_message, make_message_ur, next_data

from ur.bytewords import STYLE_MINIMAL
from ur.bytewords.bytewords_decode import BytewordsDecoder
from ur.bytewords.bytewords_encode import BytewordsEncoder
from ur.utils import xor_into
from ur.xoshiro256 import Xoshiro256
from ur.random_sampler import RandomSampler
from ur.fountain_utils import shuffled, choose_degree, choose_fragments
from ur.fountain_encoder import FountainEncoder, Part
from ur.fountain_decoder import FountainDecoder
from ur.ur_encoder import UREncoder
from ur.ur_decoder import URDecoder
from ur.crc32 import crc32


def data_to_hex(buf):
    return "".join("{:02x}".format(x) for x in buf)

def check_crc32(input, expected_hex):
    checksum = crc32(bytes(input, 'utf8'))
    hex = '{:x}'.format(checksum)
    return hex == expected_hex

if unittest == None:
    BaseClass = object
else:
    BaseClass = unittest.TestCase

class TestUR(BaseClass):
    def assertRaises(self, exc_type, func):
        if unittest == None:
            raised_exc = None
            try:
                func()
            except exc_type as e:
                raised_exc = e
            if not raised_exc:
                assert("{0} was not raised".format(exc_type))
        else:
            return super().assertRaises(exc_type, func)

    def test_crc32(self):
        assert check_crc32("Hello, world!", "ebe6c6e6")
        assert check_crc32("Wolf", "598c84dc")

    def test_bytewords_1(self):
        input = bytes([0, 1, 2, 128, 255])
        # assert(BytewordsEncoder.encode(STYLE_STANDARD, input) == "able acid also lava zoom jade need echo taxi")
        # assert(BytewordsEncoder.encode(STYLE_URI, input) == "able-acid-also-lava-zoom-jade-need-echo-taxi")
        assert(BytewordsEncoder.encode(STYLE_MINIMAL, input) == "aeadaolazmjendeoti")

        # assert(BytewordsDecoder.decode(STYLE_STANDARD, "ABLE acid also lava zoom jade need echo taxi") == input)
        # assert(BytewordsDecoder.decode(STYLE_URI, "able-ACID-also-lava-zoom-jade-need-echo-taxi") == input)
        assert(BytewordsDecoder.decode(STYLE_MINIMAL, "AEadaolazmjendeoTI") == input)

        # bad checksum
        # self.assertRaises(ValueError, lambda: BytewordsDecoder.decode(STYLE_STANDARD, "able acid also lava zoom jade need echo wolf"))
        # self.assertRaises(ValueError, lambda: BytewordsDecoder.decode(STYLE_URI, "able-acid-also-lava-zoom-jade-need-echo-wolf"))

        self.assertRaises(ValueError, lambda: BytewordsDecoder.decode(STYLE_MINIMAL, "aeadaolazmjendeowf"))

        # too short
        # self.assertRaises(ValueError, lambda: BytewordsDecoder.decode(STYLE_STANDARD, "wolf"))
        # self.assertRaises(ValueError, lambda: BytewordsDecoder.decode(STYLE_STANDARD, ""))

    def test_bytewords_2(self):
        input = bytes([
            245, 215, 20, 198, 241, 235, 69, 59, 209, 205,
            165, 18, 150, 158, 116, 135, 229, 212, 19, 159,
            17, 37, 239, 240, 253, 11, 109, 191, 37, 242,
            38, 120, 223, 41, 156, 189, 242, 254, 147, 204,
            66, 163, 216, 175, 191, 72, 169, 54, 32, 60,
            144, 230, 210, 137, 184, 197, 33, 113, 88, 14,
            157, 31, 177, 46, 1, 115, 205, 69, 225, 150,
            65, 235, 58, 144, 65, 240, 133, 69, 113, 247,
            63, 53, 242, 165, 160, 144, 26, 13, 79, 237,
            133, 71, 82, 69, 254, 165, 138, 41, 85, 24
        ])

        encoded = \
            "yank toys bulb skew when warm free fair tent swan " + \
            "open brag mint noon jury list view tiny brew note " + \
            "body data webs what zinc bald join runs data whiz " + \
            "days keys user diet news ruby whiz zone menu surf " + \
            "flew omit trip pose runs fund part even crux fern " + \
            "math visa tied loud redo silk curl jugs hard beta " + \
            "next cost puma drum acid junk swan free very mint " + \
            "flap warm fact math flap what limp free jugs yell " + \
            "fish epic whiz open numb math city belt glow wave " + \
            "limp fuel grim free zone open love diet gyro cats " + \
            "fizz holy city puff"

        encoded_minimal = \
            "yktsbbswwnwmfefrttsnonbgmtnnjyltvwtybwne" + \
            "bydawswtzcbdjnrsdawzdsksurdtnsrywzzemusf" + \
            "fwottppersfdptencxfnmhvatdldroskcljshdba" + \
            "ntctpadmadjksnfevymtfpwmftmhfpwtlpfejsyl" + \
            "fhecwzonnbmhcybtgwwelpflgmfezeonledtgocs" + \
            "fzhycypf"

        # assert(BytewordsEncoder.encode(STYLE_STANDARD, input) == encoded)
        assert(BytewordsEncoder.encode(STYLE_MINIMAL, input) == encoded_minimal)
        # assert(BytewordsDecoder.decode(STYLE_STANDARD, encoded) == input)
        assert(BytewordsDecoder.decode(STYLE_MINIMAL, encoded_minimal) == input)


    def test_rng_1(self):
        rng = Xoshiro256.from_bytes(b"Wolf")
        numbers = []
        for i in range(100):
            numbers.append(rng.next() % 100)

        expected_numbers = [42, 81, 85, 8, 82, 84, 76, 73, 70, 88, 2, 74, 40, 48, 77, 54, 88, 7, 5, 88, 37, 25, 82, 13, 69, 59, 30, 39, 11, 82, 19, 99, 45, 87, 30, 15, 32, 22, 89, 44, 92, 77, 29, 78, 4, 92, 44, 68, 92, 69, 1, 42, 89, 50, 37, 84, 63, 34, 32, 3, 17, 62, 40, 98, 82, 89, 24, 43, 85, 39, 15, 3, 99, 29, 20, 42, 27, 10, 85, 66, 50, 35, 69, 70, 70, 74, 30, 13, 72, 54, 11, 5, 70, 55, 91, 52, 10, 43, 43, 52]
        assert(numbers == expected_numbers)

    # def test_rng_2(self):
    #     checksum = bytes_to_int(crc32_bytes(string_to_bytes("Wolf")))
    #     rng = Xoshiro256.from_crc32(checksum)
    #     numbers  = []
    #     for i in range(100):
    #         numbers.append(rng.next() % 100)

    #     expected_numbers = [88, 44, 94, 74, 0, 99, 7, 77, 68, 35, 47, 78, 19, 21, 50, 15, 42, 36, 91, 11, 85, 39, 64, 22, 57, 11, 25, 12, 1, 91, 17, 75, 29, 47, 88, 11, 68, 58, 27, 65, 21, 54, 47, 54, 73, 83, 23, 58, 75, 27, 26, 15, 60, 36, 30, 21, 55, 57, 77, 76, 75, 47, 53, 76, 9, 91, 14, 69, 3, 95, 11, 73, 20, 99, 68, 61, 3, 98, 36, 98, 56, 65, 14, 80, 74, 57, 63, 68, 51, 56, 24, 39, 53, 80, 57, 51, 81, 3, 1, 30]
    #     assert(numbers == expected_numbers)

    def test_rng_3(self):
        rng = Xoshiro256.from_bytes(b"Wolf")
        numbers = []
        for i in range(100):
            numbers.append(rng.next_int(1, 10))

        expected_numbers = [6, 5, 8, 4, 10, 5, 7, 10, 4, 9, 10, 9, 7, 7, 1, 1, 2, 9, 9, 2, 6, 4, 5, 7, 8, 5, 4, 2, 3, 8, 7, 4, 5, 1, 10, 9, 3, 10, 2, 6, 8, 5, 7, 9, 3, 1, 5, 2, 7, 1, 4, 4, 4, 4, 9, 4, 5, 5, 6, 9, 5, 1, 2, 8, 3, 3, 2, 8, 4, 3, 2, 1, 10, 8, 9, 3, 10, 8, 5, 5, 6, 7, 10, 5, 8, 9, 4, 6, 4, 2, 10, 2, 1, 7, 9, 6, 7, 4, 2, 5]
        assert(numbers == expected_numbers)

    def test_find_fragment_length(self):
        assert(FountainEncoder.find_nominal_fragment_length(12345, 1005, 1955) == 1764)
        assert(FountainEncoder.find_nominal_fragment_length(12345, 1005, 30000) == 12345)

    def test_random_sampler(self):
        probs = [ 1, 2, 4, 8 ]
        sampler = RandomSampler(probs)
        rng = Xoshiro256.from_bytes(b"Wolf")
        samples = []
        f = lambda: rng.next_double()
        for i in range(500):
            samples.append(sampler.next(f))

        expected_samples = [3, 3, 3, 3, 3, 3, 3, 0, 2, 3, 3, 3, 3, 1, 2, 2, 1, 3, 3, 2, 3, 3, 1, 1, 2, 1, 1, 3, 1, 3, 1, 2, 0, 2, 1, 0, 3, 3, 3, 1, 3, 3, 3, 3, 1, 3, 2, 3, 2, 2, 3, 3, 3, 3, 2, 3, 3, 0, 3, 3, 3, 3, 1, 2, 3, 3, 2, 2, 2, 1, 2, 2, 1, 2, 3, 1, 3, 0, 3, 2, 3, 3, 3, 3, 3, 3, 3, 3, 2, 3, 1, 3, 3, 2, 0, 2, 2, 3, 1, 1, 2, 3, 2, 3, 3, 3, 3, 2, 3, 3, 3, 3, 3, 2, 3, 1, 2, 1, 1, 3, 1, 3, 2, 2, 3, 3, 3, 1, 3, 3, 3, 3, 3, 3, 3, 3, 2, 3, 2, 3, 3, 1, 2, 3, 3, 1, 3, 2, 3, 3, 3, 2, 3, 1, 3, 0, 3, 2, 1, 1, 3, 1, 3, 2, 3, 3, 3, 3, 2, 0, 3, 3, 1, 3, 0, 2, 1, 3, 3, 1, 1, 3, 1, 2, 3, 3, 3, 0, 2, 3, 2, 0, 1, 3, 3, 3, 2, 2, 2, 3, 3, 3, 3, 3, 2, 3, 3, 3, 3, 2, 3, 3, 2, 0, 2, 3, 3, 3, 3, 2, 1, 1, 1, 2, 1, 3, 3, 3, 2, 2, 3, 3, 1, 2, 3, 0, 3, 2, 3, 3, 3, 3, 0, 2, 2, 3, 2, 2, 3, 3, 3, 3, 1, 3, 2, 3, 3, 3, 3, 3, 2, 2, 3, 1, 3, 0, 2, 1, 3, 3, 3, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 2, 2, 2, 3, 1, 1, 3, 2, 2, 0, 3, 2, 1, 2, 1, 0, 3, 3, 3, 2, 2, 3, 2, 1, 2, 0, 0, 3, 3, 2, 3, 3, 2, 3, 3, 3, 3, 3, 2, 2, 2, 3, 3, 3, 3, 3, 1, 1, 3, 2, 2, 3, 1, 1, 0, 1, 3, 2, 3, 3, 2, 3, 3, 2, 3, 3, 2, 2, 2, 2, 3, 2, 2, 2, 2, 2, 1, 2, 3, 3, 2, 2, 2, 2, 3, 3, 2, 0, 2, 1, 3, 3, 3, 3, 0, 3, 3, 3, 3, 2, 2, 3, 1, 3, 3, 3, 2, 3, 3, 3, 2, 3, 3, 3, 3, 2, 3, 2, 1, 3, 3, 3, 3, 2, 2, 0, 1, 2, 3, 2, 0, 3, 3, 3, 3, 3, 3, 1, 3, 3, 2, 3, 2, 2, 3, 3, 3, 3, 3, 2, 2, 3, 3, 2, 2, 2, 1, 3, 3, 3, 3, 1, 2, 3, 2, 3, 3, 2, 3, 2, 3, 3, 3, 2, 3, 1, 2, 3, 2, 1, 1, 3, 3, 2, 3, 3, 2, 3, 3, 0, 0, 1, 3, 3, 2, 3, 3, 3, 3, 1, 3, 3, 0, 3, 2, 3, 3, 1, 3, 3, 3, 3, 3, 3, 3, 0, 3, 3, 2]
        assert(samples == expected_samples)

    def test_shuffle(self):
        rng = Xoshiro256.from_bytes(b"Wolf")
        values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        result = []
        for i in range(10):
            result.append(shuffled(values.copy(), rng))

        expectedResult = [
            [6, 4, 9, 3, 10, 5, 7, 8, 1, 2],
            [10, 8, 6, 5, 1, 2, 3, 9, 7, 4],
            [6, 4, 5, 8, 9, 3, 2, 1, 7, 10],
            [7, 3, 5, 1, 10, 9, 4, 8, 2, 6],
            [8, 5, 7, 10, 2, 1, 4, 3, 9, 6],
            [4, 3, 5, 6, 10, 2, 7, 8, 9, 1],
            [5, 1, 3, 9, 4, 6, 2, 10, 7, 8],
            [2, 1, 10, 8, 9, 4, 7, 6, 3, 5],
            [6, 7, 10, 4, 8, 9, 2, 3, 1, 5],
            [10, 2, 1, 7, 9, 5, 6, 3, 4, 8]
        ]
        assert(result == expectedResult)

    def test_partition_and_join(self):
        message = make_message(1024)
        fragment_len = FountainEncoder.find_nominal_fragment_length(len(message), 10, 100)
        fragments = FountainEncoder.partition_message(message, fragment_len)
        fragments_hex = []
        for f in fragments:
            fragments_hex.append(data_to_hex(f))
        

        expected_fragments = [
            "916ec65cf77cadf55cd7f9cda1a1030026ddd42e905b77adc36e4f2d3ccba44f7f04f2de44f42d84c374a0e149136f25b01852545961d55f7f7a8cde6d0e2ec43f3b2dcb644a2209e8c9e34af5c4747984a5e873c9cf5f965e25ee29039f",
            "df8ca74f1c769fc07eb7ebaec46e0695aea6cbd60b3ec4bbff1b9ffe8a9e7240129377b9d3711ed38d412fbb4442256f1e6f595e0fc57fed451fb0a0101fb76b1fb1e1b88cfdfdaa946294a47de8fff173f021c0e6f65b05c0a494e50791",
            "270a0050a73ae69b6725505a2ec8a5791457c9876dd34aadd192a53aa0dc66b556c0c215c7ceb8248b717c22951e65305b56a3706e3e86eb01c803bbf915d80edcd64d4d41977fa6f78dc07eecd072aae5bc8a852397e06034dba6a0b570",
            "797c3a89b16673c94838d884923b8186ee2db5c98407cab15e13678d072b43e406ad49477c2e45e85e52ca82a94f6df7bbbe7afbed3a3a830029f29090f25217e48d1f42993a640a67916aa7480177354cc7440215ae41e4d02eae9a1912",
            "33a6d4922a792c1b7244aa879fefdb4628dc8b0923568869a983b8c661ffab9b2ed2c149e38d41fba090b94155adbed32f8b18142ff0d7de4eeef2b04adf26f2456b46775c6c20b37602df7da179e2332feba8329bbb8d727a138b4ba7a5",
            "03215eda2ef1e953d89383a382c11d3f2cad37a4ee59a91236a3e56dcf89f6ac81dd4159989c317bd649d9cbc617f73fe10033bd288c60977481a09b343d3f676070e67da757b86de27bfca74392bac2996f7822a7d8f71a489ec6180390",
            "089ea80a8fcd6526413ec6c9a339115f111d78ef21d456660aa85f790910ffa2dc58d6a5b93705caef1091474938bd312427021ad1eeafbd19e0d916ddb111fabd8dcab5ad6a6ec3a9c6973809580cb2c164e26686b5b98cfb017a337968",
            "c7daaa14ae5152a067277b1b3902677d979f8e39cc2aafb3bc06fcf69160a853e6869dcc09a11b5009f91e6b89e5b927ab1527a735660faa6012b420dd926d940d742be6a64fb01cdc0cff9faa323f02ba41436871a0eab851e7f5782d10",
            "fbefde2a7e9ae9dc1e5c2c48f74f6c824ce9ef3c89f68800d44587bedc4ab417cfb3e7447d90e1e417e6e05d30e87239d3a5d1d45993d4461e60a0192831640aa32dedde185a371ded2ae15f8a93dba8809482ce49225daadfbb0fec629e",
            "23880789bdf9ed73be57fa84d555134630e8d0f7df48349f29869a477c13ccca9cd555ac42ad7f568416c3d61959d0ed568b2b81c7771e9088ad7fd55fd4386bafbf5a528c30f107139249357368ffa980de2c76ddd9ce4191376be0e6b5",
            "170010067e2e75ebe2d2904aeb1f89d5dc98cd4a6f2faaa8be6d03354c990fd895a97feb54668473e9d942bb99e196d897e8f1b01625cf48a7b78d249bb4985c065aa8cd1402ed2ba1b6f908f63dcd84b66425df00000000000000000000"
        ]
        assert(fragments_hex == expected_fragments)
        rejoined_message = FountainDecoder.join_fragments(fragments, len(message))
        assert(message == rejoined_message)

    def test_choose_degree(self):
        message = make_message(1024)
        fragment_len = FountainEncoder.find_nominal_fragment_length(len(message), 10, 100)
        fragments = FountainEncoder.partition_message(message, fragment_len)
        degrees = []
        for nonce in range(1, 201):
            part_rng = Xoshiro256.from_bytes(bytes("Wolf-{}".format(nonce), 'utf-8'))
            degrees.append(choose_degree(len(fragments), part_rng))

        expected_degrees = [11, 3, 6, 5, 2, 1, 2, 11, 1, 3, 9, 10, 10, 4, 2, 1, 1, 2, 1, 1, 5, 2, 4, 10, 3, 2, 1, 1, 3, 11, 2, 6, 2, 9, 9, 2, 6, 7, 2, 5, 2, 4, 3, 1, 6, 11, 2, 11, 3, 1, 6, 3, 1, 4, 5, 3, 6, 1, 1, 3, 1, 2, 2, 1, 4, 5, 1, 1, 9, 1, 1, 6, 4, 1, 5, 1, 2, 2, 3, 1, 1, 5, 2, 6, 1, 7, 11, 1, 8, 1, 5, 1, 1, 2, 2, 6, 4, 10, 1, 2, 5, 5, 5, 1, 1, 4, 1, 1, 1, 3, 5, 5, 5, 1, 4, 3, 3, 5, 1, 11, 3, 2, 8, 1, 2, 1, 1, 4, 5, 2, 1, 1, 1, 5, 6, 11, 10, 7, 4, 7, 1, 5, 3, 1, 1, 9, 1, 2, 5, 5, 2, 2, 3, 10, 1, 3, 2, 3, 3, 1, 1, 2, 1, 3, 2, 2, 1, 3, 8, 4, 1, 11, 6, 3, 1, 1, 1, 1, 1, 3, 1, 2, 1, 10, 1, 1, 8, 2, 7, 1, 2, 1, 9, 2, 10, 2, 1, 3, 4, 10]
        assert(degrees == expected_degrees)

    def test_choose_fragments(self):
        message = make_message(1024)
        checksum = crc32(message)
        fragment_len = FountainEncoder.find_nominal_fragment_length(len(message), 10, 100)
        fragments = FountainEncoder.partition_message(message, fragment_len)
        fragment_indexes = []
        for seq_num in range(1, 31):
            indexes_set = choose_fragments(seq_num, len(fragments), checksum)
            indexes = list(indexes_set)
            indexes.sort()
            fragment_indexes.append(indexes)

        expected_fragment_indexes = [
            [0],
            [1],
            [2],
            [3],
            [4],
            [5],
            [6],
            [7],
            [8],
            [9],
            [10],
            [9],
            [2, 5, 6, 8, 9, 10],
            [8],
            [1, 5],
            [1],
            [0, 2, 4, 5, 8, 10],
            [5],
            [2],
            [2],
            [0, 1, 3, 4, 5, 7, 9, 10],
            [0, 1, 2, 3, 5, 6, 8, 9, 10],
            [0, 2, 4, 5, 7, 8, 9, 10],
            [3, 5],
            [4],
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            [0, 1, 3, 4, 5, 6, 7, 9, 10],
            [6],
            [5, 6],
            [7]
        ]
        assert(fragment_indexes == expected_fragment_indexes)

    def test_xor(self):
        rng = Xoshiro256.from_bytes(b"Wolf")
        data1 = next_data(rng, 10)
        assert(data_to_hex(data1) == "916ec65cf77cadf55cd7")
        data2 = next_data(rng,10)
        assert(data_to_hex(data2) == "f9cda1a1030026ddd42e")
        data3 = data1[:]
        xor_into(data3, data2)
        assert(data_to_hex(data3) == "68a367fdf47c8b2888f9")
        xor_into(data3, data1)
        assert(data3 == data2)

    def test_fountain_encoder(self):
        message = make_message(256)
        encoder = FountainEncoder(message, 30)
        parts = []

        def description(part):
            return "seqNum:{}, seqLen:{}, messageLen:{}, checksum:{}, data:{}".format(
                part.seq_num,
                part.seq_len,
                part.message_len,
                part.checksum,
                data_to_hex(part.data),
            )

        for i in range(20):
            parts.append(description(encoder.next_part()))

        expected_parts = [
            "seqNum:1, seqLen:9, messageLen:256, checksum:23570951, data:916ec65cf77cadf55cd7f9cda1a1030026ddd42e905b77adc36e4f2d3c",
            "seqNum:2, seqLen:9, messageLen:256, checksum:23570951, data:cba44f7f04f2de44f42d84c374a0e149136f25b01852545961d55f7f7a",
            "seqNum:3, seqLen:9, messageLen:256, checksum:23570951, data:8cde6d0e2ec43f3b2dcb644a2209e8c9e34af5c4747984a5e873c9cf5f",
            "seqNum:4, seqLen:9, messageLen:256, checksum:23570951, data:965e25ee29039fdf8ca74f1c769fc07eb7ebaec46e0695aea6cbd60b3e",
            "seqNum:5, seqLen:9, messageLen:256, checksum:23570951, data:c4bbff1b9ffe8a9e7240129377b9d3711ed38d412fbb4442256f1e6f59",
            "seqNum:6, seqLen:9, messageLen:256, checksum:23570951, data:5e0fc57fed451fb0a0101fb76b1fb1e1b88cfdfdaa946294a47de8fff1",
            "seqNum:7, seqLen:9, messageLen:256, checksum:23570951, data:73f021c0e6f65b05c0a494e50791270a0050a73ae69b6725505a2ec8a5",
            "seqNum:8, seqLen:9, messageLen:256, checksum:23570951, data:791457c9876dd34aadd192a53aa0dc66b556c0c215c7ceb8248b717c22",
            "seqNum:9, seqLen:9, messageLen:256, checksum:23570951, data:951e65305b56a3706e3e86eb01c803bbf915d80edcd64d4d0000000000",
            "seqNum:10, seqLen:9, messageLen:256, checksum:23570951, data:330f0f33a05eead4f331df229871bee733b50de71afd2e5a79f196de09",
            "seqNum:11, seqLen:9, messageLen:256, checksum:23570951, data:3b205ce5e52d8c24a52cffa34c564fa1af3fdffcd349dc4258ee4ee828",
            "seqNum:12, seqLen:9, messageLen:256, checksum:23570951, data:dd7bf725ea6c16d531b5f03254783803048ca08b87148daacd1cd7a006",
            "seqNum:13, seqLen:9, messageLen:256, checksum:23570951, data:760be7ad1c6187902bbc04f539b9ee5eb8ea6833222edea36031306c01",
            "seqNum:14, seqLen:9, messageLen:256, checksum:23570951, data:5bf4031217d2c3254b088fa7553778b5003632f46e21db129416f65b55",
            "seqNum:15, seqLen:9, messageLen:256, checksum:23570951, data:73f021c0e6f65b05c0a494e50791270a0050a73ae69b6725505a2ec8a5",
            "seqNum:16, seqLen:9, messageLen:256, checksum:23570951, data:b8546ebfe2048541348910267331c643133f828afec9337c318f71b7df",
            "seqNum:17, seqLen:9, messageLen:256, checksum:23570951, data:23dedeea74e3a0fb052befabefa13e2f80e4315c9dceed4c8630612e64",
            "seqNum:18, seqLen:9, messageLen:256, checksum:23570951, data:d01a8daee769ce34b6b35d3ca0005302724abddae405bdb419c0a6b208",
            "seqNum:19, seqLen:9, messageLen:256, checksum:23570951, data:3171c5dc365766eff25ae47c6f10e7de48cfb8474e050e5fe997a6dc24",
            "seqNum:20, seqLen:9, messageLen:256, checksum:23570951, data:e055c2433562184fa71b4be94f262e200f01c6f74c284b0dc6fae6673f"
        ]
        assert(parts == expected_parts)


    def test_fountain_encoder_cbor(self):
        message = make_message(256)
        encoder = FountainEncoder(message, 30)
        parts = []
        for i in range(20):
            parts.append(data_to_hex(encoder.next_part().cbor()))

        expected_parts = [
            "8501091901001a0167aa07581d916ec65cf77cadf55cd7f9cda1a1030026ddd42e905b77adc36e4f2d3c",
            "8502091901001a0167aa07581dcba44f7f04f2de44f42d84c374a0e149136f25b01852545961d55f7f7a",
            "8503091901001a0167aa07581d8cde6d0e2ec43f3b2dcb644a2209e8c9e34af5c4747984a5e873c9cf5f",
            "8504091901001a0167aa07581d965e25ee29039fdf8ca74f1c769fc07eb7ebaec46e0695aea6cbd60b3e",
            "8505091901001a0167aa07581dc4bbff1b9ffe8a9e7240129377b9d3711ed38d412fbb4442256f1e6f59",
            "8506091901001a0167aa07581d5e0fc57fed451fb0a0101fb76b1fb1e1b88cfdfdaa946294a47de8fff1",
            "8507091901001a0167aa07581d73f021c0e6f65b05c0a494e50791270a0050a73ae69b6725505a2ec8a5",
            "8508091901001a0167aa07581d791457c9876dd34aadd192a53aa0dc66b556c0c215c7ceb8248b717c22",
            "8509091901001a0167aa07581d951e65305b56a3706e3e86eb01c803bbf915d80edcd64d4d0000000000",
            "850a091901001a0167aa07581d330f0f33a05eead4f331df229871bee733b50de71afd2e5a79f196de09",
            "850b091901001a0167aa07581d3b205ce5e52d8c24a52cffa34c564fa1af3fdffcd349dc4258ee4ee828",
            "850c091901001a0167aa07581ddd7bf725ea6c16d531b5f03254783803048ca08b87148daacd1cd7a006",
            "850d091901001a0167aa07581d760be7ad1c6187902bbc04f539b9ee5eb8ea6833222edea36031306c01",
            "850e091901001a0167aa07581d5bf4031217d2c3254b088fa7553778b5003632f46e21db129416f65b55",
            "850f091901001a0167aa07581d73f021c0e6f65b05c0a494e50791270a0050a73ae69b6725505a2ec8a5",
            "8510091901001a0167aa07581db8546ebfe2048541348910267331c643133f828afec9337c318f71b7df",
            "8511091901001a0167aa07581d23dedeea74e3a0fb052befabefa13e2f80e4315c9dceed4c8630612e64",
            "8512091901001a0167aa07581dd01a8daee769ce34b6b35d3ca0005302724abddae405bdb419c0a6b208",
            "8513091901001a0167aa07581d3171c5dc365766eff25ae47c6f10e7de48cfb8474e050e5fe997a6dc24",
            "8514091901001a0167aa07581de055c2433562184fa71b4be94f262e200f01c6f74c284b0dc6fae6673f"
        ]
        assert(parts == expected_parts)

    def test_fountain_encoder_is_complete(self):
        message = make_message(256)
        encoder = FountainEncoder(message, 30)
        generated_parts_count = 0
        while not encoder.is_complete():
            encoder.next_part()
            generated_parts_count += 1

        assert(encoder.seq_len() == generated_parts_count)

    
    def test_process_mixed_part_non_simple(self):
        d = FountainDecoder()

        # Fake expected state (normally set by validate_part)
        d.expected_part_indexes = {0, 1, 2}

        # Create a mixed part: indexes {0,1}
        p = FountainDecoder.Part(
            indexes={0, 1},
            data=bytearray(b'\x01\x02\x03')
        )

        assert not p.is_simple()

        d.process_mixed_part(p)

        # It should be stored as a mixed part
        assert p.indexes in d.mixed_parts
        assert d.mixed_parts[p.indexes] is p


    def test_process_mixed_part_reduces_to_simple(self):
        d = FountainDecoder()

        # Known simple part
        simple = FountainDecoder.Part(
            indexes={0},
            data=bytearray(b'\x01\x02')
        )
        d.simple_parts[simple.indexes] = simple

        # Mixed part including that index
        mixed = FountainDecoder.Part(
            indexes={0, 1},
            data=bytearray(b'\x05\x06')
        )

        d.process_mixed_part(mixed)

        # Reduction should enqueue a simple part
        assert len(d.queued_parts) == 1
        reduced = d.queued_parts[0]
        assert reduced.is_simple()
        assert reduced.indexes == {1}



    def test_fountain_decoder(self):
        message_seed = b"Wolf"
        message_size = 32767
        max_fragment_len = 1000

        message = make_message(message_size, message_seed)
        encoder = FountainEncoder(message, max_fragment_len, 100)
        decoder = FountainDecoder()

        # Emulating a do-while loop from the original reference code
        while True:
            part = encoder.next_part()
            decoder.receive_part(part)
            if decoder.is_complete():
                break

        if decoder.is_success():
            assert(decoder.result_message() == message)
        else:
            print(decoder.result_error())
            assert(False)

    def test_fountain_cbor(self):
        part = Part(12, 8, 100, 0x12345678, bytes([1, 5, 3, 3 ,5]))
        cbor = part.cbor()
        part2 = Part.from_cbor(cbor)
        cbor2 = part2.cbor()
        assert(cbor == cbor2)

    def test_single_part_ur(self):
        ur = make_message_ur(50)
        expected = "ur:bytes/hdeymejtswhhylkepmykhhtsytsnoyoyaxaedsuttydmmhhpktpmsrjtgwdpfnsboxgwlbaawzuefywkdplrsrjynbvygabwjldapfcsdwkbrkch"

        # ENCODER
        # without FountainEncoder obj
        encoded = UREncoder.encode(ur)
        assert(encoded == expected)
        # with FountainEncoder obj
        ue = UREncoder(ur, 9999)
        encoded_2 = ue.next_part()
        assert(encoded_2 == expected)

        # DECODER
        # with FountainDecoder obj
        ud = URDecoder()
        ud.receive_part(encoded)
        assert(ud.result == ur)
        assert(ud.result.type == ur.type)
        assert(ud.result.cbor == ur.cbor)
        # without FountainDecoder obj
        decoded = URDecoder.decode(encoded)
        assert(ur == decoded)
        assert(ur.type == decoded.type)
        assert(ur.cbor == decoded.cbor)

    # Added this test to check GitHub issue #3
    def test_short_crc32(self):
        fragment = "ur:crypto-psbt/20-29/lpbbcscacfcmcpcybbrsptskhdssdtsbtkdechrhpkhkvwmdmnksgdaoaeaeaeaeaechptbbeodkpletlbldamjopmbnpeplwmfzltzthgoeqzteltlgaychaeaeaeaeaechptbbfxsawkidltenbskpjlfeflmnclpkemtpwpmhmhioltkecsamaeaeaeaeaechptbbintkmwzmynknkezcbgkthdfezopaynprmefthpkgltaeaeaeaeadaddnemmdaaaeaeaeaeaecpaecxhdgwfdvtsphdolbnkigeteeclkosoxlpjssnfxsgclahesjsvturdyjzcwsrkndtadahtkghclaofstdlnuysaasiesfdnrkhsmnjztonlpsldwftdmninoxehhnkotodrwpchrorhdaclaeetwdvl"

        decoder = URDecoder()
        status = decoder.receive_part(fragment)
        assert(status)

    def test_ur_encoder(self):
        ur = make_message_ur(256)
        encoder = UREncoder(ur, 30)
        parts = []
        for i in range(20):
            parts.append(encoder.next_part())

        expected_parts = [
            "ur:bytes/1-9/lpadascfadaxcywenbpljkhdcahkadaemejtswhhylkepmykhhtsytsnoyoyaxaedsuttydmmhhpktpmsrjtdkgslpgh",
            "ur:bytes/2-9/lpaoascfadaxcywenbpljkhdcagwdpfnsboxgwlbaawzuefywkdplrsrjynbvygabwjldapfcsgmghhkhstlrdcxaefz",
            "ur:bytes/3-9/lpaxascfadaxcywenbpljkhdcahelbknlkuejnbadmssfhfrdpsbiegecpasvssovlgeykssjykklronvsjksopdzmol",
            "ur:bytes/4-9/lpaaascfadaxcywenbpljkhdcasotkhemthydawydtaxneurlkosgwcekonertkbrlwmplssjtammdplolsbrdzcrtas",
            "ur:bytes/5-9/lpahascfadaxcywenbpljkhdcatbbdfmssrkzmcwnezelennjpfzbgmuktrhtejscktelgfpdlrkfyfwdajldejokbwf",
            "ur:bytes/6-9/lpamascfadaxcywenbpljkhdcackjlhkhybssklbwefectpfnbbectrljectpavyrolkzczcpkmwidmwoxkilghdsowp",
            "ur:bytes/7-9/lpatascfadaxcywenbpljkhdcavszmwnjkwtclrtvaynhpahrtoxmwvwatmedibkaegdosftvandiodagdhthtrlnnhy",
            "ur:bytes/8-9/lpayascfadaxcywenbpljkhdcadmsponkkbbhgsoltjntegepmttmoonftnbuoiyrehfrtsabzsttorodklubbuyaetk",
            "ur:bytes/9-9/lpasascfadaxcywenbpljkhdcajskecpmdckihdyhphfotjojtfmlnwmadspaxrkytbztpbauotbgtgtaeaevtgavtny",
            "ur:bytes/10-9/lpbkascfadaxcywenbpljkhdcahkadaemejtswhhylkepmykhhtsytsnoyoyaxaedsuttydmmhhpktpmsrjtwdkiplzs",
            "ur:bytes/11-9/lpbdascfadaxcywenbpljkhdcahelbknlkuejnbadmssfhfrdpsbiegecpasvssovlgeykssjykklronvsjkvetiiapk",
            "ur:bytes/12-9/lpbnascfadaxcywenbpljkhdcarllaluzmdmgstospeyiefmwejlwtpedamktksrvlcygmzemovovllarodtmtbnptrs",
            "ur:bytes/13-9/lpbtascfadaxcywenbpljkhdcamtkgtpknghchchyketwsvwgwfdhpgmgtylctotzopdrpayoschcmhplffziachrfgd",
            "ur:bytes/14-9/lpbaascfadaxcywenbpljkhdcapazewnvonnvdnsbyleynwtnsjkjndeoldydkbkdslgjkbbkortbelomueekgvstegt",
            "ur:bytes/15-9/lpbsascfadaxcywenbpljkhdcaynmhpddpzmversbdqdfyrehnqzlugmjzmnmtwmrouohtstgsbsahpawkditkckynwt",
            "ur:bytes/16-9/lpbeascfadaxcywenbpljkhdcawygekobamwtlihsnpalnsghenskkiynthdzotsimtojetprsttmukirlrsbtamjtpd",
            "ur:bytes/17-9/lpbyascfadaxcywenbpljkhdcamklgftaxykpewyrtqzhydntpnytyisincxmhtbceaykolduortotiaiaiafhiaoyce",
            "ur:bytes/18-9/lpbgascfadaxcywenbpljkhdcahkadaemejtswhhylkepmykhhtsytsnoyoyaxaedsuttydmmhhpktpmsrjtntwkbkwy",
            "ur:bytes/19-9/lpbwascfadaxcywenbpljkhdcadekicpaajootjzpsdrbalpeywllbdsnbinaerkurspbncxgslgftvtsrjtksplcpeo",
            "ur:bytes/20-9/lpbbascfadaxcywenbpljkhdcayapmrleeleaxpasfrtrdkncffwjyjzgyetdmlewtkpktgllepfrltataztksmhkbot"
        ]
        assert(parts == expected_parts)

    def test_multipart_ur(self):
        ur = make_message_ur(32767)
        max_fragment_len = 1000
        first_seq_num = 100
        encoder = UREncoder(ur, max_fragment_len, first_seq_num)
        decoder = URDecoder()
        while True:
            part = encoder.next_part()
            decoder.receive_part(part)
            if decoder.is_complete():
                break

        if decoder.is_success():
            assert(decoder.result.type == ur.type)
            assert(decoder.result.cbor == ur.cbor)
        else:
            print('{}'.format(decoder.result))
            assert(False)

    def test_ur_lib(self):
        from test_utils import UR

        _max = 100
        data_type = 'crypto-psbt'
        data = bytearray(b'Y\x04\x06psbt\xff\x01\x00\xfd`\x01\x02\x00\x00\x00\x01\x90ise[\xdb!G\x12%\xfb\xfd\x1c:\xa54\xde=\x1bO\x063\x17\x8a2\xce\xc8\xb3*\x12\x7fc\x00\x00\x00\x00\x00\xfd\xff\xff\xff\x07\xf4\x01\x00\x00\x00\x00\x00\x00"\x00 0\xb4}\xac\x18\x19R\x0c\xc9\x03\xcb\xff/\xcf\xd9\x81\xa8\xdf\xfe\x88\x94y\x07\xb6\xcc_}vf\xbaL\x7fP\x04\x00\x00\x00\x00\x00\x00"\x00 \x00\x13\x8e\xc7}\nGV\xe0\x07\xc4\xa4\x98\x9e\xf7\xcf3\nl&_\xd9\x1f\xc9\x91\xb6\xcasC\xfbo\x19\xf4\x01\x00\x00\x00\x00\x00\x00"\x00 \xbb\xfa\xa7\xb3\x8c\xe5\xc7\xb3\xc2Y\xe5\x89\xb2\x0c\x97ooX\x0c{Y\xc3;j\x81\x87,\n9+u\t\xf4\x01\x00\x00\x00\x00\x00\x00"\x00 q\x02%\\\xafX\xa41\x03\xbbIY\xa1\xe5\r\tJ\x83b\x84\x96\x1fyz+\x95y]\xd41\xfb\x1f\xf4\x01\x00\x00\x00\x00\x00\x00"\x00 \xb82\xad\xf3\xb9\xea\xd2\x80\xdbms-\\\xf4\xd5\xf7\x1aH\xae\xe9\xbe;w\xb8@\x06\xce\x10g\x9eE(\xf4\x01\x00\x00\x00\x00\x00\x00"\x00 \xb42\xd77p?a[>P\xc5\x8d4F\xe2\x97X\x96\xd2\x95)W\xd1\xae\xf5\xb3O\x14\xcf.\x1f\xca\xf4\x01\x00\x00\x00\x00\x00\x00"\x00 \xfdD\xdc0\xb4z\x08K\xe1\x87\xf1\xaf~\xca~?)\xc9\xf1\x92nS\xb4mP\x06\xd7Y81y4G\xb8\x01\x00O\x01\x045\x87\xcf\x04}\xdd\x07`\x80\x00\x00\x02\xb4_\xb8o)\xa0\xd2\x19\xe1q\xc1\xf4\xfb\x1d\x1d4!^B\xc2\xe0d3\x97\xffL\x9a\x19\xf4\xc3\xb0\x9c\x03\x9c\xe4\xb9\x9a\x8e\x8b\xf5\xcc\xff\xa9\x92\xd07\xe0SKQ\xe3\xf5\x86\x90\xfa \xd4\x1f\xf4<\xf37s\x9c\x10\x14\xe6P"\x990\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x02\x00\x00\x80O\x01\x045\x87\xcf\x04\x81\xf9\xee\xcb\x80\x00\x00\x02Z\xc2\x8d\x17\x94&\xa5&E\x95\x85\xd0\xe4\xf4Z\x1d\xa3\xfd\xb8\x06N\xa8\xf9\x8b\x91\xb3\xfd\x02,\xa6\x0e\xdc\x02w\x99\x9fjA{Z\xdcg\x1f\xb63\x90\x97i\x02s\xcag\xe5\x91\xfb\x11\xe6\x19\xeeX[\xc0\xba\xcfQ\x14\xe0\xc5\x95\xc50\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x02\x00\x00\x80\x00\x01\x01+\xa0\x12\x00\x00\x00\x00\x00\x00"\x00 y}\xb8v\x98\\\xfd\x8ah\xef\xeb\xca,1\x00\xcc\x17\xe7\x18|\x06\r\x8e7\xb6\xfe?\xa8\xbf<\xc2\xd5\x01\x03\x04\x01\x00\x00\x00\x01\x05GR!\x02\x83\xedx@\x12\xf8j\xefH#\x7f\xac\xa0\x86\xdb\xa8\xe6K\x17_/\x87\xdf\x8e\x8a\xa3s\x8c\x7f\xd28\xaf!\x03V\xcd\x14+{\xa2\xa5\xb4\xe4\xdc)\xd8\xedi\x1b\xcf"\xcb\xbdw\x049Ow\x14\xb1\r\xd3$\x0b\x9c\x05R\xae"\x06\x02\x83\xedx@\x12\xf8j\xefH#\x7f\xac\xa0\x86\xdb\xa8\xe6K\x17_/\x87\xdf\x8e\x8a\xa3s\x8c\x7f\xd28\xaf\x1c\xe6P"\x990\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x02\x00\x00\x80\x01\x00\x00\x00\x00\x00\x00\x00"\x06\x03V\xcd\x14+{\xa2\xa5\xb4\xe4\xdc)\xd8\xedi\x1b\xcf"\xcb\xbdw\x049Ow\x14\xb1\r\xd3$\x0b\x9c\x05\x1c\xe0\xc5\x95\xc50\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x02\x00\x00\x80\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01GR!\x02\x8a\xb6:e\x88\xafo\xb9*\x901\xd5\xed\x13D\xaf\xce\x80\xbf\xf9\x1a\x13D\xac_6gL\xdd\x01\xf2E!\x03\xb3\xb6\xc8\x13\x11kM\xb0GK[o\x8e\x16^\x90\xbc\x82\xf6\xb5^\xbd\xfc\x97y\x17\x03\xa9\xe0w\x840R\xae"\x02\x03\xb3\xb6\xc8\x13\x11kM\xb0GK[o\x8e\x16^\x90\xbc\x82\xf6\xb5^\xbd\xfc\x97y\x17\x03\xa9\xe0w\x840\x1c\xe6P"\x990\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x02\x00\x00\x80\x01\x00\x00\x00\x01\x00\x00\x00"\x02\x02\x8a\xb6:e\x88\xafo\xb9*\x901\xd5\xed\x13D\xaf\xce\x80\xbf\xf9\x1a\x13D\xac_6gL\xdd\x01\xf2E\x1c\xe0\xc5\x95\xc50\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x02\x00\x00\x80\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        ur = UR(data_type, data)
        encoder = UREncoder(ur, _max, first_seq_num=8044)

        # hardcode created parts
        arbitrary_parts = []
        arbitrary_parts.append(b'UR:CRYPTO-PSBT/8045-11/LPCFCTJNBDCFAAASCYJKGHYTJKHDHYMHFRUTASRDCKTLTKMTFDAXLNJPBKYTWDASCYWEWEASPYROMETTCFRLNTZSRFLKETFMFNEOHFHKHHWNSNCERFOYNTOLCSMTTKHLVASEGYFXURGUAATLLNQZZMPYBZRPKSSGSOGSRFTLBKCSFHBKNSYKRPCFWZGEMNDPGOEEHYHPDAZOKSIMTAQZNYKNCFLTNDYLME')
        arbitrary_parts.append(b'UR:CRYPTO-PSBT/8047-11/LPCFCTJLBDCFAAASCYJKGHYTJKHDHYAECPLACXREEOZTMSIDFHHSHPFMGDSKPEEEIYNDWDVTVTGESOTYUTRHFPCKKKIADATKVOAYDPWPKIAMBTMNEMRPZECAPDNESELNASEHRLKBASGRVYLTWTPKESMKHEFSPKDKLDTDKEPYUELFCSDAPDYKMKRLOENSOYWFCMHEHNLNUYRKBTJZKTWNOETLHDRDMEBYPR')
        arbitrary_parts.append(b'UR:CRYPTO-PSBT/8048-11/LPCFCTJOBDCFAAASCYJKGHYTJKHDHYPETOAERNYTCYMUFYPSHERPIHGSUTLYWFFECLAXPRRPSPBWEOINGWFTWNJSFMVDCLKKVDRDDWQDCNHDGTYTGUHKYTPDZSQDWFEODEJLIESOJTURAOFPWFTYWFTYZELOLAFLGRUYJTMNCMUEMHRFLFKORLHYRYKEMTKKCHAXPDVTKTLRDYCEVAGDCPNLDYDAWPPLLA')
        arbitrary_parts.append(b'UR:CRYPTO-PSBT/8049-11/LPCFCTJSBDCFAAASCYJKGHYTJKHDHYPETOLARSYTCYBWFYPSHEENIOGSUTADWZFECLAXQDRPSPBWBYJEGTPFFLGRHPJLMNCMHYMHRFLFYNREHYRYZTMSKKCHAXPTVTKTLRDYGMPLCPAOAXQDRPSPBWBYJEGTPFFLGRHPJLMNCMHYMHRFLFYNREHYRYZTMSKKCHAXPTVTKTLRDYCEVAGDCPNLDYLOKNCXPR')
        arbitrary_parts.append(b'UR:CRYPTO-PSBT/8050-11/LPCFCTJPBDCFAAASCYJKGHYTJKHDHYAEAEAEAEAEAEAECPAMAXHFSNBBDNKGOEONQZVEUODTTPWEINCWTKCPSBRYKTAAESGWKTBBPABTTEDKBDNSAHCEVTSKMDSKDYAEAELAADAEAELAAEAEAELAAOAEAELAADAEAEAEAEAEAEAEAEAEADADFLGMCLAOLERPFTIHLOPEJLRHDRMHEHTLWEBWFYNTWTTNOS')
        arbitrary_parts.append(b'UR:CRYPTO-PSBT/8060-11/LPCFCTKEBDCFAAASCYJKGHYTJKHDHYAEAEAEAEAEAEAECPAMAXHFSNBBDNKGOEONQZVEUODTTPWEINCWTKCPSBRYKTAAESGWKTBBPABTTEDKBDNSAHCEVTSKMDSKDYAEAELAADAEAELAAEAEAELAAOAEAELAADAEAEAEAEAEAEAEAEAEADADFLGMCLAOLERPFTIHLOPEJLRHDRMHEHTLWEBWFYHFKSFYZE')
        arbitrary_parts.append(b'UR:CRYPTO-PSBT/8061-11/LPCFCTKIBDCFAAASCYJKGHYTJKHDHYASWKADAEAEAEAEAEAECPAECXJSAODAHHPEHDOXEHAXRKGAHKOYVWBTASGELSIDLRMTCTKKKNDNMDKKHLTYEHZOCTWKADAEAEAEAEAEAECPAECXROEYPMWFRHWDTDLAUYJNJKDPHHWKTLYLCYFDPLWLRNFRKTROFZAMTOBEIONNFEDEWKADAEAEAEAEAEBDBYLTBZ')
        arbitrary_parts.append(b'UR:CRYPTO-PSBT/8062-11/LPCFCTKBBDCFAAASCYJKGHYTJKHDHYHKAAAMJOJKIDJYZMADAEZCHNADAOAEAEAEADMHINJKIHHPUYCLFLBGDAZOZCCEFTONEEUEFSCWGWAMEOCHLEEYTOSPQDDRBGLBIAAEAEAEAEAEZCZMZMZMATWKADAEAEAEAEAEAECPAECXDYQZKIPSCSCFGMBNSOAXSBZMDLTKTALYPDURZELOMWKKATURCFVTFZ')
        arbitrary_parts.append(b'UR:CRYPTO-PSBT/8071-11/LPCFCTLTBDCFAAASCYJKGHYTJKHDHYFZAMHKPRZCCTYNHGRTBSTKATGTURADTIFECPWDLTKISPHYGYSGLELGUYRKJENDCLDNETPLPTPRTKTAFGKGMKBNLAJSPLYNRYLDSOHYFDHYCPAOZEGSFDEYGUMDGRJLLOGDMWPDWNPARKCPDRJPIHLBRSSNOTEMTSINSTTPWTJEGEVYMUVDFLHYWTCFKNIDURZELG')
        arbitrary_parts.append(b'UR:CRYPTO-PSBT/8073-11/LPCFCTLDBDCFAAASCYJKGHYTJKHDHYAEAEAEAEAEAEAECPAMAXHFSNBBDNKGOEONQZVEUODTTPWEINCWTKCPSBRYKTAAESGWKTBBPABTTEDKBDNSAHCEVTSKMDSKDYAEAELAADAEAELAAEAEAELAAOAEAELAADAEAEAEAEAEAEAEAEAEADADFLGMCLAOLERPFTIHLOPEJLRHDRMHEHTLWEBWFYHGKBWNAX')
        arbitrary_parts.append(b'UR:CRYPTO-PSBT/8074-11/LPCFCTLEBDCFAAASCYJKGHYTJKHDHYTADSLNGUJKBSNDOSHDNETOCXUECNLRKSTKHTJLSBBKPMSBPLWDKOKNPKSBIOFPMKWNHNHPZOUTATBSNLSOPYKTRKNLRERHJTPEDKMYTTHFBZKPVSBNUYRPRHDLYKBADAFTSWHSWFHSNBDNDYMHEOFECPDEPYRHMYRKGEZMHSTOHLRPDLBEKNRDFDKNGMRTLEOLRS')
        arbitrary_parts.append(b'UR:CRYPTO-PSBT/8075-11/LPCFCTLUBDCFAAASCYJKGHYTJKHDHYASWKADAEAEAEAEAEAECPAECXJSAODAHHPEHDOXEHAXRKGAHKOYVWBTASGELSIDLRMTCTKKKNDNMDKKHLTYEHZOCTWKADAEAEAEAEAEAECPAECXROEYPMWFRHWDTDLAUYJNJKDPHHWKTLYLCYFDPLWLRNFRKTROFZAMTOBEIONNFEDEWKADAEAEAEAEAENDSBYNCF')
        arbitrary_parts.append(b'UR:CRYPTO-PSBT/8077-11/LPCFCTLGBDCFAAASCYJKGHYTJKHDHYRPSFHEKIKOIYRDGSLBGDAAAEAEAEAEAEAECPAECXAEBWMNSTKIBKFLHFVTATSSOXMKNNYLTKEOBKJZDSHETACTSOMERPSGJKFXZOJLCFWKADAEAEAEAEAEAECPAECXRKZSOSQDLKVWSTQDSAHKVWLDPRBNMSJLJLHDBNKGHKSRFRIMLYLTDWBKESDNKPVTCPSNSN')
        arbitrary_parts.append(b'UR:CRYPTO-PSBT/8078-11/LPCFCTMNBDCFAAASCYJKGHYTJKHDHYPEAXAXKTKSDIHGWPRTNYGORYVOKKNTFXHLKIGHSODNHLFSWSWSMHFYVLMDBYETPLPYSTDIWSJKLEWECEGAKPAEFMPFPTWSFSLELNBYDPRHSRGTFDMUZEOYLNJPGTDIBBPLDRCLWNTYBNFTRLESGLDARODMMOCENBJKCHHEHSAMUYRKBTWPKPWNOEGOHKNTDIVTAO')
        arbitrary_parts.append(b'UR:CRYPTO-PSBT/8079-11/LPCFCTMYBDCFAAASCYJKGHYTJKHDHYAEAEAEAEAEAEAECPAMAXHFSNBBDNKGOEONQZVEUODTTPWEINCWTKCPSBRYKTAAESGWKTBBPABTTEDKBDNSAHCEVTSKMDSKDYAEAELAADAEAELAAEAEAELAAOAEAELAADAEAEAEAEAEAEAEAEAEADADFLGMCLAOLERPFTIHLOPEJLRHDRMHEHTLWEBWFYPERPKBNB')
        arbitrary_parts.append(b'UR:CRYPTO-PSBT/8080-11/LPCFCTMHBDCFAAASCYJKGHYTJKHDHYETFTTAEEBAREECFGBZQZEOJNASAETLUYEEEMEHWZCPHNTYWERLOSLYMUEEADWFKTGHMTOLSWHGSNJECKFEIMQDJKJOBYTBWKZMLFMWRKOLZMHKRTLFJPJKDWTPFMDPCXWSGLYKPDGMVAKSOXGHFNKICHADBAWTATDISPGMKBMWRFSSIDIYMNKBGHJYHTMHSNSGHL')

        # dinamically creates the same hardcoded parts above
        arbitrary_parts2 = []
        arbitrary_parts2.append(encoder.next_part())
        encoder.next_part() # miss 1
        for i in range(4):
            arbitrary_parts2.append(encoder.next_part())
        for i in range(9):
            encoder.next_part() # miss 9
        for i in range(3):
            arbitrary_parts2.append(encoder.next_part())
        for i in range(8):
            encoder.next_part() # miss 8
        arbitrary_parts2.append(encoder.next_part())
        encoder.next_part() # miss 1
        for i in range(3):
            arbitrary_parts2.append(encoder.next_part())
        encoder.next_part() # miss 1
        for i in range(4):
            arbitrary_parts2.append(encoder.next_part())

        # convert to uppercase binary as arbitrary_parts
        for i, elem in enumerate(arbitrary_parts2):
            arbitrary_parts2[i] = elem.encode().upper()

        assert(arbitrary_parts == arbitrary_parts2)

        decoder = URDecoder()
        for part in arbitrary_parts:
            decoder.receive_part(part.decode())

        assert(decoder.is_complete())
        assert(decoder.is_success())
        assert(decoder.result.cbor == data)

if __name__ == '__main__':
    if unittest != None:
        unittest.main()
