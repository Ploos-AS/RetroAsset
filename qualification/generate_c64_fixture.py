from pathlib import Path

from retroasset.c64prg import export_viewer_prg
from retroasset.petscii import C64Screen, PetsciiCell, export_color_ram, export_screen_ram


def main() -> None:
    out = Path("qualification/generated")
    out.mkdir(parents=True, exist_ok=True)
    cells = tuple(
        PetsciiCell((i % 64), (i // 40) % 16)
        for i in range(1000)
    )
    screen = C64Screen(40, 25, cells)
    (out / "fixture.prg").write_bytes(export_viewer_prg(screen))
    (out / "expected-screen.bin").write_bytes(export_screen_ram(screen))
    (out / "expected-color.bin").write_bytes(export_color_ram(screen))


if __name__ == "__main__":
    main()
