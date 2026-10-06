import struct

from .petscii import C64Screen, export_color_ram, export_screen_ram

LOAD_ADDRESS = 0x0801
CODE_ADDRESS = 0x080D
SCREEN_SOURCE = 0x0900
COLOR_SOURCE = 0x0D00
SCREEN_DEST = 0x0400
COLOR_DEST = 0xD800
VISIBLE_CELLS = 1000
TAIL_BYTES = VISIBLE_CELLS - 3 * 256


def export_viewer_prg(screen: C64Screen) -> bytes:
    if screen.columns != 40 or screen.rows != 25:
        raise ValueError("M0.7 PRG viewer requires a 40x25 C64 screen")

    # $0801 BASIC line: 10 SYS2061. The link points at the $080b end marker.
    basic = bytes([
        0x0b, 0x08,
        0x0a, 0x00,
        0x9e,
        0x32, 0x30, 0x36, 0x31,
        0x00,
        0x00, 0x00,
    ])

    def page_copy(src: int, dst: int) -> bytes:
        return bytes([
            0xa2, 0x00,
            0xbd, src & 0xff, src >> 8,
            0x9d, dst & 0xff, dst >> 8,
            0xe8,
            0xd0, 0xf7,
        ])

    def tail_copy(src: int, dst: int) -> bytes:
        return bytes([
            0xa2, 0x00,
            0xbd, src & 0xff, src >> 8,
            0x9d, dst & 0xff, dst >> 8,
            0xe8,
            0xe0, TAIL_BYTES,
            0xd0, 0xf5,
        ])

    code = bytearray()
    for page in range(3):
        code.extend(page_copy(SCREEN_SOURCE + page * 256, SCREEN_DEST + page * 256))
    code.extend(tail_copy(SCREEN_SOURCE + 3 * 256, SCREEN_DEST + 3 * 256))
    for page in range(3):
        code.extend(page_copy(COLOR_SOURCE + page * 256, COLOR_DEST + page * 256))
    code.extend(tail_copy(COLOR_SOURCE + 3 * 256, COLOR_DEST + 3 * 256))
    code.append(0x60)

    if CODE_ADDRESS + len(code) > SCREEN_SOURCE:
        raise AssertionError("viewer code overlaps screen payload")

    prefix = struct.pack("<H", LOAD_ADDRESS) + basic + bytes(code)
    loaded_prefix_size = len(prefix) - 2
    pad_to_screen = SCREEN_SOURCE - (LOAD_ADDRESS + loaded_prefix_size)
    if pad_to_screen < 0:
        raise AssertionError("invalid C64 PRG layout")

    screen_data = export_screen_ram(screen).ljust(1024, b"\x20")
    color_data = export_color_ram(screen).ljust(1024, b"\x00")
    return prefix + bytes(pad_to_screen) + screen_data + color_data
