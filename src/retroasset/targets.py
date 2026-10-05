from .model import AssetManifest
from .profiles import PROFILES, TargetProfile, get_profile


class ValidationResult:
    def __init__(self, errors=(), warnings=()):
        self.errors = tuple(errors)
        self.warnings = tuple(warnings)

    @property
    def ok(self) -> bool:
        return not self.errors


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
            errors.append(
                f"{profile.id} supports at most {profile.max_colors} colors"
            )

    if profile.family == "raster" and asset.colors is not None:
        if profile.id in ("amiga-ocs", "amiga-ecs") and asset.colors not in (2, 4, 8, 16, 32):
            warnings.append("color count does not map exactly to a full OCS/ECS bitplane set")

    if profile.family == "character":
        if asset.width is not None and profile.columns is not None and asset.width != profile.columns:
            warnings.append(f"profile default geometry is {profile.columns} columns")
        if asset.height is not None and profile.rows is not None and asset.height != profile.rows:
            warnings.append(f"profile default geometry is {profile.rows} rows")

    return ValidationResult(errors, warnings)


def validate(asset: AssetManifest) -> ValidationResult:
    return _validate_common(asset, get_profile(asset.target))


VALIDATORS = {profile_id: validate for profile_id in PROFILES}
