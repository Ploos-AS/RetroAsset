import unittest

from retroasset.model import AssetManifest
from retroasset.targets import validate


class AmigaOCSTests(unittest.TestCase):
    def test_valid_manifest(self):
        result = validate(AssetManifest("hero", "amiga-ocs", "sprite", 32, 48, 16))
        self.assertTrue(result.ok)

    def test_too_many_colors(self):
        result = validate(AssetManifest("hero", "amiga-ocs", "bitmap", 320, 256, 64))
        self.assertFalse(result.ok)


if __name__ == "__main__":
    unittest.main()
