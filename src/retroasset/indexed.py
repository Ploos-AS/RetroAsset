from dataclasses import dataclass


@dataclass(frozen=True)
class IndexedBitmap:
    width: int
    height: int
    pixels: tuple[int, ...]
    palette: tuple[tuple[int, int, int], ...]

    def __post_init__(self):
        if self.width <= 0 or self.height <= 0:
            raise ValueError("bitmap dimensions must be positive")
        if len(self.pixels) != self.width * self.height:
            raise ValueError("pixel count does not match bitmap dimensions")
        if not self.palette:
            raise ValueError("palette must not be empty")
        if any(p < 0 or p >= len(self.palette) for p in self.pixels):
            raise ValueError("pixel index outside palette")
        for rgb in self.palette:
            if len(rgb) != 3 or any(c < 0 or c > 255 for c in rgb):
                raise ValueError("palette entries must be RGB bytes")

    @property
    def planes(self) -> int:
        return max(1, (len(self.palette) - 1).bit_length())
