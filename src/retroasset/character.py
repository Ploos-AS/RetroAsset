from dataclasses import dataclass


@dataclass(frozen=True)
class CharacterCell:
    codepoint: int
    foreground: int = 7
    background: int = 0
    blink: bool = False


@dataclass(frozen=True)
class CharacterAsset:
    columns: int
    rows: int
    cells: tuple[CharacterCell, ...]

    def expected_cells(self) -> int:
        return self.columns * self.rows
