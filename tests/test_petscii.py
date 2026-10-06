import unittest

from retroasset.petscii import C64Screen, PetsciiCell, export_color_ram, export_screen_ram


class C64ScreenTests(unittest.TestCase):
    def test_native_planes(self):
        screen = C64Screen(
            2, 1,
            (PetsciiCell(1, 2), PetsciiCell(65, 14)),
        )
        self.assertEqual(export_screen_ram(screen), bytes([1, 65]))
        self.assertEqual(export_color_ram(screen), bytes([2, 14]))

    def test_color_range(self):
        with self.assertRaises(ValueError):
            PetsciiCell(65, 16)


if __name__ == "__main__":
    unittest.main()
