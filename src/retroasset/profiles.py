from dataclasses import dataclass


@dataclass(frozen=True)
class TargetProfile:
    id: str
    family: str
    platform: str
    max_colors: int | None = None
    default_width: int | None = None
    default_height: int | None = None
    columns: int | None = None
    rows: int | None = None
    charset: str | None = None


PROFILES = {
    "amiga-ocs": TargetProfile("amiga-ocs", "raster", "Amiga OCS", 32, 320, 256),
    "amiga-ecs": TargetProfile("amiga-ecs", "raster", "Amiga ECS", 32, 320, 256),
    "amiga-aga": TargetProfile("amiga-aga", "raster", "Amiga AGA", 256, 320, 256),
    "c64-screen": TargetProfile(
        "c64-screen", "character", "Commodore 64 Screen", 16,
        columns=40, rows=25, charset="c64-screen-code"
    ),
    "c64-petscii": TargetProfile(
        "c64-petscii", "character", "Commodore 64 PETSCII", 16,
        columns=40, rows=25, charset="petscii"
    ),
    "ansi-cp437": TargetProfile(
        "ansi-cp437", "character", "IBM PC ANSI", 16,
        columns=80, rows=25, charset="cp437"
    ),
}


def get_profile(profile_id: str) -> TargetProfile:
    try:
        return PROFILES[profile_id]
    except KeyError as exc:
        raise ValueError(f"unknown target: {profile_id}") from exc
