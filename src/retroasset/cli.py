import argparse
import json
from pathlib import Path

from .amiga import encode_ilbm, encode_ilbm_compressed
from .ansi import decode_ans, encode_ans
from .character import CharacterAsset, CharacterCell
from .exporters import export_asm, export_c, export_raw_planar
from .indexed import IndexedBitmap
from .model import AssetManifest
from .profiles import PROFILES
from .sauce import Sauce, decode_sauce, encode_sauce
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
    export.add_argument("--compression", choices=("none", "byterun1"), default="none",
                        help="ILBM BODY compression (default: none)")
    export.add_argument("-o", "--output", type=Path, required=True)

    char_import = sub.add_parser("char-import", help="import a native character-art asset")
    char_import.add_argument("source", type=Path)
    char_import.add_argument("--target", required=True, choices=("ansi-cp437",))
    char_import.add_argument("--columns", type=int)
    char_import.add_argument("--rows", type=int)
    char_import.add_argument("-o", "--output", type=Path, required=True)

    char_export = sub.add_parser("char-export", help="export a native character-art asset")
    char_export.add_argument("source", type=Path)
    char_export.add_argument("--target", required=True, choices=("ansi-cp437",))
    char_export.add_argument("-o", "--output", type=Path, required=True)

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

    if args.command == "char-import":
        payload, sauce = decode_sauce(args.source.read_bytes())
        columns = args.columns or (sauce.tinfo1 if sauce else 0)
        rows = args.rows or (sauce.tinfo2 if sauce else 0)
        if not columns or not rows:
            print("error: character geometry requires --columns/--rows or SAUCE dimensions")
            return 2
        asset = decode_ans(payload, columns, rows)
        data = {
            "columns": asset.columns,
            "rows": asset.rows,
            "cells": [
                {
                    "codepoint": cell.codepoint,
                    "foreground": cell.foreground,
                    "background": cell.background,
                    "blink": cell.blink,
                }
                for cell in asset.cells
            ],
        }
        if sauce is not None:
            data["sauce"] = {
                "title": sauce.title,
                "author": sauce.author,
                "group": sauce.group,
                "date": sauce.date,
                "data_type": sauce.data_type,
                "file_type": sauce.file_type,
                "tinfo1": sauce.tinfo1,
                "tinfo2": sauce.tinfo2,
            }
        args.output.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print(f"WROTE {args.output}")
        return 0

    if args.command == "char-export":
        data = json.loads(args.source.read_text(encoding="utf-8"))
        asset = CharacterAsset(
            columns=data["columns"],
            rows=data["rows"],
            cells=tuple(CharacterCell(**cell) for cell in data["cells"]),
        )
        payload = encode_ans(asset)
        if "sauce" in data:
            meta = Sauce(**data["sauce"])
            payload += encode_sauce(meta, len(payload))
        args.output.write_bytes(payload)
        print(f"WROTE {args.output}")
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
        if args.compression != "none" and args.format != "ilbm":
            print("error: --compression applies only to ILBM export")
            return 2
        if args.format == "ilbm":
            encoder = encode_ilbm_compressed if args.compression == "byterun1" else encode_ilbm
            args.output.write_bytes(encoder(bitmap))
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
