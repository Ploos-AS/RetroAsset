import unittest

from retroasset.c64prg import export_viewer_prg
from retroasset.petscii import C64Screen, PetsciiCell, interpret_petscii


class C64PrgTests(unittest.TestCase):
    def test_stream_state(self):
        screen = interpret_petscii(bytes([0x05, 0x41, 0x12, 0x42, 0x92]), 2, 1)
        self.assertEqual(screen.cells[0], PetsciiCell(0x01, 1))
        self.assertEqual(screen.cells[1], PetsciiCell(0x82, 1))

    def test_prg_load_address_and_basic_stub(self):
        screen = C64Screen(40, 25, tuple(PetsciiCell(0x20, 1) for _ in range(1000)))
        data = export_viewer_prg(screen)
        self.assertEqual(data[:2], bytes([0x01, 0x08]))
        self.assertIn(bytes([0x9e]) + b"2061", data[:16])
        self.assertGreater(len(data), 2000)


if __name__ == "__main__":
    unittest.main()
