import argparse
import json
from pathlib import Path

from .model import AssetManifest
from .profiles import PROFILES
from .targets import validate


def _load_manifest(path: Path) -> AssetManifest:
    data = json.loads(path.read_text(encoding="utf-8"))
    return AssetManifest(**data)


def main() -> int:
    parser = argparse.ArgumentParser(prog="retroasset")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("targets", help="list available targets")
    show = sub.add_parser("profile", help="show a target profile")
    show.add_argument("target")
    check = sub.add_parser("validate", help="validate an asset manifest")
    check.add_argument("manifest", type=Path)

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
