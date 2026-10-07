from dataclasses import dataclass


@dataclass(frozen=True)
class PetsciiCell:
    """A native C64 character cell.

    screen_code is the value stored in screen RAM. color is the low nibble
    stored in color RAM. PETSCII stream bytes are a separate representation.
    """
    screen_code: int
    color: int = 1

    def __post_init__(self):
        if not 0 <= self.screen_code <= 255:
            raise ValueError("C64 screen code must be a byte")
        if not 0 <= self.color <= 15:
            raise ValueError("C64 color must be 0..15")


@dataclass(frozen=True)
class C64Screen:
    columns: int
    rows: int
    cells: tuple[PetsciiCell, ...]

    def __post_init__(self):
        if self.columns <= 0 or self.rows <= 0:
            raise ValueError("screen geometry must be positive")
        if len(self.cells) != self.columns * self.rows:
            raise ValueError("cell count does not match C64 screen geometry")


def export_screen_ram(screen: C64Screen) -> bytes:
    return bytes(cell.screen_code for cell in screen.cells)


def export_color_ram(screen: C64Screen) -> bytes:
    return bytes(cell.color & 0x0f for cell in screen.cells)


def petscii_to_screen_code(value: int) -> int:
    """Convert common PETSCII printable bytes to C64 screen codes.

    This intentionally rejects control codes. Reverse-video state belongs to
    stream interpretation, not to this byte-level mapping helper.
    """
    if not 0 <= value <= 255:
        raise ValueError("PETSCII value must be a byte")
    if 0x20 <= value <= 0x3f:
        return value
    if 0x40 <= value <= 0x5f:
        return value - 0x40
    if 0x60 <= value <= 0x7f:
        return value - 0x20
    if 0xa0 <= value <= 0xbf:
        return value - 0x40
    if 0xc0 <= value <= 0xdf:
        return value - 0x80
    raise ValueError("PETSCII control/unsupported byte has no direct screen-code mapping")


def screen_code_to_petscii(value: int) -> int:
    """Canonical printable PETSCII representation for a C64 screen code."""
    if not 0 <= value <= 255:
        raise ValueError("screen code must be a byte")
    base = value & 0x7f
    if 0x00 <= base <= 0x1f:
        return base + 0x40
    if 0x20 <= base <= 0x3f:
        return base
    if 0x40 <= base <= 0x5f:
        return base + 0x20
    if 0x60 <= base <= 0x7f:
        return base + 0x40
    raise ValueError("unsupported screen code")


# Common C64 PETSCII control bytes used by the M0.7 stream interpreter.
_COLOR_CODES = {
    0x90: 0,   # black
    0x05: 1,   # white
    0x1c: 2,   # red
    0x9f: 3,   # cyan
    0x9c: 4,   # purple
    0x1e: 5,   # green
    0x1f: 6,   # blue
    0x9e: 7,   # yellow
    0x81: 8,   # orange
    0x95: 9,   # brown
    0x96: 10,  # light red
    0x97: 11,  # dark gray
    0x98: 12,  # gray
    0x99: 13,  # light green
    0x9a: 14,  # light blue
    0x9b: 15,  # light gray
}


def interpret_petscii(data: bytes, columns: int = 40, rows: int = 25) -> C64Screen:
    cells = [PetsciiCell(0x20, 14) for _ in range(columns * rows)]
    x = y = 0
    color = 14
    reverse = False

    def put(screen_code: int):
        nonlocal x, y
        if 0 <= x < columns and 0 <= y < rows:
            if reverse:
                screen_code |= 0x80
            cells[y * columns + x] = PetsciiCell(screen_code, color)
        x += 1
        if x >= columns:
            x = 0
            y = min(rows - 1, y + 1)

    for value in data:
        if value in _COLOR_CODES:
            color = _COLOR_CODES[value]
        elif value == 0x12:  # reverse on
            reverse = True
        elif value == 0x92:  # reverse off
            reverse = False
        elif value == 0x0d:  # carriage return / next line
            x = 0
            y = min(rows - 1, y + 1)
        elif value == 0x93:  # clear/home
            cells = [PetsciiCell(0x20, color) for _ in range(columns * rows)]
            x = y = 0
        elif value == 0x13:  # home
            x = y = 0
        else:
            try:
                put(petscii_to_screen_code(value))
            except ValueError as exc:
                raise ValueError(f"unsupported PETSCII control byte: 0x{value:02x}") from exc
    return C64Screen(columns, rows, tuple(cells))
