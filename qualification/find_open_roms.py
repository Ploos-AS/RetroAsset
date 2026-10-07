from pathlib import Path
import sys


def choose(root: Path, patterns: tuple[str, ...]) -> Path:
    matches = []
    for pattern in patterns:
        matches.extend(root.glob(pattern))
    matches = sorted({p.resolve() for p in matches if p.is_file()})
    if not matches:
        raise SystemExit(f"no ROM matched {patterns}")
    return matches[0]


def main() -> None:
    root = Path(sys.argv[1])
    output = Path(sys.argv[2])
    basic = choose(root, ("*basic*.rom", "*BASIC*.rom"))
    kernal = choose(root, ("*kernal*.rom", "*KERNAL*.rom"))
    chargen = choose(root, ("*chargen*.rom", "*CHARGEN*.rom", "*pxl*.rom", "*PXL*.rom"))
    output.write_text(
        f"RETROASSET_BASIC_ROM={basic}\n"
        f"RETROASSET_KERNAL_ROM={kernal}\n"
        f"RETROASSET_CHARGEN_ROM={chargen}\n"
    )


if __name__ == "__main__":
    main()
