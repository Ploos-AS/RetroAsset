import argparse
import json
from pathlib import Path

from .amiga import encode_ilbm
from .exporters import export_asm, export_c, export_raw_planar
from .indexed import IndexedBitmap
from .model import AssetManifest
from .profiles import PROFILES
from .targets import validate


def _load_manifest(path: Path) -> AssetManifest:
    data = json.loads(path.read_text(encoding="utf-8"))
    return AssetManifest(**data)


def _load_indexed(path: Path) -> IndexedBitmap:
    data = json.loads(path.read_text(encoding="utf-8"))
    return IndexedBitmap(
        width=data["width"],
        height=data["height"],
        pixels=tuple(data["pixels"]),
        palette=tuple(tuple(rgb) for rgb in data["palette"]),
    )


def main() -> int:
    parser = argparse.ArgumentParser(prog="retroasset")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("targets", help="list available targets")
    show = sub.add_parser("profile", help="show a target profile")
    show.add_argument("target")
    check = sub.add_parser("validate", help="validate an asset manifest")
    check.add_argument("manifest", type=Path)

    export = sub.add_parser("export", help="export a native retro asset")
    export.add_argument("source", type=Path)
    export.add_argument("--target", required=True, choices=sorted(PROFILES))
    export.add_argument("--format", required=True, choices=("ilbm", "raw", "c", "asm"))
    export.add_argument("--symbol", default="asset")
    export.add_argument("-o", "--output", type=Path, required=True)

    args = parser.parse_args()

    if args.command == "targets":
        for target, profile in sorted(PROFILES.items()):
            print(f"{target}\t{profile.family}\t{profile.platform}")
        return 0

    if args.command == "profile":
        try:
            profile = PROFILES[args.target]
        except KeyError:
            print(f"error: unknown target: {args.target}")
            return 2
        print(json.dumps(profile.__dict__, indent=2))
        return 0

    if args.command == "export":
        if not args.target.startswith("amiga-"):
            print("error: M0.3 native exporters currently require an Amiga target")
            return 2
        bitmap = _load_indexed(args.source)
        profile = PROFILES[args.target]
        if profile.max_colors is not None and len(bitmap.palette) > profile.max_colors:
            print(f"error: {args.target} supports at most {profile.max_colors} colors")
            return 1
        if args.format == "ilbm":
            args.output.write_bytes(encode_ilbm(bitmap))
        elif args.format == "raw":
            args.output.write_bytes(export_raw_planar(bitmap))
        elif args.format == "c":
            args.output.write_text(export_c(bitmap, args.symbol), encoding="utf-8")
        elif args.format == "asm":
            args.output.write_text(export_asm(bitmap, args.symbol), encoding="utf-8")
        print(f"WROTE {args.output}")
        return 0

    asset = _load_manifest(args.manifest)
    result = validate(asset)
    for warning in result.warnings:
        print(f"warning: {warning}")
    for error in result.errors:
        print(f"error: {error}")
    print("PASS" if result.ok else "FAIL")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
