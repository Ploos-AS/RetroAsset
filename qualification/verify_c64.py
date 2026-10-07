from pathlib import Path
import sys


def check(name: str, actual: Path, expected: Path) -> bool:
    a = actual.read_bytes()
    e = expected.read_bytes()
    if a == e:
        print(f"{name}: PASS ({len(a)} bytes)")
        return True
    first = next((i for i, pair in enumerate(zip(a, e)) if pair[0] != pair[1]), None)
    if first is None and len(a) != len(e):
        first = min(len(a), len(e))
    print(f"{name}: FAIL first_difference={first} actual={len(a)} expected={len(e)}")
    return False


def main() -> int:
    root = Path("qualification/generated")
    ok = check("screen RAM", root / "screen-dump.bin", root / "expected-screen.bin")
    ok &= check("color RAM", root / "color-dump.bin", root / "expected-color.bin")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
