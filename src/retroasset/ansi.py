from .character import CharacterAsset, CharacterCell


ESC = b"\x1b["


def _sgr(cell: CharacterCell) -> bytes:
    fg = cell.foreground
    bg = cell.background
    if not 0 <= fg <= 15 or not 0 <= bg <= 7:
        raise ValueError("ANSI colors out of DOS range")
    codes = ["0"]
    if fg >= 8:
        codes.append("1")
        fg -= 8
    codes.append(str(30 + fg))
    codes.append(str(40 + bg))
    if cell.blink:
        codes.append("5")
    return ESC + ";".join(codes).encode("ascii") + b"m"


def encode_ans(asset: CharacterAsset) -> bytes:
    if len(asset.cells) != asset.expected_cells():
        raise ValueError("cell count does not match character geometry")
    out = bytearray()
    current = None
    for y in range(asset.rows):
        for x in range(asset.columns):
            cell = asset.cells[y * asset.columns + x]
            style = (cell.foreground, cell.background, cell.blink)
            if style != current:
                out.extend(_sgr(cell))
                current = style
            if not 0 <= cell.codepoint <= 255:
                raise ValueError("CP437 cell must contain a byte value")
            out.append(cell.codepoint)
        if y != asset.rows - 1:
            out.extend(b"\r\n")
    out.extend(ESC + b"0m")
    return bytes(out)
