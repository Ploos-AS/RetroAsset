from .model import AssetManifest
from .profiles import PROFILES, TargetProfile, get_profile


class ValidationResult:
    def __init__(self, errors=(), warnings=(), memory_bytes=None):
        self.errors = tuple(errors)
        self.warnings = tuple(warnings)
        self.memory_bytes = memory_bytes

    @property
    def ok(self) -> bool:
        return not self.errors

    @property
    def export_ready(self) -> bool:
        return self.ok


def _amiga_memory_bytes(asset: AssetManifest) -> int | None:
    if asset.width is None or asset.height is None or asset.colors is None or asset.colors <= 0:
        return None
    planes = max(1, (asset.colors - 1).bit_length())
    row_bytes = ((asset.width + 15) // 16) * 2
    return row_bytes * asset.height * planes


def _validate_common(asset: AssetManifest, profile: TargetProfile) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    if asset.width is not None and asset.width <= 0:
        errors.append("width must be positive")
    if asset.height is not None and asset.height <= 0:
        errors.append("height must be positive")
    if asset.colors is not None:
        if asset.colors <= 0:
            errors.append("colors must be positive")
        elif profile.max_colors is not None and asset.colors > profile.max_colors:
            errors.append(f"{profile.id} supports at most {profile.max_colors} colors")

    if profile.family == "raster" and asset.colors is not None:
        if profile.id in ("amiga-ocs", "amiga-ecs") and asset.colors not in (2, 4, 8, 16, 32):
            warnings.append("color count does not map exactly to a full OCS/ECS bitplane set")

    if profile.family == "character":
        if asset.width is not None and profile.columns is not None and asset.width != profile.columns:
            warnings.append(f"profile default geometry is {profile.columns} columns")
        if asset.height is not None and profile.rows is not None and asset.height != profile.rows:
            warnings.append(f"profile default geometry is {profile.rows} rows")

    return ValidationResult(errors, warnings)


def _validate_amiga(asset: AssetManifest, profile: TargetProfile) -> ValidationResult:
    base = _validate_common(asset, profile)
    errors = list(base.errors)
    warnings = list(base.warnings)

    if asset.kind not in ("bitmap", "sprite", "bob", "tile", "tileset"):
        errors.append("Amiga asset kind must be bitmap, sprite, bob, tile, or tileset")

    if asset.width is None or asset.height is None or asset.colors is None:
        errors.append("Amiga export readiness requires width, height, and colors")

    metadata = asset.metadata
    if asset.kind in ("sprite", "bob"):
        if "hotspot" not in metadata:
            warnings.append(f"{asset.kind} metadata has no hotspot")
        elif not (isinstance(metadata["hotspot"], (list, tuple)) and len(metadata["hotspot"]) == 2):
            errors.append("hotspot must be a two-element [x, y] pair")

    if asset.kind in ("tile", "tileset"):
        tile = metadata.get("tile_size")
        if tile is None:
            errors.append("tile/tileset export readiness requires metadata.tile_size")
        elif not (isinstance(tile, (list, tuple)) and len(tile) == 2 and
                  all(isinstance(v, int) and v > 0 for v in tile)):
            errors.append("metadata.tile_size must be a positive [width, height] pair")
        elif asset.width and asset.height and (asset.width % tile[0] or asset.height % tile[1]):
            errors.append("asset dimensions must be divisible by metadata.tile_size")

    memory_bytes = _amiga_memory_bytes(asset)
    return ValidationResult(errors, warnings, memory_bytes)


def validate(asset: AssetManifest) -> ValidationResult:
    profile = get_profile(asset.target)
    if profile.id.startswith("amiga-"):
        return _validate_amiga(asset, profile)
    return _validate_common(asset, profile)


VALIDATORS = {profile_id: validate for profile_id in PROFILES}
