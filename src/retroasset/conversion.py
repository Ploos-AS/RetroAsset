from dataclasses import dataclass


@dataclass(frozen=True)
class ConversionReport:
    source: str
    target: str
    lossy: bool = False
    losses: tuple[str, ...] = ()

    def as_dict(self) -> dict:
        return {
            "source": self.source,
            "target": self.target,
            "lossy": self.lossy,
            "losses": list(self.losses),
        }


def native_report(source: str, target: str) -> ConversionReport:
    return ConversionReport(source, target)
