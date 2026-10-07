import unittest

from retroasset.model import AssetManifest
from retroasset.targets import validate


class AmigaTargetValidationTests(unittest.TestCase):
    def test_bitmap_is_export_ready_and_reports_planar_memory(self):
        result = validate(AssetManifest("checker", "amiga-ocs", "bitmap", 16, 2, 2))
        self.assertTrue(result.export_ready)
        self.assertEqual(result.memory_bytes, 4)

    def test_ocs_rejects_too_many_colors(self):
        result = validate(AssetManifest("too-many", "amiga-ocs", "bitmap", 320, 256, 64))
        self.assertFalse(result.export_ready)

    def test_sprite_and_bob_accept_hotspot_hook(self):
        for kind in ("sprite", "bob"):
            result = validate(AssetManifest(kind, "amiga-ocs", kind, 16, 16, 4, {"hotspot": [8, 8]}))
            self.assertTrue(result.export_ready)

    def test_bad_hotspot_is_rejected(self):
        result = validate(AssetManifest("sprite", "amiga-ocs", "sprite", 16, 16, 4, {"hotspot": [8]}))
        self.assertFalse(result.export_ready)

    def test_tiles_require_valid_divisible_tile_size(self):
        missing = validate(AssetManifest("tiles", "amiga-ocs", "tileset", 32, 32, 4))
        self.assertFalse(missing.export_ready)
        good = validate(AssetManifest("tiles", "amiga-ocs", "tileset", 32, 32, 4, {"tile_size": [16, 16]}))
        self.assertTrue(good.export_ready)
        bad = validate(AssetManifest("tiles", "amiga-ocs", "tileset", 30, 32, 4, {"tile_size": [16, 16]}))
        self.assertFalse(bad.export_ready)

    def test_incomplete_amiga_manifest_is_not_export_ready(self):
        result = validate(AssetManifest("draft", "amiga-ocs", "bitmap"))
        self.assertFalse(result.export_ready)
        self.assertIsNone(result.memory_bytes)


if __name__ == "__main__":
    unittest.main()
