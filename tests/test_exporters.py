import unittest

from retroasset.exporters import export_asm, export_c, export_raw_planar
from retroasset.indexed import IndexedBitmap


class ExporterTests(unittest.TestCase):
    def setUp(self):
        self.bitmap = IndexedBitmap(
            16, 2,
            tuple([0, 1] * 8 + [1, 0] * 8),
            ((0, 0, 0), (255, 255, 255)),
        )

    def test_raw(self):
        self.assertEqual(export_raw_planar(self.bitmap), bytes.fromhex("5555aaaa"))

    def test_c(self):
        text = export_c(self.bitmap, "checker")
        self.assertIn("#define CHECKER_WIDTH 16", text)
        self.assertIn("0x55, 0x55, 0xaa, 0xaa", text)

    def test_asm(self):
        text = export_asm(self.bitmap, "checker")
        self.assertIn("checker_width equ 16", text)
        self.assertIn("dc.b $55,$55,$aa,$aa", text)
        self.assertIn("dc.w $000,$fff", text)


if __name__ == "__main__":
    unittest.main()
