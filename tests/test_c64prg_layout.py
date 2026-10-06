import unittest

from retroasset.c64prg import export_viewer_prg
from retroasset.petscii import C64Screen, PetsciiCell


class C64PrgLayoutTests(unittest.TestCase):
    def setUp(self):
        self.screen = C64Screen(
            40, 25,
            tuple(PetsciiCell(i & 0x7f, i & 0x0f) for i in range(1000)),
        )
        self.prg = export_viewer_prg(self.screen)

    def test_machine_code_starts_at_sys_address(self):
        load = int.from_bytes(self.prg[:2], "little")
        sys_addr = 2061
        offset = 2 + (sys_addr - load)
        self.assertEqual(offset, 14)
        self.assertEqual(self.prg[offset:offset + 2], bytes([0xa2, 0x00]))

    def test_first_copy_source_points_to_payload(self):
        load = int.from_bytes(self.prg[:2], "little")
        code_offset = 2 + (0x080d - load)
        code_size = 89
        payload_addr = 0x080d + code_size
        self.assertEqual(
            self.prg[code_offset + 3:code_offset + 5],
            payload_addr.to_bytes(2, "little"),
        )

    def test_branch_returns_to_lda_not_ldx(self):
        load = int.from_bytes(self.prg[:2], "little")
        code_offset = 2 + (0x080d - load)
        # BNE opcode at +9, operand -9 => next-PC + (-9) = LDA at +2.
        self.assertEqual(self.prg[code_offset + 9:code_offset + 11], bytes([0xd0, 0xf7]))


if __name__ == "__main__":
    unittest.main()
