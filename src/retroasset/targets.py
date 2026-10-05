from dataclasses import dataclass
from .model import AssetManifest


@dataclass(frozen=True)
class ValidationResult:
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.errors


def validate_amiga_ocs(asset: AssetManifest) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    if asset.width is not None and asset.width <= 0:
        errors.append("width must be positive")
    if asset.height is not None and asset.height <= 0:
        errors.append("height must be positive")
    if asset.colors is not None:
        if asset.colors <= 0:
            errors.append("colors must be positive")
        elif asset.colors > 32:
            errors.append("amiga-ocs baseline supports at most 32 indexed colors")
        elif asset.colors not in (2, 4, 8, 16, 32):
            warnings.append("color count does not map exactly to a full OCS bitplane set")

    return ValidationResult(tuple(errors), tuple(warnings))


VALIDATORS = {
    "amiga-ocs": validate_amiga_ocs,
}


def validate(asset: AssetManifest) -> ValidationResult:
    try:
        validator = VALIDATORS[asset.target]
    except KeyError as exc:
        raise ValueError(f"unknown target: {asset.target}") from exc
    return validator(asset)
