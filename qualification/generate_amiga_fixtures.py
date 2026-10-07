from pathlib import Path

from retroasset.amiga import encode_ilbm, encode_ilbm_compressed
from retroasset.indexed import IndexedBitmap


def main() -> None:
    out = Path("qualification/generated")
    out.mkdir(parents=True, exist_ok=True)
    bitmap = IndexedBitmap(
        16, 2,
        tuple([0, 1] * 8 + [1, 0] * 8),
        ((0, 0, 0), (255, 255, 255)),
    )
    (out / "amiga-uncompressed.ilbm").write_bytes(encode_ilbm(bitmap))
    (out / "amiga-byterun1.ilbm").write_bytes(encode_ilbm_compressed(bitmap))


if __name__ == "__main__":
    main()
