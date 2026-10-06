import struct
import unittest

from retroasset.amiga import byterun1_decode, byterun1_encode, decode_ilbm, encode_ilbm, encode_ilbm_compressed, pack_planar, row_bytes
from retroasset.indexed import IndexedBitmap


class AmigaExportTests(unittest.TestCase):
    def setUp(self):
        self.bitmap = IndexedBitmap(
            16, 2,
            tuple([0, 1] * 8 + [1, 0] * 8),
            ((0, 0, 0), (255, 255, 255)),
        )

    def test_word_aligned_rows(self):
        self.assertEqual(row_bytes(1), 2)
        self.assertEqual(row_bytes(16), 2)
        self.assertEqual(row_bytes(17), 4)

    def test_planar_fixture(self):
        self.assertEqual(pack_planar(self.bitmap), bytes.fromhex("5555aaaa"))

    def test_ilbm_form(self):
        data = encode_ilbm(self.bitmap)
        self.assertEqual(data[:4], b"FORM")
        self.assertEqual(data[8:12], b"ILBM")
        self.assertEqual(struct.unpack(">I", data[4:8])[0], len(data) - 8)
        self.assertIn(b"BMHD", data)
        self.assertIn(b"CMAP", data)
        self.assertIn(b"BODY", data)

    def test_ilbm_round_trip(self):
        decoded = decode_ilbm(encode_ilbm(self.bitmap))
        self.assertEqual(decoded, self.bitmap)

    def test_byterun1(self):
        source = b"AAAABCDDDDDDDXYZ"
        encoded = byterun1_encode(source)
        self.assertEqual(byterun1_decode(encoded, len(source)), source)

    def test_compressed_ilbm_header(self):
        data = encode_ilbm_compressed(self.bitmap)
        self.assertEqual(data[:4], b"FORM")
        self.assertIn(b"BODY", data)

    def test_compressed_ilbm_round_trip(self):
        decoded = decode_ilbm(encode_ilbm_compressed(self.bitmap))
        self.assertEqual(decoded, self.bitmap)

    def test_byterun1_rejects_truncated_literal(self):
        with self.assertRaisesRegex(ValueError, "truncated ByteRun1 literal"):
            byterun1_decode(bytes([2, 0xaa]), 3)

    def test_byterun1_rejects_row_overflow(self):
        with self.assertRaisesRegex(ValueError, "exceeds expected size"):
            byterun1_decode(bytes([0xfd, 0xaa]), 2)


if __name__ == "__main__":
    unittest.main()
