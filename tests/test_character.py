import unittest

from retroasset.character import CharacterAsset, CharacterCell


class CharacterAssetTests(unittest.TestCase):
    def test_geometry(self):
        asset = CharacterAsset(2, 1, (CharacterCell(65), CharacterCell(66)))
        self.assertEqual(asset.expected_cells(), 2)


if __name__ == "__main__":
    unittest.main()
