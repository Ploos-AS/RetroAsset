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


def decode_ans(data: bytes, columns: int, rows: int) -> CharacterAsset:
    cells = []
    fg, bg, blink = 7, 0, False
    i = 0
    while i < len(data) and len(cells) < columns * rows:
        if data[i:i + 2] == b"\x1b[":
            end = data.find(b"m", i + 2)
            if end < 0:
                raise ValueError("unterminated ANSI SGR sequence")
            raw = data[i + 2:end]
            codes = [int(x) for x in raw.split(b";") if x] or [0]
            bright = False
            for code in codes:
                if code == 0:
                    fg, bg, blink, bright = 7, 0, False, False
                elif code == 1:
                    bright = True
                elif code == 5:
                    blink = True
                elif 30 <= code <= 37:
                    fg = code - 30 + (8 if bright else 0)
                elif 40 <= code <= 47:
                    bg = code - 40
            i = end + 1
            continue
        if data[i:i + 2] == b"\r\n":
            # Writer emits CR/LF only at exact row boundaries.
            if len(cells) % columns:
                raise ValueError("unexpected CR/LF before end of ANSI row")
            i += 2
            continue
        cells.append(CharacterCell(data[i], fg, bg, blink))
        i += 1
    if len(cells) != columns * rows:
        raise ValueError("ANSI data does not fill requested geometry")
    return CharacterAsset(columns, rows, tuple(cells))
