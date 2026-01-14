#
#  Copyright 2026 by Dmitry Berezovsky, MIT License
#
__all__ = ["QuotaFeature", "FeatureSet", "FEATURES", "FeatureId"]
import dataclasses


@dataclasses.dataclass(frozen=True, kw_only=True)
class QuotaFeature:
    namespace: str
    name: str
    verbose_name: str

    @property
    def full_name(self) -> str:
        return f"{self.namespace}.{self.name}" if self.namespace else self.name

    @property
    def id(self) -> str:
        return self.full_name

    def __str__(self) -> str:
        return self.full_name

    def __repr__(self) -> str:
        return f"QuotaFeature(full_name={self.full_name!r}, verbose_name={self.verbose_name!r})"


FeatureId = str | QuotaFeature


class FeatureSet:
    def __init__(self) -> None:
        self._features: dict[str, QuotaFeature] = {}

    def register(self, *feature: QuotaFeature) -> None:
        for f in feature:
            self._features[f.id] = f

    def get(self, feature_id: str) -> QuotaFeature | None:
        return self._features.get(feature_id)

    def all(self) -> list[QuotaFeature]:
        return list(self._features.values())


FEATURES = FeatureSet()
