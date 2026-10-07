import unittest

from retroasset.c64prg import (
    CODE_ADDRESS, COLOR_SOURCE, SCREEN_SOURCE, TAIL_BYTES, export_viewer_prg,
)
from retroasset.petscii import C64Screen, PetsciiCell


class C64PrgLayoutTests(unittest.TestCase):
    def setUp(self):
        self.screen = C64Screen(
            40, 25,
            tuple(PetsciiCell(i & 0x7f, i & 0x0f) for i in range(1000)),
        )
        self.prg = export_viewer_prg(self.screen)

    def offset(self, address: int) -> int:
        load = int.from_bytes(self.prg[:2], "little")
        return 2 + address - load

    def test_basic_next_line_pointer_targets_end_marker(self):
        self.assertEqual(self.prg[2:4], bytes([0x0b, 0x08]))

    def test_machine_code_starts_at_sys_address(self):
        self.assertEqual(CODE_ADDRESS, 2061)
        self.assertEqual(self.prg[self.offset(CODE_ADDRESS):self.offset(CODE_ADDRESS)+2], bytes([0xa2, 0x00]))

    def test_payload_is_page_aligned(self):
        self.assertEqual(self.prg[self.offset(SCREEN_SOURCE)], 0x00)
        self.assertEqual(self.prg[self.offset(COLOR_SOURCE)], 0x00)
        self.assertEqual(COLOR_SOURCE - SCREEN_SOURCE, 1024)

    def test_first_copy_source_is_screen_payload(self):
        off = self.offset(CODE_ADDRESS)
        self.assertEqual(self.prg[off+3:off+5], SCREEN_SOURCE.to_bytes(2, "little"))

    def test_full_page_branch_returns_to_lda(self):
        off = self.offset(CODE_ADDRESS)
        self.assertEqual(self.prg[off+9:off+11], bytes([0xd0, 0xf7]))

    def test_tail_is_bounded_to_232_bytes(self):
        tail = self.offset(CODE_ADDRESS) + 3 * 11
        self.assertEqual(TAIL_BYTES, 232)
        self.assertEqual(self.prg[tail+9:tail+13], bytes([0xe0, 0xe8, 0xd0, 0xf5]))


if __name__ == "__main__":
    unittest.main()
