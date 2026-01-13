from ...datamodels.DataModel import DataModel as DataModel
from ...datamodels.wells.Station import Station as Station
from _typeshed import Incomplete
from dataclasses import dataclass, field
from dataclasses_json import config
from strenum import StrEnum
from typing import Protocol

class DeviationSurveyUsageEnum(StrEnum):
    Plan = 'Plan'
    Actual = 'Actual'

class AzimuthReferenceEnum(StrEnum):
    Unknown = 'Unknown'
    TrueNorth = 'TrueNorth'
    MagneticNorth = 'MagneticNorth'
    GridNorth = 'GridNorth'

@dataclass
class Survey(DataModel):
    description: str | None = ...
    azimuth_reference: AzimuthReferenceEnum | None = ...
    azimuth_offset: float | None = ...
    usage: DeviationSurveyUsageEnum | None = ...
    is_default: bool | None = ...
    stations: list[Station] = field(default_factory=list[Station])
    landing_md: float | None = field(default=None, metadata=config(field_name='LandingMD'))
    def copy_ids_from(self, source: DataModel): ...
    @property
    def valid_stations(self) -> list[Station]: ...
    def compute_landing_md(self) -> float | None: ...
    def find_md(self, tvd: float, extrapolate: bool = False) -> float | None: ...
    def find_tvd(self, md: float) -> float | None: ...

class InclAzi(Protocol):
    inclination: float | None
    azimuth: float | None

class InclAziImpl:
    inclination: Incomplete
    azimuth: Incomplete
    def __init__(self, inclination: float | None, azimuth: float | None) -> None: ...
