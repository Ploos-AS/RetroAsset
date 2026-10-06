import struct

from .petscii import C64Screen, export_color_ram, export_screen_ram


def export_viewer_prg(screen: C64Screen) -> bytes:
    if screen.columns != 40 or screen.rows != 25:
        raise ValueError("M0.7 PRG viewer requires a 40x25 C64 screen")

    # $0801 BASIC line: 10 SYS2061
    basic = bytes([
        0x0b, 0x08,       # pointer to next BASIC line
        0x0a, 0x00,       # line 10
        0x9e,             # SYS token
        0x32, 0x30, 0x36, 0x31,  # "2061"
        0x00,
        0x00, 0x00,       # end of BASIC program
    ])

    # 6502 routine at $080d. Copy 1000 bytes in four pages from data
    # immediately following the routine. Screen data is followed by color data.
    # Uses self-contained absolute indexed loads/stores and four page loops.
    code = bytearray()
    screen_src = 0x080d + 0  # patched after code length is known

    # We emit four unrolled page-copy loops for screen RAM and color RAM.
    # Final page copies 232 useful bytes; remaining 24 bytes are harmless padding
    # inside screen/color memory and are supplied as zeros in the payload.
    def page_copy(src: int, dst: int):
        return bytes([
            0xa2, 0x00,                   # LDX #$00
            0xbd, src & 0xff, src >> 8,   # LDA src,X
            0x9d, dst & 0xff, dst >> 8,   # STA dst,X
            0xe8,                         # INX
            0xd0, 0xf7,                   # BNE back to LDA (relative -9)
        ])

    # Code size is deterministic: 8 page loops * 11 bytes + RTS.
    code_size = 8 * 11 + 1
    screen_src = 0x080d + code_size
    color_src = screen_src + 1024
    for page in range(4):
        code.extend(page_copy(screen_src + page * 256, 0x0400 + page * 256))
    for page in range(4):
        code.extend(page_copy(color_src + page * 256, 0xd800 + page * 256))
    code.append(0x60)  # RTS

    screen_data = export_screen_ram(screen).ljust(1024, b"\x20")
    color_data = export_color_ram(screen).ljust(1024, b"\x00")
    return struct.pack("<H", 0x0801) + basic + bytes(code) + screen_data + color_data
