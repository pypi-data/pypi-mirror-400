from dataclasses import dataclass

from zonevu.datamodels.DataModel import DataModel


@dataclass
class SurveyModPoint(DataModel):
    latitude: float = -1
    longitude: float = -1
    elevation: float = -1
    azimuth: float = -1
    MD: float = -1
    VX: float = -1
    TVD: float = -1


