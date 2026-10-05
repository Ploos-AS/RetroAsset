from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AssetManifest:
    name: str
    target: str
    kind: str
    width: int | None = None
    height: int | None = None
    colors: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
