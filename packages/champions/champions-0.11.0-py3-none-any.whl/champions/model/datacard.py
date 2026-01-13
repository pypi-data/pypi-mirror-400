from enum import StrEnum
import logging
from typing import Literal
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class FeatureType(StrEnum):
    CATEGORIAL = "categorial"
    NUMERICAL = "numerical"


class Feature(BaseModel):
    name: str
    statistical: FeatureType
    type: str


class Target(BaseModel):
    feature_name: str
    values: list[int | str]


class DataCard(BaseModel):
    features: list[Feature]
    infos: dict
    target: Target
    test_files: list[str]
    train_files: list[str]

    @property
    def feature_names_sql_save(self) -> list[str]:
        return [f'"{feat.name}"' for feat in self.features]

    @property
    def feature_names(self) -> list[str]:
        return [feat.name for feat in self.features]

    @property
    def train_features(self) -> list[Feature]:
        return [feat for feat in self.features if feat.name != self.target.feature_name]
