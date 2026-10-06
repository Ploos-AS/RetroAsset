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
