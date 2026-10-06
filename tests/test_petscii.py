import unittest

from retroasset.petscii import C64Screen, PetsciiCell, export_color_ram, export_screen_ram, petscii_to_screen_code, screen_code_to_petscii


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

    def test_common_petscii_mapping(self):
        self.assertEqual(petscii_to_screen_code(0x41), 0x01)
        self.assertEqual(screen_code_to_petscii(0x01), 0x41)
        self.assertEqual(petscii_to_screen_code(0x20), 0x20)

    def test_control_code_is_not_silently_mapped(self):
        with self.assertRaises(ValueError):
            petscii_to_screen_code(0x0d)


if __name__ == "__main__":
    unittest.main()
