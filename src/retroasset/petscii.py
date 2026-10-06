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
