import unittest

from retroasset.ansi import decode_ans, encode_ans
from retroasset.character import CharacterAsset, CharacterCell


class AnsiTests(unittest.TestCase):
    def test_native_cp437_output(self):
        asset = CharacterAsset(
            3, 1,
            (
                CharacterCell(ord("A"), 7, 0),
                CharacterCell(0xDB, 15, 1),
                CharacterCell(ord("B"), 7, 0),
            ),
        )
        data = encode_ans(asset)
        self.assertIn(b"A", data)
        self.assertIn(bytes([0xDB]), data)
        self.assertTrue(data.endswith(b"\x1b[0m"))

    def test_geometry_is_enforced(self):
        with self.assertRaises(ValueError):
            encode_ans(CharacterAsset(2, 1, (CharacterCell(65),)))

    def test_round_trip(self):
        asset = CharacterAsset(
            3, 1,
            (
                CharacterCell(ord("A"), 7, 0),
                CharacterCell(0xDB, 15, 1),
                CharacterCell(ord("B"), 7, 0),
            ),
        )
        self.assertEqual(decode_ans(encode_ans(asset), 3, 1), asset)


if __name__ == "__main__":
    unittest.main()
