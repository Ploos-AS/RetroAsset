from pathlib import Path


def emit(name: str, data: bytes) -> str:
    rows = []
    for offset in range(0, len(data), 12):
        chunk = ", ".join(f"0x{b:02x}" for b in data[offset:offset + 12])
        rows.append("    " + chunk)
    return (
        f"static const unsigned char {name}[] = {{\n"
        + ",\n".join(rows)
        + "\n};\n"
        + f"static const unsigned long {name}_len = sizeof({name});\n"
    )


def main() -> None:
    root = Path("qualification/generated")
    out = Path("qualification/amiga/generated_fixtures.h")
    pairs = [
        ("fixture_uncompressed", root / "amiga-uncompressed.ilbm"),
        ("fixture_byterun1", root / "amiga-byterun1.ilbm"),
    ]
    text = "#ifndef RETROASSET_GENERATED_FIXTURES_H\n#define RETROASSET_GENERATED_FIXTURES_H\n\n"
    for name, path in pairs:
        text += emit(name, path.read_bytes()) + "\n"
    text += "#endif\n"
    out.write_text(text, encoding="ascii")


if __name__ == "__main__":
    main()
